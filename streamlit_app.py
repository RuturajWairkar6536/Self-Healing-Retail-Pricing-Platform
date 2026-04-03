import streamlit as st
import requests
import numpy as np
import pandas as pd

# =========================
# Title
# =========================
st.title("💰 Retail Price Optimization System")

# =========================
# Inputs
# =========================
price = st.slider("Select Current Price", 1, 500, 100)
day = st.selectbox("Day of Week (0=Mon, 6=Sun)", list(range(7)))
month = st.selectbox("Month", list(range(1, 13)))

# =========================
# Button
# =========================
if st.button("Optimize Price"):

    url = "http://127.0.0.1:5000/optimize"

    data = {
        "price": price,
        "day": day,
        "month": month
    }

    try:
        response = requests.post(url, json=data)

        if response.status_code == 200:
            result = response.json()

            # =========================
            # Results UI
            # =========================
            st.subheader("📊 Optimization Results")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Current Revenue", f"{result['current_revenue']:.2f}")

            with col2:
                st.metric("Optimized Revenue", f"{result['best_revenue']:.2f}")

            st.write(f"💰 Best Price: {result['best_price']}")
            st.write(f"📦 Predicted Demand: {result['predicted_demand']:.2f}")
            st.write(f"📈 Improvement: {result['improvement_%']:.2f}%")

            # Decision
            if "Apply" in result['decision']:
                st.success(f"✅ {result['decision']}")
            else:
                st.warning(f"⚠️ {result['decision']}")

            # =========================
            # 📈 Price vs Revenue Curve
            # =========================
            st.subheader("📈 Price vs Revenue Curve")

            prices = np.linspace(price * 0.8, price * 1.2, 25)
            revenues = []

            for p in prices:
                temp_data = {
                    "price": float(p),
                    "day": day,
                    "month": month
                }

                temp_response = requests.post(url, json=temp_data)

                if temp_response.status_code == 200:
                    temp_result = temp_response.json()
                    revenues.append(temp_result['best_revenue'])
                else:
                    revenues.append(0)

            df = pd.DataFrame({
                "Price": prices,
                "Revenue": revenues
            })

            st.line_chart(df.set_index("Price"))

        else:
            st.error("API call failed ❌")

    except:
        st.error("Cannot connect to Flask API 🚨")