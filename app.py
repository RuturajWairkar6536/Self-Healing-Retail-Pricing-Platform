from flask import Flask, request, jsonify
import pickle
import pandas as pd
import numpy as np
import os
import logging
import subprocess
import threading
import sys

# =========================
# Logging
# =========================
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

app = Flask(__name__)

# =========================
# Load Model
# =========================
MODEL_PATH = "pricing_model.pkl"

def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

model = load_model()
logger.info("Model loaded successfully.")

# =========================
# Core Functions
# =========================
def predict_demand(price, day_of_week, month):
    """Predict demand for a given price, day, and month."""
    features = pd.DataFrame({
        "Price": [price],
        "day_of_week": [day_of_week],
        "month": [month]
    })
    demand = model.predict(features)[0]
    return max(float(demand), 0.0)


def optimize_price(current_price, day_of_week, month, price_range_pct=0.2, steps=25):
    """
    Scan a price range (+/- price_range_pct of current price) and find
    the price that maximises revenue = price * predicted_demand.
    """
    best_price   = current_price
    best_revenue = 0.0
    best_demand  = 0.0

    low  = current_price * (1 - price_range_pct)
    high = current_price * (1 + price_range_pct)

    for price in np.linspace(low, high, steps):
        demand  = predict_demand(price, day_of_week, month)
        revenue = price * demand
        if revenue > best_revenue:
            best_revenue = revenue
            best_price   = price
            best_demand  = demand

    return best_price, best_demand, best_revenue


def compare_prices(current_price, best_price, current_revenue, best_revenue, competitor_price=None):
    """
    A/B comparison logic:
      - If optimised revenue improves by > 5%  → Apply Optimised Price
      - If competitor is undercutting us        → Consider Competitive Pricing
      - Otherwise                               → Keep Current Price
    """
    improvement = ((best_revenue - current_revenue) / current_revenue * 100) if current_revenue else 0.0

    if improvement > 5:
        decision = "Apply Optimized Price"
    elif competitor_price and best_price > competitor_price * 1.1:
        decision = "Consider Competitive Pricing (Competitor is cheaper)"
    else:
        decision = "Keep Current Price"

    return improvement, decision


# =========================
# API Endpoints
# =========================

@app.route("/health", methods=["GET"])
def health():
    """Health-check endpoint — used by Jenkins / load-balancer."""
    model_exists = os.path.exists(MODEL_PATH)
    return jsonify({
        "status": "ok",
        "model_loaded": model_exists,
        "model_path": MODEL_PATH
    }), 200


@app.route("/optimize", methods=["POST"])
def optimize():
    """
    Price optimisation endpoint.

    Request JSON:
        price            (float, required)  — current selling price
        day              (int,   required)  — day of week (0=Mon, 6=Sun)
        month            (int,   required)  — month (1–12)
        stock            (int,   optional)  — current stock level (informational)
        competitor_price (float, optional)  — competitor's price for A/B decision
    """
    try:
        data = request.get_json(force=True)

        # --- Required fields ---
        price = float(data["price"])
        day   = int(data["day"])
        month = int(data["month"])

        if not (1 <= price):
            return jsonify({"error": "price must be >= 1"}), 400
        if not (0 <= day <= 6):
            return jsonify({"error": "day must be 0–6"}), 400
        if not (1 <= month <= 12):
            return jsonify({"error": "month must be 1–12"}), 400

        # --- Optional fields ---
        stock            = int(data.get("stock", -1))          # -1 = not provided
        competitor_price = data.get("competitor_price", None)
        if competitor_price is not None:
            competitor_price = float(competitor_price)
        product_code = str(data.get("product_code", "")).strip()

        # --- Predictions ---
        current_demand  = predict_demand(price, day, month)
        current_revenue = price * current_demand

        best_price, best_demand, best_revenue = optimize_price(price, day, month)

        improvement, decision = compare_prices(
            price, best_price, current_revenue, best_revenue, competitor_price
        )

        response = {
            "product_code":     product_code if product_code else "N/A",
            "current_price":    round(price, 2),
            "current_demand":   round(current_demand, 2),
            "current_revenue":  round(current_revenue, 2),
            "best_price":       round(best_price, 2),
            "best_demand":      round(best_demand, 2),
            "best_revenue":     round(best_revenue, 2),
            "improvement_%":    round(improvement, 2),
            "decision":         decision,
        }

        # Include stock & competitor info if provided
        if stock >= 0:
            response["stock"] = stock
        if competitor_price is not None:
            response["competitor_price"] = round(competitor_price, 2)

        logger.info(f"/optimize | price={price} day={day} month={month} → {decision}")
        return jsonify(response), 200

    except KeyError as e:
        return jsonify({"error": f"Missing required field: {e}"}), 400
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid input: {e}"}), 400
    except Exception as e:
        logger.error(f"Unexpected error in /optimize: {e}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/reload_model", methods=["POST"])
