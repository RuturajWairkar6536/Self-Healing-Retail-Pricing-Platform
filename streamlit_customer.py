import pandas as pd
import requests
import streamlit as st


st.set_page_config(
    page_title="Smart Store",
    page_icon="🛍️",
    layout="wide",
)

API_URL = "http://127.0.0.1:5001"
SESSION_ID = "customer_session"

st.markdown(
    """
    <style>
    .price {font-size: 1.45rem; font-weight: 700; color: #d9480f;}
    .badge {display: inline-block; padding: .2rem .45rem; border-radius: .35rem; background: #e7f5ff; color: #1864ab; font-size: .78rem;}
    .discount {display: inline-block; padding: .2rem .45rem; border-radius: .35rem; background: #fff4e6; color: #d9480f; font-size: .78rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


def get(path, params=None):
    r = requests.get(f"{API_URL}{path}", params=params, timeout=10)
    r.raise_for_status()
    return r.json()


def post(path, payload):
    r = requests.post(f"{API_URL}{path}", json=payload, timeout=15)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=20)
def products(search="", category="All"):
    params = {}
    if search:
        params["search"] = search
    if category != "All":
        params["category"] = category
    return get("/products", params=params)["products"]


@st.cache_data(ttl=60)
def categories():
    return get("/categories")["categories"]


def cart():
    return get("/cart", {"session": SESSION_ID})


def clear_store_cache():
    products.clear()
    categories.clear()


try:
    get("/health")
except Exception as exc:
    st.error(f"Store is offline. Start the Flask API with `python app.py`. Details: {exc}")
    st.stop()

if "page" not in st.session_state:
    st.session_state.page = "home"
if "product_id" not in st.session_state:
    st.session_state.product_id = None


with st.sidebar:
    st.title("Smart Store")
    st.caption("Live prices powered by the AI optimizer")
    if st.button("Home", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()
    if st.button("Browse", use_container_width=True):
        st.session_state.page = "browse"
        st.rerun()
    current_cart = cart()
    if st.button(f"Cart ({current_cart['total_items']})", use_container_width=True):
        st.session_state.page = "cart"
        st.rerun()
    st.metric("Cart total", f"₹{current_cart['total_price']:.2f}")


def product_card(product, key_prefix):
    st.image(product["image_url"], use_container_width=True)
    st.subheader(product["product_name"])
    st.caption(product["category"])
    price_cols = st.columns([1, 1])
    price_cols[0].markdown(f"<div class='price'>₹{product['current_price']:.2f}</div>", unsafe_allow_html=True)
    if product.get("discount_%", 0) > 0:
        price_cols[1].markdown(f"<span class='discount'>{product['discount_%']:.0f}% off</span>", unsafe_allow_html=True)
    st.markdown("<span class='badge'>AI-updated store price</span>", unsafe_allow_html=True)
    st.write("In stock" if product["stock"] > 0 else "Out of stock")
    b1, b2 = st.columns(2)
    if b1.button("View", key=f"{key_prefix}_view_{product['product_id']}", use_container_width=True):
        st.session_state.product_id = product["product_id"]
        st.session_state.page = "detail"
        st.rerun()
    disabled = product["stock"] <= 0
    if b2.button("Add", key=f"{key_prefix}_add_{product['product_id']}", disabled=disabled, use_container_width=True):
        post("/cart/add", {"session": SESSION_ID, "product_id": product["product_id"], "quantity": 1})
        clear_store_cache()
        st.success("Added to cart.")
        st.rerun()


if st.session_state.page == "home":
    st.title("AI-Powered Smart Ecommerce Pricing Platform")
    st.write("Browse products whose selling prices are controlled by the admin-side AI price optimizer.")
    featured = products()[:4]
    cols = st.columns(4)
    for idx, product in enumerate(featured):
        with cols[idx % 4]:
            product_card(product, "home")


elif st.session_state.page == "browse":
    st.title("Browse Products")
    c1, c2 = st.columns([2, 1])
    search = c1.text_input("Search products")
    category = c2.selectbox("Category", ["All"] + categories())
    results = products(search, category)
    st.caption(f"{len(results)} products found")
    cols = st.columns(3)
    for idx, product in enumerate(results):
        with cols[idx % 3]:
            product_card(product, "browse")


elif st.session_state.page == "detail":
    product_id = st.session_state.product_id
    if not product_id:
        st.session_state.page = "browse"
        st.rerun()
    product = get(f"/product/{product_id}")
    left, right = st.columns([1, 1])
    with left:
        st.image(product["image_url"], use_container_width=True)
    with right:
        st.title(product["product_name"])
        st.caption(product["category"])
        st.markdown(f"<div class='price'>₹{product['current_price']:.2f}</div>", unsafe_allow_html=True)
        if product.get("discount_%", 0) > 0:
            st.markdown(f"<span class='discount'>{product['discount_%']:.0f}% off</span>", unsafe_allow_html=True)
        st.markdown("<span class='badge'>Price applied from AI optimizer</span>", unsafe_allow_html=True)
        st.write(product["description"])
        st.write(f"Stock: {product['stock']}")
        st.caption(f"Latest AI recommendation: ₹{product['ai_recommended_price']:.2f} | Decision: {product['ai_decision']}")
        qty = st.number_input("Quantity", min_value=1, max_value=max(1, int(product["stock"])), value=1, disabled=product["stock"] <= 0)
        if st.button("Add to cart", disabled=product["stock"] <= 0, use_container_width=True):
            post("/cart/add", {"session": SESSION_ID, "product_id": product_id, "quantity": int(qty)})
            st.success("Added to cart.")
            st.rerun()


elif st.session_state.page == "cart":
    st.title("Shopping Cart")
    current_cart = cart()
    if not current_cart["items"]:
        st.info("Your cart is empty.")
    else:
        st.dataframe(pd.DataFrame(current_cart["items"]), use_container_width=True, hide_index=True)
        st.subheader(f"Total: ₹{current_cart['total_price']:.2f}")
        for item in current_cart["items"]:
            if st.button(f"Remove {item['product_name']}", key=f"remove_{item['product_id']}"):
                post("/cart/remove", {"session": SESSION_ID, "product_id": item["product_id"]})
                st.rerun()
        if st.button("Checkout", type="primary", use_container_width=True):
            st.session_state.page = "checkout"
            st.rerun()


elif st.session_state.page == "checkout":
    st.title("Mock Checkout")
    current_cart = cart()
    st.write(f"Items: {current_cart['total_items']}")
    st.write(f"Total: ₹{current_cart['total_price']:.2f}")
    customer_name = st.text_input("Name", value="Guest")
    if st.button("Place order", type="primary", use_container_width=True):
        result = post("/checkout", {"session": SESSION_ID, "customer_name": customer_name})
        clear_store_cache()
        st.success(f"Order placed: {result['order_id']} | Total ₹{result['total_amount']:.2f}")
        st.balloons()
