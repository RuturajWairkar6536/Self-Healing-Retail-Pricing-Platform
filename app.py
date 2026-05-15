from datetime import datetime
import json
import logging
import logging.handlers
import os
import pickle
import subprocess
import sys
import threading

from flask import Flask, jsonify, request
import numpy as np
import pandas as pd
from werkzeug.security import check_password_hash, generate_password_hash

#check webhook trigger
# Setup JSON logging for ELK Stack
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'service': 'pricing-api'
        }
        for key in ("method", "path", "status_code", "remote_addr", "duration_ms"):
            if hasattr(record, key):
                log_data[key] = getattr(record, key)
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)

# Configure logging
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# File handler - JSON format for Logstash
file_handler = logging.handlers.RotatingFileHandler(
    os.path.join(log_dir, 'api.log'),
    maxBytes=10485760,  # 10MB
    backupCount=5
)
file_handler.setFormatter(JSONFormatter())
logger.addHandler(file_handler)

# Console handler - readable format
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(console_handler)

app = Flask(__name__)

# =========================
# VAULT SECRET INTEGRATION
# =========================
def get_vault_secret(path, key_name):
    """Retrieves a secret from HashiCorp Vault via API."""
    vault_url = os.environ.get("VAULT_ADDR", "http://vault:8200")
    vault_token = os.environ.get("VAULT_TOKEN", "spe-dev-root")
    
    try:
        url = f"{vault_url}/v1/secret/data/{path}"
        headers = {"X-Vault-Token": vault_token}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data["data"]["data"].get(key_name)
        return None
    except Exception as e:
        logger.warning(f"Vault retrieval failed: {e}. Falling back to env vars.")
        return None

# Example usage for security evaluation
JWT_SECRET = get_vault_secret("spe-platform/config", "JWT_SECRET_KEY") or "fallback-secret"


@app.before_request
def start_request_timer():
    request._start_time = datetime.now()


@app.after_request
def log_request(response):
    started_at = getattr(request, "_start_time", datetime.now())
    duration_ms = round((datetime.now() - started_at).total_seconds() * 1000, 2)
    logger.info(
        "request completed",
        extra={
            "method": request.method,
            "path": request.path,
            "status_code": response.status_code,
            "remote_addr": request.remote_addr,
            "duration_ms": duration_ms,
        },
    )
    return response

MODEL_PATH = "pricing_model.pkl"
DATA_DIR = "data"
PRODUCTS_CSV = os.path.join(DATA_DIR, "products.csv")
INVENTORY_CSV = os.path.join(DATA_DIR, "inventory.csv")
ORDERS_CSV = os.path.join(DATA_DIR, "orders.csv")
SALES_HISTORY_CSV = os.path.join(DATA_DIR, "sales_history.csv")
PRICE_HISTORY_CSV = os.path.join(DATA_DIR, "price_history.csv")
CART_JSON = os.path.join(DATA_DIR, "cart.json")
CONFIG_JSON = os.path.join(DATA_DIR, "config.json")
USERS_JSON = os.path.join(DATA_DIR, "users.json")

ORDER_COLUMNS = [
    "order_id", "order_date", "customer_name", "customer_email", "product_id", "product_name",
    "quantity_sold", "price_at_sale", "revenue", "day_of_week", "month"
]
SALES_COLUMNS = ["StockCode", "date", "day_of_week", "month", "demand", "Price"]
PRICE_HISTORY_COLUMNS = [
    "timestamp", "product_id", "old_price", "new_price", "reason", "decision",
    "predicted_demand", "revenue_gain_pct"
]

PRICE_RANGE_PCT = 0.20
OPTIMIZER_STEPS = 31
MIN_REVENUE_GAIN_TO_APPLY = 5.0
MIN_PRICE_CHANGE_PCT = 1.0
COMPETITOR_MATCH_BAND = 0.10
COMPETITOR_UNDERCUT_PCT = 0.03


def load_model():
    if not os.path.exists(MODEL_PATH):
        logger.warning(f"Model file not found: {MODEL_PATH}. Creating a dummy model for startup.")
        # Create a simple dummy model so the service can start
        from sklearn.linear_model import LinearRegression
        dummy = LinearRegression()
        dummy.coef_ = np.array([0.1, 0.2, 0.3])
        dummy.intercept_ = 10.0
        # Mock the predict method to work with DataFrames
        original_predict = dummy.predict
        def safe_predict(X):
            try: return original_predict(X)
            except: return np.array([10.0])
        dummy.predict = safe_predict
        return dummy
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)


