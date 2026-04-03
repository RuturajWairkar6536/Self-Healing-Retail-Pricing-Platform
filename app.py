from flask import Flask, request, jsonify
import pickle
import pandas as pd
import numpy as np

app = Flask(__name__)

# =========================
# Load model
# =========================
with open('pricing_model.pkl', 'rb') as f:
    model = pickle.load(f)

# =========================
# Functions
# =========================
def predict_demand(price, day_of_week, month):
    features = pd.DataFrame({
        'Price': [price],
        'day_of_week': [day_of_week],
        'month': [month]
    })
    demand = model.predict(features)[0]
    return max(demand, 0)


def optimize_price(current_price, day_of_week, month):
    best_price = current_price
    best_revenue = 0
    best_demand = 0

    price_range = np.linspace(current_price * 0.8, current_price * 1.2, 20)

    for price in price_range:
        demand = predict_demand(price, day_of_week, month)
        revenue = price * demand

        if revenue > best_revenue:
            best_revenue = revenue
            best_price = price
            best_demand = demand

    return best_price, best_demand, best_revenue


# =========================
# API Endpoint
# =========================
@app.route('/optimize', methods=['POST'])
def optimize():

    data = request.get_json()

    price = float(data['price'])
    day = int(data['day'])
    month = int(data['month'])

    # current
    current_demand = predict_demand(price, day, month)
    current_revenue = price * current_demand

    # optimized
    best_price, best_demand, best_revenue = optimize_price(price, day, month)

    improvement = ((best_revenue - current_revenue) / current_revenue) * 100 if current_revenue != 0 else 0

    decision = "Apply Optimized Price" if improvement > 5 else "Keep Current Price"

    return jsonify({
        "current_price": price,
        "current_revenue": float(current_revenue),
        "best_price": float(best_price),
        "best_revenue": float(best_revenue),
        "predicted_demand": float(best_demand),
        "improvement_%": float(improvement),
        "decision": decision
    })


# =========================
# Run app
# =========================
if __name__ == '__main__':
    app.run(debug=True)