def reload_model():
    """
    Hot-reload the model from disk (called after retraining without restart).
    Protected by a simple token — set RELOAD_TOKEN env var.
    """
    global model
    token = request.headers.get("X-Reload-Token", "")
    expected = os.environ.get("RELOAD_TOKEN", "")

    if expected and token != expected:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        model = load_model()
        logger.info("Model hot-reloaded successfully via /reload_model")
        return jsonify({"status": "model reloaded"}), 200
    except Exception as e:
        logger.error(f"Hot-reload failed: {e}")
        return jsonify({"error": str(e)}), 500


# =========================
# Retraining Trigger
# =========================

# Shared state so we can report status
_retrain_state = {"running": False, "last_status": None, "last_log": ""}


def _run_retrain_background(new_data: str):
    """Run retrain.py in a subprocess — called in a background thread."""
    global _retrain_state
    _retrain_state["running"] = True
    _retrain_state["last_status"] = None
    _retrain_state["last_log"] = ""

    try:
        cmd = [sys.executable, "retrain.py", "--new_data", new_data]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        _retrain_state["last_log"] = proc.stdout + proc.stderr
        _retrain_state["last_status"] = "success" if proc.returncode == 0 else "failed"
        logger.info(f"Retrain subprocess finished with code {proc.returncode}")

        # Hot-reload the model so Flask serves the updated version immediately
        if proc.returncode == 0:
            global model
            model = load_model()
            logger.info("Model hot-reloaded after retraining.")

    except subprocess.TimeoutExpired:
        _retrain_state["last_status"] = "timeout"
        _retrain_state["last_log"] = "Retraining timed out after 600s."
        logger.error("Retrain subprocess timed out.")
    except Exception as e:
        _retrain_state["last_status"] = "error"
        _retrain_state["last_log"] = str(e)
        logger.error(f"Retrain subprocess error: {e}")
    finally:
        _retrain_state["running"] = False


@app.route("/trigger_retrain", methods=["POST"])
def trigger_retrain():
    """
    Trigger model retraining in the background.
    Jenkins calls this endpoint after a GitHub push.

    Request JSON (all optional):
        new_data  (str)  — path to new Excel file (default: online_retail_II.xlsx)
        token     (str)  — see RELOAD_TOKEN env var

    Response:
        202  Accepted — retraining started
        409  Conflict — retraining already running
        401  Unauthorized — bad token
    """
    # Token check
    token    = request.headers.get("X-Reload-Token", "")
    expected = os.environ.get("RELOAD_TOKEN", "")
    if expected and token != expected:
        return jsonify({"error": "Unauthorized"}), 401

    if _retrain_state["running"]:
        return jsonify({"status": "already_running",
                        "message": "Retraining is already in progress."}), 409

    data     = request.get_json(silent=True) or {}
    new_data = data.get("new_data", "online_retail_II.xlsx")

    thread = threading.Thread(
        target=_run_retrain_background,
        args=(new_data,),
        daemon=True
    )
    thread.start()

    logger.info(f"/trigger_retrain called — new_data={new_data}")
    return jsonify({
        "status":   "accepted",
        "message":  "Retraining started in background.",
        "new_data": new_data
    }), 202


@app.route("/retrain_status", methods=["GET"])
def retrain_status():
    """Check if retraining is running and what the last result was."""
    return jsonify({
        "running":     _retrain_state["running"],
        "last_status": _retrain_state["last_status"],
        "last_log":    _retrain_state["last_log"][-2000:],  # last 2000 chars
    }), 200


# =========================
# E-Commerce: Products
# =========================

def get_all_products():
    """Load all products from CSV"""
    try:
        df = pd.read_csv("data/products.csv")
        return df.to_dict("records")
    except:
        return []


def get_product_by_id(product_id):
    """Get single product"""
    try:
        df = pd.read_csv("data/products.csv")
        filtered = df[df["product_id"] == product_id]
        if filtered.empty:
            return None
        return filtered.iloc[0].to_dict()
    except:
        return None