model = load_model()
logger.info("Model loaded successfully.")


def ensure_data_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    defaults = {
        ORDERS_CSV: ORDER_COLUMNS,
        SALES_HISTORY_CSV: SALES_COLUMNS,
        PRICE_HISTORY_CSV: PRICE_HISTORY_COLUMNS,
    }
    for path, columns in defaults.items():
        if not os.path.exists(path):
            pd.DataFrame(columns=columns).to_csv(path, index=False)
    if not os.path.exists(CART_JSON):
        write_json(CART_JSON, {"carts": {}})
    if not os.path.exists(CONFIG_JSON):
        write_json(CONFIG_JSON, {"platform_title": "AI-Powered Smart Ecommerce Pricing Platform"})
    if not os.path.exists(USERS_JSON):
        write_json(USERS_JSON, {"users": []})


def read_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def read_csv(path, columns=None):
    try:
        return pd.read_csv(path)
    except Exception:
        return pd.DataFrame(columns=columns or [])


def write_csv(path, df):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)


def normalize_email(email):
    return str(email or "").strip().lower()


def public_user(user):
    return {
        "user_id": user["user_id"],
        "name": user["name"],
        "email": user["email"],
        "role": user.get("role", "customer"),
    }


ensure_data_files()


def predict_demand(price, day_of_week, month):
    features = pd.DataFrame({
        "Price": [float(price)],
        "day_of_week": [int(day_of_week)],
        "month": [int(month)],
    })
    demand = model.predict(features)[0]
    return max(float(demand), 0.0)


def capped_units(predicted_demand, stock=None):
    if stock is None:
        return float(predicted_demand)
    return min(float(predicted_demand), max(int(stock), 0))


def revenue_for(price, predicted_demand, stock=None):
    return float(price) * capped_units(predicted_demand, stock)


def market_score(price, revenue, competitor_price=None):
    if not competitor_price:
        return float(revenue), 0.0

    competitor_price = float(competitor_price)
    allowed_market_price = competitor_price * (1 + COMPETITOR_MATCH_BAND)
    if price <= allowed_market_price:
        return float(revenue), 0.0

    excess_pct = (float(price) - allowed_market_price) / allowed_market_price
    penalty = float(revenue) * min(excess_pct * 6.0, 1.25)
    return float(revenue) - penalty, penalty


def candidate_price_bounds(current_price, competitor_price=None, price_range_pct=PRICE_RANGE_PCT):
    current_price = float(current_price)
    base_low = max(1.0, current_price * (1 - price_range_pct))
    base_high = current_price * (1 + price_range_pct)

    if not competitor_price:
        return base_low, base_high

    competitor_price = float(competitor_price)
    if competitor_price <= 0:
        return base_low, base_high

    market_low = max(1.0, competitor_price * (1 - COMPETITOR_MATCH_BAND))
    market_high = competitor_price * (1 + COMPETITOR_MATCH_BAND)

    if competitor_price < current_price:
        return market_low, max(market_low, min(base_high, market_high))

    return base_low, min(base_high, market_high)


def build_candidate_prices(low, high, current_price, competitor_price=None, steps=OPTIMIZER_STEPS):
    candidates = list(np.linspace(low, high, steps))
    candidates.append(float(current_price))
    if competitor_price and competitor_price > 0:
        competitor_price = float(competitor_price)
        candidates.extend([
            competitor_price * (1 - COMPETITOR_UNDERCUT_PCT),
            competitor_price,
            competitor_price * (1 + COMPETITOR_MATCH_BAND),
        ])
    return sorted({round(max(1.0, float(price)), 2) for price in candidates})


