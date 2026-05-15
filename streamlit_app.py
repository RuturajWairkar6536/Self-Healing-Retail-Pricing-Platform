import os
import pandas as pd
import requests
import streamlit as st


st.set_page_config(
    page_title="AI Smart Pricing Admin",
    page_icon="🛒",
    layout="wide",
)

st.markdown(
    """
    <style>
    :root {
        --surface: #fbfaf7;
        --panel: #ffffff;
        --ink: #24312f;
        --muted: #6f7f7b;
        --accent: #2f8f83;
        --accent-soft: #e4f3ef;
        --line: #dde7e2;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(255, 240, 232, 0.9), transparent 32rem),
            linear-gradient(180deg, #fbfaf7 0%, #eef7f4 100%);
        color: var(--ink);
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }

    h1, h2, h3 {
        color: #20302d;
        letter-spacing: 0;
    }

    [data-testid="stMetric"],
    [data-testid="stDataFrame"],
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid var(--line);
        border-radius: 8px;
        box-shadow: 0 10px 30px rgba(44, 81, 76, 0.06);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid var(--line);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        color: var(--muted);
    }

    .stTabs [aria-selected="true"] {
        background: var(--accent-soft);
        color: #1f6f66;
    }

    .stButton > button {
        border-radius: 8px;
        border-color: #b8d9d2;
    }

    .stButton > button[kind="primary"] {
        background: #2f8f83;
        border-color: #2f8f83;
    }

    .admin-hero {
        padding: 1.55rem 1.75rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, .65);
        background:
            linear-gradient(120deg, rgba(32, 48, 45, .94), rgba(47, 143, 131, .72)),
            url("https://images.unsplash.com/photo-1556740758-90de374c12ad?w=1600&h=520&fit=crop&q=80");
        background-size: cover;
        background-position: center;
        color: #ffffff;
        box-shadow: 0 22px 54px rgba(30, 69, 63, 0.18);
        margin-bottom: 1.25rem;
    }

    .admin-hero h1 {
        color: #ffffff;
        margin: 0 0 .4rem;
        font-size: clamp(2rem, 4vw, 3.15rem);
        line-height: 1.05;
    }

    .admin-hero p {
        margin: 0;
        max-width: 760px;
        color: rgba(255, 255, 255, .9);
        font-size: 1.02rem;
        line-height: 1.6;
    }

    .section-heading {
        margin: .8rem 0 1rem;
        padding-bottom: .7rem;
        border-bottom: 1px solid var(--line);
    }

    .section-heading h2 {
        margin: 0;
        font-size: 1.45rem;
    }

    .section-heading p {
        margin: .25rem 0 0;
        color: var(--muted);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

API_URL = os.environ.get("ADMIN_API_URL", "http://pricing-api:5001")


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


def section_heading(title, subtitle):
    st.markdown(
        f"""
        <div class="section-heading">
            <h2>{title}</h2>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown(
    """
    <div class="admin-hero">
        <h1>Smart Pricing Admin</h1>
        <p>Monitor demand, tune live product prices, and keep the storefront catalog healthy from one calmer dashboard.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    health = api_get("/health")
    st.success(f"API connected | Model loaded: {health['model_loaded']}")
except Exception as exc:
    st.error(f"Flask API is offline. Start it with `python app.py`. Details: {exc}")
    st.stop()


tabs = st.tabs(["Optimizer", "Products", "Analytics", "Retraining"])


with tabs[0]:
    section_heading("Optimizer", "Select a product and compare the current price against the AI recommendation.")
    products = load_products()
    if not products:
        st.warning("No products found. Add a product from the Products tab.")
        st.stop()

    product_options = {f"{p['product_name']} ({p['product_id']})": p for p in products}
    selected_label = st.selectbox("Select product", list(product_options.keys()))
    product = product_options[selected_label]

    c1, c2, c3, c4 = st.columns(4)
    current_price = c1.number_input("Current selling price", min_value=1.0, value=float(product["current_price"]), step=1.0)
    stored_competitor = product.get("competitor_price") or float(product["current_price"]) * 0.95
    competitor_price = c2.number_input("Competitor price", min_value=0.0, value=float(stored_competitor), step=1.0)
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
        m2.metric("Recommended price", f"₹{result['best_price']:.2f}", f"{result.get('price_change_%', 0):.2f}%")
        m3.metric("Sellable units", f"{result.get('best_sellable_units', result['best_demand']):.0f}", f"Demand {result['best_demand']:.0f}")
        m4.metric("Revenue gain", f"{result['improvement_%']:.2f}%")

        policy = result.get("optimizer_policy", {})
        if policy:
            st.caption(
                "Policy: "
                f"searched ₹{policy['search_min_price']:.2f} to ₹{policy['search_max_price']:.2f}; "
                f"competitor band ±{policy['competitor_match_band_%']:.0f}%; "
                f"apply only if revenue gain ≥ {policy['apply_threshold_revenue_gain_%']:.0f}%."
            )

        decision = result["decision"]
        if decision == "Apply Optimized Price":
            st.success(f"Decision suggestion: {decision}")
        elif "Competitive" in decision:
            st.info(f"Decision suggestion: {decision}")
        else:
            st.warning(f"Decision suggestion: {decision}")

        curve = pd.DataFrame(result["price_revenue_curve"])
        chart_cols = [c for c in ["revenue", "score"] if c in curve.columns]
        st.line_chart(curve.set_index("price")[chart_cols])
        display_cols = ["price", "predicted_demand", "sellable_units", "revenue", "market_penalty", "score"]
        st.dataframe(curve[[c for c in display_cols if c in curve.columns]], use_container_width=True, hide_index=True)

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
    section_heading("Product Management", "Review catalog health and add products to the customer store.")
    products = load_products()
    df = pd.DataFrame(products)
    visible_cols = ["product_id", "product_name", "category", "current_price", "competitor_price", "original_price", "stock", "ai_recommended_price", "ai_decision"]
    st.dataframe(df[[c for c in visible_cols if c in df.columns]], use_container_width=True, hide_index=True)

    with st.expander("Add product"):
        c1, c2, c3 = st.columns(3)
        name = c1.text_input("Product name")
        category = c2.text_input("Category", value="General")
        stock_code = c3.text_input("Stock code")
        description = st.text_area("Description")
        c4, c5, c6, c7 = st.columns(4)
        price = c4.number_input("Current price", min_value=1.0, value=499.0, step=1.0)
        original = c5.number_input("Original price", min_value=1.0, value=699.0, step=1.0)
        competitor = c6.number_input("Competitor price", min_value=0.0, value=469.0, step=1.0)
        stock_qty = c7.number_input("Stock", min_value=0, value=25, step=1)
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
                    "competitor_price": competitor if competitor > 0 else None,
                    "stock": stock_qty,
                    "image_url": image_url,
                })
                clear_cache()
                st.success(f"Created {created['product']['product_name']} and made it available in the store.")


with tabs[2]:
    section_heading("Analytics", "Track revenue, orders, inventory pressure, and recent price changes.")
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
    section_heading("Retraining", "Refresh the pricing model after new sales data is available.")
    st.write("Upload or generate new sales through checkout, then retrain with `data/sales_history.csv`.")

    retrain_file = st.text_input("New training data path", value="data/sales_history.csv")
    c1, c2 = st.columns(2)
    if c1.button("Trigger retraining"):
        response = api_post("/trigger_retrain", {"new_data": retrain_file})
        st.success(response["message"])
    if c2.button("Refresh retrain status"):
        status = api_get("/retrain_status")
        st.json(status)
