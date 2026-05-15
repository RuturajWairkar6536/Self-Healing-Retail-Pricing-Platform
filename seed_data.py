import pandas as pd
import json
import os
from werkzeug.security import generate_password_hash

os.makedirs('data', exist_ok=True)

# 1. Generate products.csv from clean_demand_data.csv
if os.path.exists('clean_demand_data.csv'):
    df = pd.read_csv('clean_demand_data.csv')
    # Filter out invalid StockCodes (non-alphanumeric/empty)
    df['StockCode'] = df['StockCode'].astype(str)
    
    products = df.groupby('StockCode').agg({
        'Price': 'mean',
        'demand': 'sum'
    }).reset_index()
    
    # Sort by demand to get popular items
    products = products.sort_values('demand', ascending=False).head(20)
    
    # Add dummy names and categories for demo
    products['product_name'] = products['StockCode'].apply(lambda x: f"Premium {x}")
    products['category'] = 'Essentials'
    products['description'] = 'AI-optimized retail product for maximum performance.'
    products['image_url'] = 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=600'
    products['current_price'] = products['Price'].round(2)
    products['original_price'] = (products['Price'] * 1.2).round(2)
    products['stock'] = 100
    products['active'] = True
    
    # Rename for app.py
    products = products.rename(columns={'StockCode': 'product_id'})
    products['stock_code'] = products['product_id']
    
    # Ensure correct columns
    cols = ['product_id', 'stock_code', 'product_name', 'category', 'description', 'image_url', 'current_price', 'original_price', 'stock', 'active']
    products = products[cols]
    
    products.to_csv('data/products.csv', index=False)
    print("Seeded data/products.csv")

# 2. Seed users.json
users = {
    "users": [
        {
            "user_id": "cust_1",
            "name": "Viraj Wairkar",
            "email": "viraj@gmail.com",
            "password_hash": generate_password_hash("viraj123"),
            "role": "customer",
            "created_at": "2026-05-15T00:00:00"
        }
    ]
}
with open('data/users.json', 'w') as f:
    json.dump(users, f, indent=2)
print("Seeded data/users.json")