def optimize_price(current_price, day_of_week, month, stock=None, competitor_price=None,
                   price_range_pct=PRICE_RANGE_PCT, steps=OPTIMIZER_STEPS):
    low, high = candidate_price_bounds(current_price, competitor_price, price_range_pct)
    best = {"price": float(current_price), "demand": 0.0, "sellable_units": 0.0, "revenue": 0.0, "score": 0.0}
    curve = []

    for price in build_candidate_prices(low, high, current_price, competitor_price, steps):
        demand = predict_demand(price, day_of_week, month)
        sellable = capped_units(demand, stock)
        revenue = revenue_for(price, demand, stock)
        score, penalty = market_score(price, revenue, competitor_price)
        point = {
            "price": round(float(price), 2),
            "predicted_demand": round(demand, 2),
            "sellable_units": round(sellable, 2),
            "revenue": round(revenue, 2),
            "market_penalty": round(penalty, 2),
            "score": round(score, 2),
        }
        curve.append(point)
        if score > best["score"]:
            best = {
                "price": float(price),
                "demand": demand,
                "sellable_units": sellable,
                "revenue": revenue,
                "score": score,
            }

    return best, curve, {"min_price": round(low, 2), "max_price": round(high, 2)}


def compare_prices(current_price, best_price, current_revenue, best_revenue, competitor_price=None):
    improvement = ((best_revenue - current_revenue) / current_revenue * 100) if current_revenue else 0.0
    price_change_pct = ((best_price - current_price) / current_price * 100) if current_price else 0.0
    if competitor_price and current_price > competitor_price * (1 + COMPETITOR_MATCH_BAND) and best_price < current_price:
        decision = "Consider Competitive Pricing (Competitor is cheaper)"
    elif competitor_price and best_price > competitor_price * (1 + COMPETITOR_MATCH_BAND):
        decision = "Consider Competitive Pricing (Competitor is cheaper)"
    elif improvement >= MIN_REVENUE_GAIN_TO_APPLY and abs(price_change_pct) >= MIN_PRICE_CHANGE_PCT:
        decision = "Apply Optimized Price"
    else:
        decision = "Keep Current Price"
    return improvement, decision, price_change_pct


def build_optimization(price, day, month, stock=None, competitor_price=None, product_code=""):
    current_demand = predict_demand(price, day, month)
    current_sellable = capped_units(current_demand, stock)
    current_revenue = revenue_for(price, current_demand, stock)
    best, curve, bounds = optimize_price(price, day, month, stock=stock, competitor_price=competitor_price)
    improvement, decision, price_change_pct = compare_prices(
        float(price), best["price"], current_revenue, best["revenue"], competitor_price
    )
    response = {
        "product_code": product_code or "N/A",
        "current_price": round(float(price), 2),
        "current_demand": round(current_demand, 2),
        "current_sellable_units": round(current_sellable, 2),
        "current_revenue": round(current_revenue, 2),
        "best_price": round(best["price"], 2),
        "best_demand": round(best["demand"], 2),
        "best_sellable_units": round(best["sellable_units"], 2),
        "best_revenue": round(best["revenue"], 2),
        "best_score": round(best["score"], 2),
        "improvement_%": round(improvement, 2),
        "price_change_%": round(price_change_pct, 2),
        "decision": decision,
        "optimizer_policy": {
            "objective": "maximize stock-capped revenue with competitor-aware market penalty",
            "search_min_price": bounds["min_price"],
            "search_max_price": bounds["max_price"],
            "competitor_match_band_%": round(COMPETITOR_MATCH_BAND * 100, 2),
            "apply_threshold_revenue_gain_%": MIN_REVENUE_GAIN_TO_APPLY,
        },
        "price_revenue_curve": curve,
    }
    if stock is not None:
        response["stock"] = int(stock)
    if competitor_price is not None:
        response["competitor_price"] = round(float(competitor_price), 2)
    return response


def products_df():
    df = read_csv(PRODUCTS_CSV)
    if "active" in df.columns:
        df["active"] = df["active"].astype(str).str.lower().isin(["true", "1", "yes"])
    return df


def save_products(df):
    write_csv(PRODUCTS_CSV, df)
    inventory = df[["product_id", "stock"]].copy()
    inventory["last_updated"] = datetime.now().isoformat(timespec="seconds")
    if os.path.exists(INVENTORY_CSV):
        old = read_csv(INVENTORY_CSV)
        threshold_map = dict(zip(old.get("product_id", []), old.get("low_stock_threshold", [])))
        inventory["low_stock_threshold"] = inventory["product_id"].map(threshold_map).fillna(10).astype(int)
    else:
        inventory["low_stock_threshold"] = 10
    write_csv(INVENTORY_CSV, inventory)


def product_by_id(product_id):
    df = products_df()
    if df.empty:
        return None
    match = df[df["product_id"].astype(str) == str(product_id)]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def append_rows(path, rows, columns):
    existing = read_csv(path, columns=columns)
    incoming = pd.DataFrame(rows, columns=columns)
    write_csv(path, pd.concat([existing, incoming], ignore_index=True))


