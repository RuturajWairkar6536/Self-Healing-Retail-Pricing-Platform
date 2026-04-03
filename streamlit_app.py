import streamlit as st
import requests

st.title("💰 Retail Price Optimization System")

# Inputs
price = st.slider("Select Current Price", 1, 500, 100)
day = st.selectbox("Day of Week (0=Mon, 6=Sun)", list(range(7)))
month = st.selectbox("Month", list(range(1, 13)))

# Button
if st.button("Optimize Price"):

    url = "http://127.0.0.1:5000/optimize"

    data = {
        "price": price,
        "day": day,
        "month": month
    }

    response = requests.post(url, json=data)

    if response.status_code == 200:
        result = response.json()

        st.subheader("📊 Results")

        st.write(f"Current Price: {result['current_price']}")
        st.write(f"Current Revenue: {result['current_revenue']}")

        st.write(f"Best Price: {result['best_price']}")
        st.write(f"Optimized Revenue: {result['best_revenue']}")

        st.write(f"Predicted Demand: {result['predicted_demand']}")
        st.write(f"Improvement %: {result['improvement_%']}")

        st.success(f"Decision: {result['decision']}")

    else:
        st.error("API call failed ❌")