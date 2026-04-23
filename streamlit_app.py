import pandas as pd
import requests
import streamlit as st


st.set_page_config(
    page_title="AI Smart Pricing Admin",
    page_icon="🛒",
    layout="wide",
)

API_URL = "http://127.0.0.1:5001"


def api_get(path, params=None):
    r = requests.get(f"{API_URL}{path}", params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def api_post(path, payload=None):
    r = requests.post(f"{API_URL}{path}", json=payload or {}, timeout=30)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=20)
def load_products():
    return api_get("/products")["products"]


@st.cache_data(ttl=20)
def load_analytics():
    return api_get("/analytics")


def clear_cache():
    load_products.clear()
    load_analytics.clear()


st.title("AI-Powered Smart Ecommerce Pricing Platform")
st.caption("Admin dashboard for product catalog, demand prediction, revenue optimization, and ecommerce pricing control")

try:
    health = api_get("/health")
    st.success(f"API connected | Model loaded: {health['model_loaded']}")
except Exception as exc:
    st.error(f"Flask API is offline. Start it with `python app.py`. Details: {exc}")
    st.stop()


tabs = st.tabs(["Optimizer", "Products", "Analytics", "Retraining"])


with tabs[0]:
    products = load_products()
    if not products:
        st.warning("No products found. Add a product from the Products tab.")
        st.stop()

    product_options = {f"{p['product_name']} ({p['product_id']})": p for p in products}
    selected_label = st.selectbox("Select product", list(product_options.keys()))
    product = product_options[selected_label]

    c1, c2, c3, c4 = st.columns(4)
    current_price = c1.number_input("Current selling price", min_value=1.0, value=float(product["current_price"]), step=1.0)
    competitor_price = c2.number_input("Competitor price", min_value=0.0, value=float(product["current_price"]) * 0.95, step=1.0)
    stock = c3.number_input("Stock quantity", min_value=0, value=int(product["stock"]), step=1)
    day = c4.selectbox("Day", options=list(range(7)), format_func=lambda x: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][x])
    month = st.selectbox("Month", options=list(range(1, 13)), format_func=lambda x: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][x - 1])

    if st.button("Run AI Optimizer", type="primary", use_container_width=True):
        payload = {
            "product_code": product["stock_code"],
            "price": current_price,
            "day": day,
            "month": month,
            "stock": stock,
            "competitor_price": competitor_price if competitor_price > 0 else None,
        }
        result = api_post("/optimize", payload)
        st.session_state.optimizer_result = result
        st.session_state.optimizer_product_id = product["product_id"]

    result = st.session_state.get("optimizer_result")
    if result and st.session_state.get("optimizer_product_id") == product["product_id"]:
        st.subheader("Optimization Result")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Current price", f"₹{result['current_price']:.2f}")
        m2.metric("Best price", f"₹{result['best_price']:.2f}", f"₹{result['best_price'] - result['current_price']:.2f}")
        m3.metric("Predicted demand", f"{result['best_demand']:.0f} units")
        m4.metric("Revenue gain", f"{result['improvement_%']:.2f}%")

        decision = result["decision"]
        if decision == "Apply Optimized Price":
            st.success(f"Decision suggestion: {decision}")
        elif "Competitive" in decision:
            st.info(f"Decision suggestion: {decision}")
        else:
            st.warning(f"Decision suggestion: {decision}")

        curve = pd.DataFrame(result["price_revenue_curve"])
        st.line_chart(curve.set_index("price")["revenue"])

        if st.button("Apply optimized price to ecommerce store", use_container_width=True):
            applied = api_post("/apply_price", {
                "product_id": product["product_id"],
                "new_price": result["best_price"],
                "decision": result["decision"],
                "predicted_demand": result["best_demand"],
                "revenue_gain_pct": result["improvement_%"],
            })
            clear_cache()
            st.success(f"Updated {applied['product_id']} from ₹{applied['old_price']:.2f} to ₹{applied['new_price']:.2f}. Customers now see the new price.")


with tabs[1]:
    st.subheader("Product Management")
    products = load_products()
    df = pd.DataFrame(products)
    visible_cols = ["product_id", "product_name", "category", "current_price", "original_price", "stock", "ai_recommended_price", "ai_decision"]
    st.dataframe(df[[c for c in visible_cols if c in df.columns]], use_container_width=True, hide_index=True)

    with st.expander("Add product"):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Product name")
        category = c2.text_input("Category", value="General")
        stock_code = c3.text_input("Stock code")
        description = st.text_area("Description")
        c4, c5, c6 = st.columns(3)
        price = c4.number_input("Current price", min_value=1.0, value=499.0, step=1.0)
        original = c5.number_input("Original price", min_value=1.0, value=699.0, step=1.0)
        stock_qty = c6.number_input("Stock", min_value=0, value=25, step=1)
        image_url = st.text_input("Image URL", value="https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600")

        if st.button("Add product to catalog"):
            if not name:
                st.error("Product name is required.")
            else:
                created = api_post("/products", {
                    "product_name": name,
                    "category": category,
                    "stock_code": stock_code or name.upper().replace(" ", "_"),
                    "description": description,
                    "current_price": price,
                    "original_price": original,
                    "stock": stock_qty,
                    "image_url": image_url,
                })
                clear_cache()
                st.success(f"Created {created['product']['product_name']} and made it available in the store.")


with tabs[2]:
    st.subheader("Analytics")
    analytics = load_analytics()
    c1, c2, c3 = st.columns(3)
    c1.metric("Total revenue", f"₹{analytics['total_revenue']:.2f}")
    c2.metric("Orders", analytics["total_orders"])
    c3.metric("Units sold", analytics["units_sold"])

    left, right = st.columns(2)
    with left:
        st.markdown("Revenue by product")
        revenue = pd.DataFrame(analytics["revenue_by_product"])
        if not revenue.empty:
            st.bar_chart(revenue.set_index("product_name")["revenue"])
        else:
            st.info("No orders yet.")

        st.markdown("Low stock alerts")
        low_stock = pd.DataFrame(analytics["low_stock_alerts"])
        if not low_stock.empty:
            st.dataframe(low_stock, use_container_width=True, hide_index=True)
        else:
            st.success("No low stock alerts.")

    with right:
        st.markdown("Bestselling products")
        bestsellers = pd.DataFrame(analytics["bestselling_products"])
        if not bestsellers.empty:
            st.bar_chart(bestsellers.set_index("product_name")["quantity_sold"])
        else:
            st.info("No sales yet.")

        st.markdown("Monthly sales")
        monthly = pd.DataFrame(analytics["monthly_sales"])
        if not monthly.empty:
            st.line_chart(monthly.set_index("month")["revenue"])
        else:
            st.info("No monthly sales yet.")

    st.markdown("Price change history")
    history = pd.DataFrame(analytics["price_change_history"])
    if not history.empty:
        st.dataframe(history, use_container_width=True, hide_index=True)
    else:
        st.info("No price changes applied yet.")


with tabs[3]:
    st.subheader("Retraining")
    st.write("Upload or generate new sales through checkout, then retrain with `data/sales_history.csv`.")

    retrain_file = st.text_input("New training data path", value="data/sales_history.csv")
    c1, c2 = st.columns(2)
    if c1.button("Trigger retraining"):
        response = api_post("/trigger_retrain", {"new_data": retrain_file})
        st.success(response["message"])
    if c2.button("Refresh retrain status"):
        status = api_get("/retrain_status")
        st.json(status)
