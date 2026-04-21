import streamlit as st
import requests
import numpy as np
import pandas as pd

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="Retail Price Optimizer",
    page_icon="🛒",
    layout="centered"
)

FLASK_URL = "http://127.0.0.1:5001"
CSV_PATH  = "clean_demand_data.csv"

# =========================
# Load Product List
# =========================
@st.cache_data
def load_products():
    """Load top 50 products by number of records, return StockCode + avg price."""
    try:
        df = pd.read_csv(CSV_PATH, dtype={"StockCode": str})
        top = (
            df.groupby("StockCode")
            .agg(records=("Price", "count"), avg_price=("Price", "mean"))
            .sort_values("records", ascending=False)
            .head(50)
            .reset_index()
        )
        return top
    except Exception:
        return pd.DataFrame(columns=["StockCode", "avg_price"])


# =========================
# Health Check
# =========================
def api_online():
    try:
        r = requests.get(f"{FLASK_URL}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


# =========================
# Title
# =========================
st.title("🛒 Retail Price Optimizer")
st.caption("Predict demand & find the best price to maximise revenue")

if not api_online():
    st.error("🔴 Flask API is offline — run `python app.py` first")
    st.stop()
else:
    st.success("🟢 API connected")

st.divider()

# =========================
# Load Products
# =========================
products_df = load_products()
product_list = products_df["StockCode"].tolist() if not products_df.empty else []

# =========================
# Inputs
# =========================
st.subheader("📦 Product & Pricing")

col1, col2 = st.columns(2)

with col1:
    if product_list:
        selected_product = st.selectbox("Select Product (StockCode)", product_list)
        # Auto-fill price from dataset average
        default_price = float(
            products_df.loc[products_df["StockCode"] == selected_product, "avg_price"].values[0]
        )
    else:
        selected_product = st.text_input("Product Code", value="PROD001")
        default_price = 100.0

with col2:
    price = st.number_input(
        "Current Price (₹)",
        min_value=0.01,
        value=round(default_price, 2),
        step=0.01,
        format="%.2f"
    )

st.subheader("📅 Date & Stock")

col3, col4, col5 = st.columns(3)

with col3:
    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    day = st.selectbox("Day of Week", options=list(range(7)),
                       format_func=lambda x: day_labels[x])

with col4:
    month_labels = ["Jan","Feb","Mar","Apr","May","Jun",
                    "Jul","Aug","Sep","Oct","Nov","Dec"]
    month = st.selectbox("Month", options=list(range(1, 13)),
                         format_func=lambda x: month_labels[x - 1])

with col5:
    stock = st.number_input("Stock (units)", min_value=0, value=50, step=1)

# Optional competitor price
with st.expander("🏪 Competitor Price (optional)"):
    use_competitor = st.checkbox("Add competitor price")
    competitor_price = None
    if use_competitor:
        competitor_price = st.number_input(
            "Competitor Price (₹)", min_value=0.01,
            value=round(price * 0.9, 2), step=0.01, format="%.2f"
        )

st.divider()

# =========================
# Optimize Button
# =========================
if st.button("🚀 Optimize Price", type="primary", use_container_width=True):

    payload = {
        "price":        price,
        "day":          day,
        "month":        month,
        "stock":        stock,
        "product_code": selected_product
    }
    if competitor_price:
        payload["competitor_price"] = competitor_price

    with st.spinner("Running optimisation..."):
        try:
            resp = requests.post(f"{FLASK_URL}/optimize", json=payload, timeout=15)

            if resp.status_code != 200:
                st.error(f"API Error {resp.status_code}: {resp.json().get('error','unknown')}")
                st.stop()

            r = resp.json()

            # ── Results ────────────────────────────────────
            st.subheader("📊 Results")

            c1, c2, c3 = st.columns(3)
            c1.metric("Current Price",      f"₹{r['current_price']:.2f}")
            c2.metric("Best Price",         f"₹{r['best_price']:.2f}",
                      delta=f"₹{r['best_price'] - r['current_price']:.2f}")
            c3.metric("Revenue Improvement",f"{r['improvement_%']:.1f}%")

            c4, c5, c6 = st.columns(3)
            c4.metric("Current Revenue",    f"₹{r['current_revenue']:.2f}")
            c5.metric("Optimised Revenue",  f"₹{r['best_revenue']:.2f}")
            c6.metric("Predicted Demand",   f"{r['best_demand']:.0f} units")

            # ── Decision ───────────────────────────────────
            decision = r["decision"]
            if "Apply" in decision:
                st.success(f"✅ Decision: {decision}")
            elif "Competitive" in decision:
                st.info(f"💡 Decision: {decision}")
            else:
                st.warning(f"⚠️ Decision: {decision}")

            # ── Price vs Revenue Chart ──────────────────────
            st.subheader("📈 Price vs Revenue")

            prices_range = np.linspace(price * 0.7, price * 1.3, 20)
            revenues     = []

            for p in prices_range:
                res = requests.post(
                    f"{FLASK_URL}/optimize",
                    json={"price": float(p), "day": day, "month": month},
                    timeout=15
                )
                revenues.append(res.json()["best_revenue"] if res.status_code == 200 else 0)

            chart_df = pd.DataFrame({
                "Price (₹)":   prices_range,
                "Revenue (₹)": revenues
            }).set_index("Price (₹)")

            st.line_chart(chart_df)

            # ── Summary table ───────────────────────────────
            with st.expander("📋 Full Summary"):
                st.table(pd.DataFrame({
                    "Field": [
                        "Product", "Current Price", "Best Price", "Price Delta",
                        "Current Demand", "Optimised Demand",
                        "Current Revenue", "Optimised Revenue",
                        "Revenue Improvement", "Decision"
                    ],
                    "Value": [
                        selected_product,
                        f"₹{r['current_price']:.2f}",
                        f"₹{r['best_price']:.2f}",
                        f"₹{r['best_price'] - r['current_price']:.2f}",
                        f"{r['current_demand']:.0f} units",
                        f"{r['best_demand']:.0f} units",
                        f"₹{r['current_revenue']:.2f}",
                        f"₹{r['best_revenue']:.2f}",
                        f"{r['improvement_%']:.2f}%",
                        decision
                    ]
                }))

        except requests.exceptions.ConnectionError:
            st.error("🚨 Cannot connect to Flask API.")
        except Exception as e:
            st.error(f"🚨 Error: {e}")