@app.route("/products", methods=["GET"])
def list_products():
    """Get all products"""
    try:
        products = get_all_products()
        return jsonify({"products": products, "count": len(products)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/product/<product_id>", methods=["GET"])
def get_product(product_id):
    """Get single product with AI price recommendation"""
    try:
        product = get_product_by_id(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        # Get AI recommendation for current price
        from datetime import datetime
        now = datetime.now()
        rec = optimize_price(
            product["current_price"],
            now.weekday(),
            now.month
        )
        
        product["ai_price"] = round(rec[0], 2)
        product["ai_demand"] = round(rec[1], 2)
        product["ai_revenue"] = round(rec[2], 2)
        
        return jsonify(product), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/categories", methods=["GET"])
def get_categories():
    """Get all unique categories"""
    try:
        df = pd.read_csv("data/products.csv")
        categories = df["category"].unique().tolist()
        return jsonify({"categories": sorted(categories)}), 200
    except:
        return jsonify({"categories": []}), 200


# =========================
# E-Commerce: Cart & Orders
# =========================

def load_cart(session_id="default"):
    """Load cart from JSON"""
    import json
    try:
        with open("data/cart.json", "r") as f:
            data = json.load(f)
        return data.get("carts", {}).get(session_id, {"items": [], "total_items": 0, "total_price": 0.0})
    except:
        return {"items": [], "total_items": 0, "total_price": 0.0}


def save_cart(session_id, cart):
    """Save cart to JSON"""
    import json
    try:
        with open("data/cart.json", "r") as f:
            data = json.load(f)
    except:
        data = {"carts": {}}
    
    if "carts" not in data:
        data["carts"] = {}
    
    data["carts"][session_id] = cart
    
    with open("data/cart.json", "w") as f:
        json.dump(data, f, indent=2)


@app.route("/cart", methods=["GET"])
def get_cart():
    """Get shopping cart"""
    try:
        session_id = request.args.get("session", "default")
        cart = load_cart(session_id)
        return jsonify(cart), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    """Add item to cart"""
    try:
        data = request.get_json(force=True)
        session_id = data.get("session", "default")
        product_id = data.get("product_id")
        quantity = int(data.get("quantity", 1))
        price = float(data.get("price"))
        
        cart = load_cart(session_id)
        
        # Check if product already in cart
        found = False
        for item in cart["items"]:
            if item["product_id"] == product_id:
                item["quantity"] += quantity
                found = True
                break
        
        if not found:
            cart["items"].append({
                "product_id": product_id,
                "quantity": quantity,
                "price": price
            })
        
        # Recalculate totals
        cart["total_items"] = sum(item["quantity"] for item in cart["items"])
        cart["total_price"] = sum(item["quantity"] * item["price"] for item in cart["items"])
        
        save_cart(session_id, cart)
        logger.info(f"Added {product_id} to cart")
        
        return jsonify({"status": "added", "cart": cart}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/cart/remove", methods=["POST"])
def remove_from_cart():
    """Remove item from cart"""
    try:
        data = request.get_json(force=True)
        session_id = data.get("session", "default")
        product_id = data.get("product_id")
        
        cart = load_cart(session_id)
        cart["items"] = [item for item in cart["items"] if item["product_id"] != product_id]
        
        # Recalculate
        cart["total_items"] = sum(item["quantity"] for item in cart["items"])
        cart["total_price"] = sum(item["quantity"] * item["price"] for item in cart["items"])
        
        save_cart(session_id, cart)
        logger.info(f"Removed {product_id} from cart")
        
        return jsonify({"status": "removed", "cart": cart}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/checkout", methods=["POST"])
def checkout():
    """Process checkout and save order"""
    try:
        data = request.get_json(force=True)
        session_id = data.get("session", "default")
        customer_name = data.get("customer_name", "Guest")
        
        cart = load_cart(session_id)
        if not cart["items"]:
            return jsonify({"error": "Cart is empty"}), 400
        
        # Append to orders CSV
        from datetime import datetime
        now = datetime.now()
        
        orders_data = []
        for item in cart["items"]:
            orders_data.append({
                "date": now.strftime("%Y-%m-%d"),
                "product_id": item["product_id"],
                "quantity_sold": item["quantity"],
                "price_at_sale": item["price"],
                "revenue": item["quantity"] * item["price"],
                "day_of_week": now.weekday(),
                "month": now.month
            })
        
        # Save to orders.csv
        orders_df = pd.DataFrame(orders_data)
        try:
            existing = pd.read_csv("data/orders.csv")
            orders_df = pd.concat([existing, orders_df], ignore_index=True)
        except:
            pass
        
        orders_df.to_csv("data/orders.csv", index=False)
        
        # Update product stock
        try:
            products_df = pd.read_csv("data/products.csv")
            for item in cart["items"]:
                products_df.loc[products_df["product_id"] == item["product_id"], "stock"] -= item["quantity"]
            products_df.to_csv("data/products.csv", index=False)
        except:
            pass
        
        # Clear cart
        cart["items"] = []
        cart["total_items"] = 0
        cart["total_price"] = 0.0
        save_cart(session_id, cart)
        
        order_id = f"ORD-{now.strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Order {order_id}: {len(orders_data)} items for ₹{sum([o['revenue'] for o in orders_data]):.2f}")
        
        return jsonify({
            "status": "success",
            "order_id": order_id,
            "total_amount": sum([o["revenue"] for o in orders_data]),
            "items_count": sum([o["quantity_sold"] for o in orders_data])
        }), 200
    except Exception as e:
        logger.error(f"Checkout error: {e}")
        return jsonify({"error": str(e)}), 500


# =========================
# Run
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)