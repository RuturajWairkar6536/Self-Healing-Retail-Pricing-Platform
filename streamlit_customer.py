"""
streamlit_customer.py
Customer-facing e-commerce store
Integrated with AI pricing optimizer
"""

import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# ====================
# Config
# ====================

st.set_page_config(
    page_title="Smart Store - AI Pricing",
    page_icon="🛍️",
    layout="wide"
)

API_URL = "http://127.0.0.1:5001"
SESSION_ID = "customer_session"

# Custom CSS
st.markdown("""
<style>
    .product-card {
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #ddd;
        text-align: center;
    }
    .ai-badge {
        background-color: #4CAF50;
        color: white;
        padding: 5px 10px;
        border-radius: 5px;
        font-size: 0.8em;
    }
    .price-badge {
        font-size: 1.5em;
        font-weight: bold;
        color: #FF6B35;
    }
</style>
""", unsafe_allow_html=True)

# ====================
# API Calls
# ====================

@st.cache_data(ttl=300)
def get_products():
    try:
        r = requests.get(f"{API_URL}/products", timeout=5)
        return r.json()["products"] if r.status_code == 200 else []
    except:
        return []


@st.cache_data(ttl=300)
def get_categories():
    try:
        r = requests.get(f"{API_URL}/categories", timeout=5)
        return r.json()["categories"] if r.status_code == 200 else []
    except:
        return []


