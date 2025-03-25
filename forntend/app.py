import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

st.title("Product Dashboard")

# ✅ Initialize session state variables if not set
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "token" not in st.session_state:
    st.session_state["token"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

def login_page():
    st.subheader("🔑 Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    
    if st.button("Login"):
        response = requests.post(f"{BASE_URL}/login/", data={"username": username, "password": password})
        
        if response.status_code == 200:
            st.session_state["token"] = response.json()["access_token"]
            st.session_state["username"] = username
            st.session_state["logged_in"] = True
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid credentials")

def signup_page():
    st.subheader("📝 Signup")
    new_username = st.text_input("Username", key="signup_username")
    new_password = st.text_input("Password", type="password", key="signup_password")
    
    if st.button("Register"):
        response = requests.post(f"{BASE_URL}/register/", data={"username": new_username, "password": new_password})
        
        if response.status_code == 200:
            st.success("✅ Registration successful! Please log in.")
        else:
            st.error("❌ Username already exists or another error occurred.")

def logout():
    st.session_state["token"] = None
    st.session_state["username"] = None
    st.session_state["logged_in"] = False
    st.success("✅ Logged out successfully!")
    st.rerun()

def get_products():
    st.subheader("🛒 Product List")
    
    response = requests.get(f"{BASE_URL}/products/", headers={"Authorization": f"Bearer {st.session_state['token']}"})
    
    if response.status_code == 200:
        products = response.json()
        if products:
            for product in products:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{product['name']}** - ${product['price']}")
                with col2:
                    if st.button(f"🛒 Add {product['name']}", key=f"add_{product['id']}"):
                        add_to_cart(product['id'])
        else:
            st.info("ℹ️ No products available.")
    else:
        st.error("❌ Failed to fetch products. You may not be authorized.")

def add_to_cart(product_id, quantity=1):
    response = requests.post(
        f"{BASE_URL}/cart/add/",
        params={"product_id": product_id, "quantity": quantity},
        headers={"Authorization": f"Bearer {st.session_state['token']}"}
    )
    if response.status_code == 200:
        st.success("🛒 Product added to cart")
    else:
        st.error("❌ Failed to add product")

def view_cart():
    st.subheader("🛒 Your Cart")
    response = requests.get(
        f"{BASE_URL}/cart/",
        headers={"Authorization": f"Bearer {st.session_state['token']}"}
    )
    if response.status_code == 200:
        cart_items = response.json()
        total_price = 0
        for item in cart_items:
            st.write(f"🎁 {item['name']} | Quantity: {item['quantity']} | Price: ${item['price']} each")
            # total_price += item['price'] * item['quantity']
            # st.write("Cart Items Response:", cart_items)

        st.write(f"**Total Price: ${total_price}**")
    else:
        st.error("❌ Failed to load cart")

def place_order():
    response = requests.post(
        f"{BASE_URL}/orders/place/",
        headers={"Authorization": f"Bearer {st.session_state['token']}"}
    )
    if response.status_code == 200:
        st.success("✅ Order placed successfully!")
    else:
        st.error("❌ Failed to place order")

def order_history():
    st.subheader("📜 Order History")
    response = requests.get(
        f"{BASE_URL}/orders/history/",
        headers={"Authorization": f"Bearer {st.session_state['token']}"}
    )
    if response.status_code == 200:
        orders = response.json()
        for order in orders:
            st.write(f"🎁 {order['name']} | Quantity: {order['quantity']} | Price: ${order['price']} ")
    else:
        st.error("❌ Failed to load orders")

if not st.session_state["logged_in"]:
    option = st.sidebar.radio("🔹 Choose an option", ["Login", "Signup"])
    if option == "Login":
        login_page()
    else:
        signup_page()
else:
    st.sidebar.subheader(f"Welcome, {st.session_state['username']} 👋")
    page = st.sidebar.radio("🔍 Navigation", ["Dashboard", "Products", "Cart", "Order History"])
    if st.sidebar.button("Logout ❌"):
        logout()
    if page == "Dashboard":
        st.header("📊 Dashboard - Protected Route")
        response = requests.get(f"{BASE_URL}/protected/", headers={"Authorization": f"Bearer {st.session_state['token']}"})
        if response.status_code == 200:
            st.write(response.json())
        else:
            st.error("❌ Authentication failed")
    elif page == "Products":
        get_products()
    elif page == "Cart":
        view_cart()
        if st.button("Place Order ✅"):
            place_order()
    elif page == "Order History":
        order_history()
