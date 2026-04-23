# AI-Powered Smart Ecommerce Pricing Platform

One unified Streamlit + Flask + Python platform where an ecommerce store directly uses the AI price optimizer.

## What It Does

Admin side:
- Manage products and inventory
- Run demand prediction and price optimization
- Compare current price vs optimized price
- See predicted demand, revenue gain, and decision suggestion
- Apply the optimized price directly to the ecommerce catalog
- View revenue, bestselling products, demand trends, low stock alerts, and price history
- Trigger retraining with new CSV/Excel sales data

Customer side:
- Browse products
- Search and filter by category
- View product details, images, stock, discount badges, and AI-updated prices
- Add products to cart
- Complete a mock checkout
- Checkout writes orders and sales data back to CSV for future retraining

## Integrated Flow

```text
Admin adds product
-> ML model predicts demand and best price
-> Admin applies optimized price
-> products.csv is updated
-> Customer store reads the updated catalog price
-> Customer buys product
-> orders.csv and sales_history.csv are updated
-> New sales data can be used for retraining
```

## Tech Stack

- Streamlit
- Flask REST API
- Python
- CSV files
- JSON files
- Existing scikit-learn ML model (`pricing_model.pkl`)

No Docker, Kubernetes, Jenkins, Ansible, CI/CD, or cloud deployment is included.

## Folder Structure

```text
SPE_MP/
├── app.py                    # Unified Flask API: optimizer + ecommerce + analytics
├── streamlit_app.py          # Admin dashboard
├── streamlit_customer.py     # Customer ecommerce store
├── retrain.py                # Retraining pipeline
├── test_api.py               # Optimizer API smoke tests
├── pricing_model.pkl         # Existing trained model
├── clean_demand_data.csv     # Existing training dataset
├── data/
│   ├── products.csv
│   ├── inventory.csv
│   ├── orders.csv
│   ├── sales_history.csv
│   ├── price_history.csv
│   ├── users.json
│   ├── cart.json
│   └── config.json
└── requirements.txt
```

## Run Locally

```bash
cd ~/Desktop/SPE_MP

# Terminal 1
venv/bin/python app.py

# Terminal 2
venv/bin/streamlit run streamlit_app.py --server.port 8503

# Terminal 3
venv/bin/streamlit run streamlit_customer.py --server.port 8504
```

URLs:
- Flask API: `http://127.0.0.1:5001`
- Admin dashboard: `http://127.0.0.1:8503`
- Customer store: `http://127.0.0.1:8504`

## Key API Endpoints

- `GET /health`
- `GET /products`
- `POST /products`
- `GET /product/<product_id>`
- `POST /optimize`
- `POST /apply_price`
- `GET /cart`
- `POST /cart/add`
- `POST /cart/remove`
- `POST /checkout`
- `GET /analytics`
- `POST /trigger_retrain`
- `GET /retrain_status`

## Data Schemas

`products.csv`
```text
product_id,stock_code,product_name,category,description,image_url,current_price,original_price,stock,active
```

`inventory.csv`
```text
product_id,stock,last_updated,low_stock_threshold
```

`orders.csv`
```text
order_id,order_date,customer_name,product_id,product_name,quantity_sold,price_at_sale,revenue,day_of_week,month
```

`sales_history.csv`
```text
StockCode,date,day_of_week,month,demand,Price
```

`price_history.csv`
```text
timestamp,product_id,old_price,new_price,reason,decision,predicted_demand,revenue_gain_pct
```

## Verification

```bash
venv/bin/python -m py_compile app.py retrain.py streamlit_app.py streamlit_customer.py test_api.py
venv/bin/python test_api.py --url http://127.0.0.1:5001
```
