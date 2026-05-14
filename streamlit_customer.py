import os
from html import escape

import pandas as pd
import requests
import streamlit as st
from requests import HTTPError


st.set_page_config(
    page_title="Smart Store",
    page_icon="🛍️",
    layout="wide",
)

API_URL = os.environ.get("STORE_API_URL", "http://pricing-api:5001").rstrip("/")

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
        --warm: #b86b3f;
        --warm-soft: #fff0e8;
        --line: #dde7e2;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(255, 240, 232, 0.9), transparent 32rem),
            linear-gradient(180deg, #fbfaf7 0%, #edf6f2 100%);
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

    [data-testid="stSidebar"] {
        background: #f2f8f5;
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] h1 {
        font-size: 1.4rem;
        margin-bottom: .15rem;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--line);
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.9);
        box-shadow: 0 12px 34px rgba(44, 81, 76, 0.08);
    }

    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #a9d4cb;
        box-shadow: 0 18px 44px rgba(44, 81, 76, 0.13);
        transform: translateY(-1px);
        transition: all .18s ease;
    }

    .store-hero {
        min-height: 250px;
        display: flex;
        align-items: flex-end;
        padding: 2rem;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.65);
        background-size: cover;
        background-position: center;
        box-shadow: 0 22px 54px rgba(30, 69, 63, 0.18);
        overflow: hidden;
        margin-bottom: 1.4rem;
    }

    .store-hero-content {
        max-width: 680px;
        color: #ffffff;
        text-shadow: 0 1px 18px rgba(17, 38, 35, .35);
    }

    .store-eyebrow {
        display: inline-block;
        margin-bottom: .75rem;
        padding: .28rem .6rem;
        border: 1px solid rgba(255, 255, 255, .58);
        border-radius: 999px;
        background: rgba(255, 255, 255, .18);
        font-size: .78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: .08em;
    }

    .store-hero h1 {
        color: #ffffff;
        margin: 0 0 .45rem;
        font-size: clamp(2rem, 4vw, 3.5rem);
        line-height: 1.04;
    }

    .store-hero p {
        margin: 0;
        max-width: 580px;
        font-size: 1.05rem;
        line-height: 1.6;
    }

    .section-heading {
        display: flex;
        align-items: end;
        justify-content: space-between;
        gap: 1rem;
        margin: 1.25rem 0 .75rem;
        padding-bottom: .75rem;
        border-bottom: 1px solid var(--line);
    }

    .section-heading h2 {
        margin: 0;
        font-size: 1.5rem;
    }

    .section-heading p {
        margin: .25rem 0 0;
        color: var(--muted);
    }

    .soft-panel {
        padding: 1.35rem;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: rgba(255, 255, 255, .88);
        box-shadow: 0 14px 34px rgba(44, 81, 76, .08);
        margin-bottom: 1rem;
    }

    .login-panel {
        max-width: 760px;
        margin: 0 auto;
    }

    .product-name {
        min-height: 3rem;
        margin: .85rem 0 .15rem;
        font-size: 1.06rem;
        font-weight: 750;
        line-height: 1.35;
        color: #20302d;
    }

    .product-category {
        color: var(--muted);
        font-size: .86rem;
        margin-bottom: .5rem;
    }

    .product-desc {
        min-height: 3.25rem;
        margin: .55rem 0 .75rem;
        color: #5c6d68;
        font-size: .9rem;
        line-height: 1.45;
    }

    .product-image-frame {
        width: 100%;
        aspect-ratio: 1 / 1;
        overflow: hidden;
        border-radius: 8px;
        border: 1px solid var(--line);
        background: #f7faf8;
    }

    .product-image-frame img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }

    .product-detail-image {
        aspect-ratio: 4 / 3;
    }

    .price {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1f6f66;
    }

    .badge {
        display: inline-block;
        padding: .24rem .5rem;
        border-radius: .35rem;
        background: var(--accent-soft);
        color: #1f6f66;
        font-size: .78rem;
    }

    .discount {
        display: inline-block;
        padding: .24rem .5rem;
        border-radius: .35rem;
        background: var(--warm-soft);
        color: var(--warm);
        font-size: .78rem;
    }

    .stock-note {
        color: var(--muted);
        font-size: .92rem;
        margin: .35rem 0 .5rem;
    }

    .cart-total {
        padding: 1rem;
        border-radius: 8px;
        background: #20302d;
        color: #ffffff;
        margin: .75rem 0 1rem;
    }

    .cart-total strong {
        display: block;
        font-size: 1.55rem;
        margin-top: .2rem;
    }

    .stButton > button {
        border-radius: 8px;
        border-color: #b8d9d2;
        min-height: 2.65rem;
        font-weight: 650;
    }

    .stButton > button[kind="primary"] {
        background: #2f8f83;
        border-color: #2f8f83;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def get(path, params=None):
    r = requests.get(f"{API_URL}{path}", params=params, timeout=10)
    handle_api_error(r)
    return r.json()


def post(path, payload):
    r = requests.post(f"{API_URL}{path}", json=payload, timeout=15)
    handle_api_error(r)
    return r.json()


def handle_api_error(response):
    try:
        response.raise_for_status()
    except HTTPError as exc:
        try:
            detail = response.json().get("error", str(exc))
        except ValueError:
            detail = response.text or str(exc)
        raise RuntimeError(detail) from exc


def current_session_id():
    user_id = st.session_state.get("user_id")
    return f"user_{user_id}" if user_id else "anonymous"


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
    return get("/cart", {"session": current_session_id()})


def clear_store_cache():
    products.clear()
    categories.clear()


def product_image(image_url, alt_text, detail=False):
    frame_class = "product-image-frame product-detail-image" if detail else "product-image-frame"
    safe_url = escape(str(image_url or ""), quote=True)
    safe_alt = escape(str(alt_text or "Product image"), quote=True)
    st.markdown(
        f"<div class='{frame_class}'><img src='{safe_url}' alt='{safe_alt}' loading='lazy'></div>",
        unsafe_allow_html=True,
    )


def hero(title, subtitle, eyebrow, image_url):
    safe_title = escape(title)
    safe_subtitle = escape(subtitle)
    safe_eyebrow = escape(eyebrow)
    safe_url = escape(image_url, quote=True)
    st.markdown(
        f"""
        <div class="store-hero" style="background-image:
            linear-gradient(90deg, rgba(24, 50, 47, .86), rgba(24, 50, 47, .48), rgba(24, 50, 47, .14)),
            url('{safe_url}');">
            <div class="store-hero-content">
                <span class="store-eyebrow">{safe_eyebrow}</span>
                <h1>{safe_title}</h1>
                <p>{safe_subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(title, subtitle):
    st.markdown(
        f"""
        <div class="section-heading">
            <div>
                <h2>{escape(title)}</h2>
                <p>{escape(subtitle)}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


try:
    get("/health")
except Exception as exc:
    st.error(f"Store is offline. Start the Flask API with `python app.py`. Details: {exc}")
    st.stop()

if "page" not in st.session_state:
    st.session_state.page = "login"
if "product_id" not in st.session_state:
    st.session_state.product_id = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

if not st.session_state.user_id and st.session_state.page != "login":
    st.session_state.page = "login"


with st.sidebar:
    st.title("Smart Store")
    st.caption("AI-priced essentials")
    
    # Show user info if logged in
    if st.session_state.user_id:
        st.success(f"Signed in as {st.session_state.user_name}")
        st.caption(st.session_state.user_email)
        if st.button("Logout", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.session_state.user_email = None
            st.session_state.product_id = None
            st.session_state.page = "login"
            st.rerun()
        st.divider()
        
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
    else:
        st.info("Please login to shop")


def product_card(product, key_prefix):
    with st.container(border=True):
        product_image(product["image_url"], product["product_name"])
        st.markdown(f"<div class='product-name'>{escape(product['product_name'])}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='product-category'>{escape(product['category'])}</div>", unsafe_allow_html=True)
        price_cols = st.columns([1, 1])
        price_cols[0].markdown(f"<div class='price'>₹{product['current_price']:.2f}</div>", unsafe_allow_html=True)
        if product.get("discount_%", 0) > 0:
            price_cols[1].markdown(f"<span class='discount'>{product['discount_%']:.0f}% off</span>", unsafe_allow_html=True)
        st.markdown("<span class='badge'>AI-updated store price</span>", unsafe_allow_html=True)
        desc = str(product.get("description", ""))
        if len(desc) > 92:
            desc = f"{desc[:89]}..."
        st.markdown(f"<div class='product-desc'>{escape(desc)}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='stock-note'>{'In stock' if product['stock'] > 0 else 'Out of stock'}</div>",
            unsafe_allow_html=True,
        )
        b1, b2 = st.columns(2)
        if b1.button("View", key=f"{key_prefix}_view_{product['product_id']}", use_container_width=True):
            st.session_state.product_id = product["product_id"]
            st.session_state.page = "detail"
            st.rerun()
        disabled = product["stock"] <= 0
        if b2.button("Add", key=f"{key_prefix}_add_{product['product_id']}", disabled=disabled, use_container_width=True):
            post("/cart/add", {"session": current_session_id(), "product_id": product["product_id"], "quantity": 1})
            clear_store_cache()
            st.success("Added to cart.")
            st.rerun()


if st.session_state.page == "login":
    hero(
        "Smart Store",
        "A calmer shopping experience with live prices, curated essentials, and a clean checkout flow.",
        "Welcome",
        "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1600&h=700&fit=crop&q=80",
    )
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.container(border=True):
            st.subheader("Login")
            login_email = st.text_input("Email", key="login_email", placeholder="your@email.com")
            login_password = st.text_input("Password", key="login_password", type="password")
            if st.button("Login", type="primary", use_container_width=True):
                if not login_email or not login_password:
                    st.error("Please enter your email and password")
                else:
                    try:
                        response = post("/user/login", {"email": login_email, "password": login_password})
                        st.session_state.user_id = response["user_id"]
                        st.session_state.user_name = response["name"]
                        st.session_state.user_email = response["email"]
                        st.success(f"Welcome back, {response['name']}!")
                        st.session_state.page = "home"
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
    
    with tab2:
        with st.container(border=True):
            st.subheader("Register")
            reg_name = st.text_input("Full Name", key="reg_name", placeholder="Your Name")
            reg_email = st.text_input("Email", key="reg_email", placeholder="your@email.com")
            reg_password = st.text_input("Password", key="reg_password", type="password", help="Minimum 6 characters")
            if st.button("Register", type="primary", use_container_width=True):
                if not reg_name or not reg_email or not reg_password:
                    st.error("Please fill in all fields")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    try:
                        response = post("/user/register", {"name": reg_name, "email": reg_email, "password": reg_password})
                        st.session_state.user_id = response["user_id"]
                        st.session_state.user_name = response["name"]
                        st.session_state.user_email = response["email"]
                        st.success(f"Welcome {response['name']}! Registration successful!")
                        st.session_state.page = "home"
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))


elif st.session_state.page == "home":
    featured = products()[:4]
    hero(
        "Shop Smarter",
        "Discover everyday products with prices refreshed by the AI pricing engine.",
        "Featured today",
        featured[0]["image_url"] if featured else "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1600&h=700&fit=crop&q=80",
    )
    section_heading("Featured Products", "A quick look at products with live store pricing.")
    cols = st.columns(4, gap="large")
    for idx, product in enumerate(featured):
        with cols[idx % 4]:
            product_card(product, "home")


elif st.session_state.page == "browse":
    hero(
        "Browse Products",
        "Search the catalog, compare AI-updated prices, and add items without leaving the page.",
        "Catalog",
        "https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=1600&h=700&fit=crop&q=80",
    )
    c1, c2 = st.columns([2, 1])
    search = c1.text_input("Search products")
    category = c2.selectbox("Category", ["All"] + categories())
    results = products(search, category)
    section_heading("All Products", f"{len(results)} products found")
    for idx, product in enumerate(results):
        if idx % 3 == 0:
            cols = st.columns(3, gap="large")
        with cols[idx % 3]:
            product_card(product, "browse")


elif st.session_state.page == "detail":
    product_id = st.session_state.product_id
    if not product_id:
        st.session_state.page = "browse"
        st.rerun()
    product = get(f"/product/{product_id}")
    section_heading(product["product_name"], product["category"])
    left, right = st.columns([1, 1])
    with left:
        product_image(product["image_url"], product["product_name"], detail=True)
    with right:
        with st.container(border=True):
            st.markdown(f"<div class='price'>₹{product['current_price']:.2f}</div>", unsafe_allow_html=True)
            if product.get("discount_%", 0) > 0:
                st.markdown(f"<span class='discount'>{product['discount_%']:.0f}% off</span>", unsafe_allow_html=True)
            st.markdown("<span class='badge'>Price applied from AI optimizer</span>", unsafe_allow_html=True)
            st.write(product["description"])
            st.write(f"Stock: {product['stock']}")
            st.caption(f"Latest AI recommendation: ₹{product['ai_recommended_price']:.2f} | Decision: {product['ai_decision']}")
            qty = st.number_input("Quantity", min_value=1, max_value=max(1, int(product["stock"])), value=1, disabled=product["stock"] <= 0)
            if st.button("Add to cart", disabled=product["stock"] <= 0, use_container_width=True):
                post("/cart/add", {"session": current_session_id(), "product_id": product_id, "quantity": int(qty)})
                st.success("Added to cart.")
                st.rerun()


elif st.session_state.page == "cart":
    section_heading("Shopping Cart", "Review your items before checkout.")
    current_cart = cart()
    if not current_cart["items"]:
        st.info("Your cart is empty.")
    else:
        st.dataframe(pd.DataFrame(current_cart["items"]), use_container_width=True, hide_index=True)
        st.markdown(
            f"<div class='cart-total'>Cart total<strong>₹{current_cart['total_price']:.2f}</strong></div>",
            unsafe_allow_html=True,
        )
        for item in current_cart["items"]:
            if st.button(f"Remove {item['product_name']}", key=f"remove_{item['product_id']}"):
                post("/cart/remove", {"session": current_session_id(), "product_id": item["product_id"]})
                st.rerun()
        if st.button("Checkout", type="primary", use_container_width=True):
            st.session_state.page = "checkout"
            st.rerun()


elif st.session_state.page == "checkout":
    section_heading("Checkout", "Confirm delivery details and complete your order.")
    current_cart = cart()
    
    # Show order summary
    st.subheader("Order Summary")
    st.write(f"**Items**: {current_cart['total_items']}")
    st.write(f"**Total**: ₹{current_cart['total_price']:.2f}")
    st.dataframe(pd.DataFrame(current_cart["items"]), use_container_width=True, hide_index=True)
    
    st.divider()
    
    # Show user info (pre-filled)
    st.subheader("Delivery Details")
    st.write(f"**Name**: {st.session_state.user_name}")
    st.write(f"**Email**: {st.session_state.user_email}")
    
    # Optional: Collect address
    address = st.text_area("Delivery Address", placeholder="Street address, City, State, Postal Code")
    
    st.divider()
    
    if st.button("Complete Purchase", type="primary", use_container_width=True):
        if not address:
            st.error("Please enter delivery address")
        else:
            try:
                result = post("/checkout", {
                    "session": current_session_id(),
                    "customer_name": st.session_state.user_name,
                    "customer_email": st.session_state.user_email
                })
                clear_store_cache()
                st.success(f"✅ Order Placed Successfully!")
                st.info(f"**Order ID**: {result['order_id']}\n\n**Total**: ₹{result['total_amount']:.2f}\n\n**Items**: {result['items_count']}")
                st.write(f"Confirmation email sent to: {st.session_state.user_email}")
                st.balloons()
                st.session_state.page = "home"
            except Exception as e:
                st.error(f"Checkout failed: {str(e)}")