def serialize_product(row, include_ai=True):
    product = dict(row)
    product["current_price"] = round(float(product["current_price"]), 2)
    product["original_price"] = round(float(product.get("original_price", product["current_price"])), 2)
    competitor_price = product.get("competitor_price")
    if competitor_price in (None, "", "nan") or pd.isna(competitor_price):
        competitor_price = None
    else:
        competitor_price = round(float(competitor_price), 2)
        product["competitor_price"] = competitor_price
    product["stock"] = int(product.get("stock", 0))
    product["active"] = str(product.get("active", True)).lower() in ["true", "1", "yes"]
    if include_ai:
        now = datetime.now()
        recommendation = build_optimization(
            product["current_price"], now.weekday(), now.month,
            stock=product["stock"], competitor_price=competitor_price,
            product_code=product.get("stock_code", product["product_id"])
        )
        product["ai_recommended_price"] = recommendation["best_price"]
        product["ai_predicted_demand"] = recommendation["best_demand"]
        product["ai_revenue_gain_%"] = recommendation["improvement_%"]
        product["ai_decision"] = recommendation["decision"]
        product["discount_%"] = round(
            max((product["original_price"] - product["current_price"]) / product["original_price"] * 100, 0), 1
        ) if product["original_price"] else 0.0
    return product


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "platform": "AI-Powered Smart Ecommerce Pricing Platform",
        "model_loaded": os.path.exists(MODEL_PATH),
        "model_path": MODEL_PATH,
        "data_files": {
            "products": os.path.exists(PRODUCTS_CSV),
            "inventory": os.path.exists(INVENTORY_CSV),
            "orders": os.path.exists(ORDERS_CSV),
            "sales_history": os.path.exists(SALES_HISTORY_CSV),
            "price_history": os.path.exists(PRICE_HISTORY_CSV),
        }
    }), 200


@app.route("/optimize", methods=["POST"])
def optimize():
    try:
        data = request.get_json(force=True)
        price = float(data["price"])
        day = int(data["day"])
        month = int(data["month"])
        if price < 1:
            return jsonify({"error": "price must be >= 1"}), 400
        if not 0 <= day <= 6:
            return jsonify({"error": "day must be 0-6"}), 400
        if not 1 <= month <= 12:
            return jsonify({"error": "month must be 1-12"}), 400

        competitor_price = data.get("competitor_price")
        competitor_price = float(competitor_price) if competitor_price not in (None, "") else None
        stock = data.get("stock")
        stock = int(stock) if stock not in (None, "") else None
        response = build_optimization(
            price, day, month, stock=stock, competitor_price=competitor_price,
            product_code=str(data.get("product_code", "")).strip()
        )
        return jsonify(response), 200
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {e}"}), 400
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid input: {e}"}), 400
    except Exception as e:
        logger.error("Unexpected error in /optimize: %s", e, exc_info=True)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/products", methods=["GET", "POST"])