def get_product_detail(product_id):
    try:
        r = requests.get(f"{API_URL}/product/{product_id}", timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None


def get_cart():
    try:
        r = requests.get(f"{API_URL}/cart?session={SESSION_ID}", timeout=5)
        return r.json() if r.status_code == 200 else None
    except:
        return None


def add_to_cart_api(product_id, quantity, price):
    try:
        r = requests.post(f"{API_URL}/cart/add", json={
            "product_id": product_id,
            "quantity": quantity,
            "price": price,
            "session": SESSION_ID
        }, timeout=5)
        return r.status_code == 200
    except:
        return False


def remove_from_cart_api(product_id):
    try:
        r = requests.post(f"{API_URL}/cart/remove", json={
            "product_id": product_id,
            "session": SESSION_ID
        }, timeout=5)
        return r.status_code == 200
    except:
        return False


def checkout_api(customer_name):
    try:
        r = requests.post(f"{API_URL}/checkout", json={
            "session": SESSION_ID,
            "customer_name": customer_name
        }, timeout=5)
        return r.status_code == 200, r.json()
    except Exception as e:
        return False, {"error": str(e)}


# ====================
# Check API
# ====================

try:
    r = requests.get(f"{API_URL}/health", timeout=3)
    api_online = r.status_code == 200
except:
    api_online = False

if not api_online:
    st.error("🔴 API is offline! Run `python app.py` first")
    st.stop()

# ====================
# Session State
# ====================

if "page" not in st.session_state:
    st.session_state.page = "home"

# ====================
# Sidebar
# ====================

with st.sidebar:
    st.title("🛍️ Smart Store")
    st.markdown("AI-Powered Dynamic Pricing")
    st.markdown("---")
    
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    
    if st.button("📦 Browse", use_container_width=True):
        st.session_state.page = "browse"
        st.rerun()
    
    if st.button("🛒 Cart", use_container_width=True):
        st.session_state.page = "cart"
        st.rerun()
    
    st.markdown("---")
    
    cart = get_cart()
    if cart:
        st.metric("🛒 Items", cart["total_items"])
        st.metric("💰 Total", f"₹{cart['total_price']:.2f}")

# ====================
# Page: Home
# ====================

if st.session_state.page == "home":
    st.markdown("# 🛍️ Welcome to Smart Store")
    st.markdown("### AI-Powered E-commerce with Dynamic Pricing")
    
    st.write("Our store uses AI to optimize prices in real-time based on demand, ensuring you get the best prices!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💫 Smart Pricing", "AI Optimized")
    with col2:
        st.metric("📊 Real-time", "Dynamic")
    with col3:
        st.metric("✨ Best Deals", "Guaranteed")
    
    st.markdown("---")
    
    st.subheader("🌟 Featured Products")
    
    products = get_products()
    if products:
        featured = products[:3]
        cols = st.columns(3)
        
        for idx, product in enumerate(featured):
            with cols[idx]:
                st.image(product.get("image_url", "https://via.placeholder.com/200"), use_column_width=True)
                st.write(f"### {product['product_name']}")
                
                col_price, col_ai = st.columns(2)
                with col_price:
                    st.markdown(f"<div class='price-badge'>₹{product['current_price']}</div>", unsafe_allow_html=True)
                with col_ai:
                    st.markdown(f"<div class='ai-badge'>AI Price</div>", unsafe_allow_html=True)
                
                if st.button("👁️ View", key=f"featured_{product['product_id']}", use_container_width=True):
                    st.session_state.product = product['product_id']
                    st.session_state.page = "product"
                    st.rerun()

# ====================
# Page: Browse Products
# ====================

elif st.session_state.page == "browse":
    st.subheader("📦 Products")
    
    col1, col2 = st.columns(2)
    
    with col1:
        search = st.text_input("🔍 Search", placeholder="Search products...")
    
    with col2:
        categories = get_categories()
        selected_category = st.selectbox("📂 Category", ["All"] + categories)
    
    products = get_products()
    
    if search:
        products = [p for p in products if search.lower() in p["product_name"].lower()]
    
    if selected_category != "All":
        products = [p for p in products if p["category"] == selected_category]
    
    st.write(f"Found {len(products)} products")
    
    cols = st.columns(3)
    for idx, product in enumerate(products):
        col = cols[idx % 3]
        
        with col:
            st.image(product.get("image_url", "https://via.placeholder.com/200"), use_column_width=True)
            st.write(f"**{product['product_name']}**")
            st.caption(product["category"])
            
            col_price, col_stock = st.columns(2)
            with col_price:
                st.markdown(f"₹**{product['current_price']}**")
            with col_stock:
                st.write(f"Stock: {product['stock']}")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("👁️ View", key=f"view_{product['product_id']}", use_container_width=True):
                    st.session_state.product = product['product_id']
                    st.session_state.page = "product"
                    st.rerun()
            
            with col_btn2:
                if product["stock"] > 0:
                    if st.button("🛒 Add", key=f"add_{product['product_id']}", use_container_width=True):
                        if add_to_cart_api(product['product_id'], 1, product['current_price']):
                            st.success("✅ Added to cart!")
                        else:
                            st.error("❌ Failed to add")
                else:
                    st.button("Out of Stock", disabled=True, use_container_width=True)

# ====================
# Page: Product Detail
# ====================

elif st.session_state.page == "product":
    if "product" in st.session_state:
        product = get_product_detail(st.session_state.product)
        
        if product:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.image(product.get("image_url", "https://via.placeholder.com/300"), use_column_width=True)
            
            with col2:
                st.title(product['product_name'])
                st.caption(f"Category: {product['category']}")
                
                st.markdown("---")
                
                # AI Pricing Section
                st.subheader("💰 Smart Pricing")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Current Price", f"₹{product['current_price']}")
                with col_b:
                    st.metric("AI Price", f"₹{product.get('ai_price', product['current_price'])}")
                
                st.info("✨ Our AI analyzes demand trends to give you the best price!")
                
                st.markdown("---")
                
                # Stock & Description
                if product["stock"] > 0:
                    st.success(f"✅ {product['stock']} in stock")
                else:
                    st.error("❌ Out of stock")
                
                st.write(product["description"])
                
                st.markdown("---")
                
                # Add to cart
                if product["stock"] > 0:
                    qty = st.number_input("Quantity", min_value=1, max_value=product["stock"], value=1)
                    
                    if st.button("🛒 Add to Cart", use_container_width=True):
                        if add_to_cart_api(product['product_id'], qty, product['current_price']):
                            st.success(f"✅ Added {qty} to cart!")
                        else:
                            st.error("Failed to add to cart")
                
                if st.button("🔙 Back to Browse", use_container_width=True):
                    st.session_state.page = "browse"
                    st.rerun()

# ====================
# Page: Cart
# ====================

elif st.session_state.page == "cart":
    st.subheader("🛒 Shopping Cart")
    
    cart = get_cart()
    if not cart or not cart["items"]:
        st.info("Your cart is empty")
    else:
        st.write(f"**Items in cart:** {cart['total_items']}")
        
        # Display items
        items_data = []
        for item in cart["items"]:
            product = get_product_detail(item['product_id'])
            if product:
                items_data.append({
                    "Product": product['product_name'],
                    "Qty": item['quantity'],
                    "Price": f"₹{item['price']:.2f}",
                    "Total": f"₹{(item['quantity'] * item['price']):.2f}"
                })
        
        if items_data:
            st.dataframe(pd.DataFrame(items_data), use_container_width=True)
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f"### Total: ₹{cart['total_price']:.2f}")
        
        with col2:
            if st.button("✅ Checkout", use_container_width=True):
                st.session_state.page = "checkout"
                st.rerun()

# ====================
# Page: Checkout
# ====================

elif st.session_state.page == "checkout":
    st.subheader("✅ Checkout")
    
    customer_name = st.text_input("Your Name")
    
    cart = get_cart()
    if cart:
        st.markdown("---")
        st.subheader("Order Summary")
        st.write(f"**Items:** {cart['total_items']}")
        st.write(f"**Total:** ₹{cart['total_price']:.2f}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Place Order", use_container_width=True):
                if not customer_name:
                    st.error("Please enter your name")
                else:
                    success, result = checkout_api(customer_name)
                    if success:
                        st.success(f"✅ Order placed! Order ID: {result['order_id']}")
                        st.balloons()
                        if st.button("🏠 Back to Home"):
                            st.session_state.page = "home"
                            st.rerun()
                    else:
                        st.error(f"❌ Checkout failed: {result.get('error')}")
        
        with col2:
            if st.button("🔙 Back to Cart", use_container_width=True):
                st.session_state.page = "cart"
                st.rerun()