def products():
    if request.method == "GET":
        df = products_df()
        products = [serialize_product(row) for row in df.to_dict("records")]
        category = request.args.get("category")
        search = request.args.get("search", "").strip().lower()
        if category and category != "All":
            products = [p for p in products if p.get("category") == category]
        if search:
            products = [p for p in products if search in p.get("product_name", "").lower()]
        return jsonify({"products": products, "count": len(products)}), 200

    try:
        data = request.get_json(force=True)
        df = products_df()
        product_id = str(data.get("product_id") or f"P{len(df) + 1:03d}")
        if product_id in df.get("product_id", pd.Series(dtype=str)).astype(str).tolist():
            return jsonify({"error": "product_id already exists"}), 409
        row = {
            "product_id": product_id,
            "stock_code": str(data.get("stock_code") or product_id),
            "product_name": data["product_name"],
            "category": data.get("category", "General"),
            "description": data.get("description", ""),
            "image_url": data.get("image_url", "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600"),
            "current_price": round(float(data["current_price"]), 2),
            "original_price": round(float(data.get("original_price", data["current_price"])), 2),
            "competitor_price": round(float(data["competitor_price"]), 2) if data.get("competitor_price") not in (None, "") else "",
            "stock": int(data.get("stock", 0)),
            "active": True,
        }
        save_products(pd.concat([df, pd.DataFrame([row])], ignore_index=True))
        return jsonify({"status": "created", "product": serialize_product(row)}), 201
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/product/<product_id>", methods=["GET"])
def product_detail(product_id):
    product = product_by_id(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(serialize_product(product)), 200


@app.route("/categories", methods=["GET"])
def categories():
    df = products_df()
    values = sorted(df["category"].dropna().astype(str).unique().tolist()) if "category" in df else []
    return jsonify({"categories": values}), 200


@app.route("/apply_price", methods=["POST"])
def apply_price():
    try:
        data = request.get_json(force=True)
        product_id = str(data["product_id"])
        new_price = round(float(data["new_price"]), 2)
        if new_price < 1:
            return jsonify({"error": "new_price must be >= 1"}), 400

        df = products_df()
        idx = df.index[df["product_id"].astype(str) == product_id].tolist()
        if not idx:
            return jsonify({"error": "Product not found"}), 404
        idx = idx[0]
        old_price = round(float(df.loc[idx, "current_price"]), 2)
        df.loc[idx, "current_price"] = new_price
        if float(df.loc[idx, "original_price"]) < new_price:
            df.loc[idx, "original_price"] = new_price
        save_products(df)

        append_rows(PRICE_HISTORY_CSV, [{
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "product_id": product_id,
            "old_price": old_price,
            "new_price": new_price,
            "reason": data.get("reason", "AI optimizer applied by admin"),
            "decision": data.get("decision", "Apply Optimized Price"),
            "predicted_demand": data.get("predicted_demand", ""),
            "revenue_gain_pct": data.get("revenue_gain_pct", ""),
        }], PRICE_HISTORY_COLUMNS)
        return jsonify({"status": "applied", "product_id": product_id, "old_price": old_price, "new_price": new_price}), 200
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def load_cart(session_id="default"):
    data = read_json(CART_JSON, {"carts": {}})
    return data.get("carts", {}).get(session_id, {"items": [], "total_items": 0, "total_price": 0.0})


def save_cart(session_id, cart):
    data = read_json(CART_JSON, {"carts": {}})
    data.setdefault("carts", {})[session_id] = cart
    write_json(CART_JSON, data)


def recalculate_cart(cart):
    cart["total_items"] = int(sum(int(item["quantity"]) for item in cart["items"]))
    cart["total_price"] = round(sum(int(item["quantity"]) * float(item["price"]) for item in cart["items"]), 2)
    return cart


@app.route("/cart", methods=["GET"])
def cart_get():
    session_id = request.args.get("session", "default")
    return jsonify(load_cart(session_id)), 200


@app.route("/cart/add", methods=["POST"])
def cart_add():
    try:
        data = request.get_json(force=True)
        session_id = data.get("session", "default")
        product_id = str(data["product_id"])
        quantity = int(data.get("quantity", 1))
        if quantity < 1:
            return jsonify({"error": "quantity must be >= 1"}), 400
        product = product_by_id(product_id)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        if int(product["stock"]) < quantity:
            return jsonify({"error": "Not enough stock"}), 400

        price = round(float(product["current_price"]), 2)
        cart = load_cart(session_id)
        for item in cart["items"]:
            if item["product_id"] == product_id:
                item["quantity"] = int(item["quantity"]) + quantity
                item["price"] = price
                break
        else:
            cart["items"].append({
                "product_id": product_id,
                "product_name": product["product_name"],
                "quantity": quantity,
                "price": price,
            })
        save_cart(session_id, recalculate_cart(cart))
        return jsonify({"status": "added", "cart": cart}), 200
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {e}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/cart/remove", methods=["POST"])
def cart_remove():
    data = request.get_json(force=True)
    session_id = data.get("session", "default")
    product_id = str(data.get("product_id", ""))
    cart = load_cart(session_id)
    cart["items"] = [item for item in cart["items"] if item["product_id"] != product_id]
    save_cart(session_id, recalculate_cart(cart))
    return jsonify({"status": "removed", "cart": cart}), 200


@app.route("/checkout", methods=["POST"])
def checkout():
    try:
        data = request.get_json(force=True)
        session_id = data.get("session", "default")
        customer_name = data.get("customer_name", "Guest")
        customer_email = data.get("customer_email", "guest@example.com")
        cart = load_cart(session_id)
        if not cart["items"]:
            return jsonify({"error": "Cart is empty"}), 400

        df = products_df()
        now = datetime.now()
        order_id = f"ORD-{now.strftime('%Y%m%d%H%M%S')}"
        order_rows = []
        sales_rows = []

        for item in cart["items"]:
            product_id = item["product_id"]
            quantity = int(item["quantity"])
            idx = df.index[df["product_id"].astype(str) == product_id].tolist()
            if not idx:
                return jsonify({"error": f"Product not found: {product_id}"}), 404
            idx = idx[0]
            if int(df.loc[idx, "stock"]) < quantity:
                return jsonify({"error": f"Not enough stock for {df.loc[idx, 'product_name']}"}), 400
            price = round(float(df.loc[idx, "current_price"]), 2)
            revenue = round(quantity * price, 2)
            df.loc[idx, "stock"] = int(df.loc[idx, "stock"]) - quantity
            order_rows.append({
                "order_id": order_id,
                "order_date": now.isoformat(timespec="seconds"),
                "customer_name": customer_name,
                "customer_email": customer_email,
                "product_id": product_id,
                "product_name": df.loc[idx, "product_name"],
                "quantity_sold": quantity,
                "price_at_sale": price,
                "revenue": revenue,
                "day_of_week": now.weekday(),
                "month": now.month,
            })
            sales_rows.append({
                "StockCode": df.loc[idx, "stock_code"],
                "date": now.date().isoformat(),
                "day_of_week": now.weekday(),
                "month": now.month,
                "demand": quantity,
                "Price": price,
            })

        save_products(df)
        append_rows(ORDERS_CSV, order_rows, ORDER_COLUMNS)
        append_rows(SALES_HISTORY_CSV, sales_rows, SALES_COLUMNS)
        save_cart(session_id, {"items": [], "total_items": 0, "total_price": 0.0})

        total = round(sum(row["revenue"] for row in order_rows), 2)
        return jsonify({
            "status": "success",
            "order_id": order_id,
            "total_amount": total,
            "items_count": sum(row["quantity_sold"] for row in order_rows),
        }), 200
    except Exception as e:
        logger.error("Checkout error: %s", e, exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/analytics", methods=["GET"])
def analytics():
    orders = read_csv(ORDERS_CSV, ORDER_COLUMNS)
    products = products_df()
    price_history = read_csv(PRICE_HISTORY_CSV, PRICE_HISTORY_COLUMNS)
    inventory = read_csv(INVENTORY_CSV)

    if orders.empty:
        revenue_by_product = []
        bestsellers = []
        monthly_sales = []
        demand_trends = []
    else:
        revenue_by_product = (
            orders.groupby(["product_id", "product_name"], as_index=False)["revenue"].sum()
            .sort_values("revenue", ascending=False)
            .to_dict("records")
        )
        bestsellers = (
            orders.groupby(["product_id", "product_name"], as_index=False)["quantity_sold"].sum()
            .sort_values("quantity_sold", ascending=False)
            .to_dict("records")
        )
        monthly_sales = (
            orders.groupby("month", as_index=False)["revenue"].sum()
            .sort_values("month")
            .to_dict("records")
        )
        demand_trends = (
            orders.groupby(["order_date", "product_id"], as_index=False)["quantity_sold"].sum()
            .sort_values("order_date")
            .to_dict("records")
        )

    low_stock = []
    if not inventory.empty and not products.empty:
        merged = inventory.merge(products[["product_id", "product_name", "category"]], on="product_id", how="left")
        low = merged[merged["stock"].astype(float) <= merged["low_stock_threshold"].astype(float)]
        low_stock = low.to_dict("records")

    return jsonify({
        "total_revenue": round(float(orders["revenue"].sum()), 2) if "revenue" in orders else 0.0,
        "total_orders": int(orders["order_id"].nunique()) if "order_id" in orders else 0,
        "units_sold": int(orders["quantity_sold"].sum()) if "quantity_sold" in orders else 0,
        "revenue_by_product": revenue_by_product,
        "bestselling_products": bestsellers,
        "monthly_sales": monthly_sales,
        "demand_trends": demand_trends,
        "low_stock_alerts": low_stock,
        "price_change_history": price_history.tail(50).to_dict("records"),
    }), 200


@app.route("/reload_model", methods=["POST"])
def reload_model():
    global model
    token = request.headers.get("X-Reload-Token", "")
    expected = os.environ.get("RELOAD_TOKEN", "")
    if expected and token != expected:
        return jsonify({"error": "Unauthorized"}), 401
    model = load_model()
    return jsonify({"status": "model reloaded"}), 200


_retrain_state = {"running": False, "last_status": None, "last_log": ""}


def _run_retrain_background(new_data):
    global model
    _retrain_state.update({"running": True, "last_status": None, "last_log": ""})
    try:
        proc = subprocess.run(
            [sys.executable, "retrain.py", "--new_data", new_data],
            capture_output=True, text=True, timeout=600
        )
        _retrain_state["last_log"] = proc.stdout + proc.stderr
        _retrain_state["last_status"] = "success" if proc.returncode == 0 else "failed"
        if proc.returncode == 0:
            model = load_model()
    except subprocess.TimeoutExpired:
        _retrain_state["last_status"] = "timeout"
        _retrain_state["last_log"] = "Retraining timed out after 600s."
    except Exception as e:
        _retrain_state["last_status"] = "error"
        _retrain_state["last_log"] = str(e)
    finally:
        _retrain_state["running"] = False


@app.route("/trigger_retrain", methods=["POST"])
def trigger_retrain():
    token = request.headers.get("X-Reload-Token", "")
    expected = os.environ.get("RELOAD_TOKEN", "")
    if expected and token != expected:
        return jsonify({"error": "Unauthorized"}), 401
    if _retrain_state["running"]:
        return jsonify({"status": "already_running", "message": "Retraining is already in progress."}), 409

    data = request.get_json(silent=True) or {}
    new_data = data.get("new_data", SALES_HISTORY_CSV)
    thread = threading.Thread(target=_run_retrain_background, args=(new_data,), daemon=True)
    thread.start()
    return jsonify({"status": "accepted", "message": "Retraining started in background.", "new_data": new_data}), 202


@app.route("/retrain_status", methods=["GET"])
def retrain_status():
    return jsonify({
        "running": _retrain_state["running"],
        "last_status": _retrain_state["last_status"],
        "last_log": _retrain_state["last_log"][-2000:],
    }), 200


# =========================
# USER LOGIN ENDPOINTS
# =========================
@app.route("/user/register", methods=["POST"])
def user_register():
    data = request.get_json(force=True)
    name = data.get("name", "").strip()
    email = normalize_email(data.get("email"))
    password = str(data.get("password", ""))
    
    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    
    # Check if email already exists
    users_data = read_json(USERS_JSON, {"users": []})
    for user in users_data.get("users", []):
        if normalize_email(user.get("email")) == email:
            if not user.get("password_hash"):
                user["name"] = name
                user["email"] = email
                user["password_hash"] = generate_password_hash(password)
                user["role"] = user.get("role", "customer")
                user["updated_at"] = datetime.now().isoformat()
                write_json(USERS_JSON, users_data)
                return jsonify({
                    "success": True,
                    **public_user(user),
                    "message": "Account password created"
                }), 200
            return jsonify({"error": "Email already registered"}), 400
    
    # Create new user
    existing_customer_count = sum(
        1 for user in users_data.get("users", [])
        if str(user.get("user_id", "")).startswith("cust_")
    )
    user_id = f"cust_{existing_customer_count + 1}"
    new_user = {
        "user_id": user_id,
        "name": name,
        "email": email,
        "password_hash": generate_password_hash(password),
        "role": "customer",
        "created_at": datetime.now().isoformat()
    }
    users_data.setdefault("users", []).append(new_user)
    write_json(USERS_JSON, users_data)
    
    return jsonify({
        "success": True,
        **public_user(new_user),
        "message": "Registration successful"
    }), 201


@app.route("/user/login", methods=["POST"])
def user_login():
    data = request.get_json(force=True)
    email = normalize_email(data.get("email"))
    password = str(data.get("password", ""))
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    # Find user by email
    users_data = read_json(USERS_JSON, {"users": []})
    for user in users_data.get("users", []):
        if normalize_email(user.get("email")) == email:
            password_hash = user.get("password_hash")
            if not password_hash:
                return jsonify({"error": "This account needs a password. Please use Register once to create one."}), 400
            if not check_password_hash(password_hash, password):
                return jsonify({"error": "Invalid email or password"}), 401
            return jsonify({
                "success": True,
                **public_user(user),
                "message": "Login successful"
            }), 200
    
    return jsonify({"error": "Invalid email or password"}), 401


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)
