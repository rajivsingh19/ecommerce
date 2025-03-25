from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta
from auth import encrypt_password, decrypt_password, create_access_token, verify_access_token
from database import get_session, init_db
from models import Product, User,Cart,Order
from fastapi import Form 
from fastapi.security import OAuth2PasswordBearer

init_db()
app = FastAPI()

ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@app.post("/register/")
# def register(username: str, password: str, db: Session = Depends(get_session)):
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_session)):
    existing_user = db.query(User).filter(User.username == username).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    encrypted_password = encrypt_password(password)
    new_user = User(username=username, password=encrypted_password)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/login/")
# def login(username: str, password: str, db: Session = Depends(get_session)):
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_session)):
    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    decrypted_password = decrypt_password(db_user.password)
    if decrypted_password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token({"sub": username}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/protected/")
def protected_route(token: str = Depends(oauth2_scheme)):
    user_data = verify_access_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"message": f"Hello, {user_data['sub']}! You are authenticated."}
@app.get("/products/")
def get_products(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    user_data = verify_access_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    products = db.query(Product).all()
    return products

# ✅ Add product to cart
@app.post("/cart/add/")
def add_to_cart(product_id: int, quantity: int = 1, token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    user_data = verify_access_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == user_data["sub"]).first()
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart_item = db.query(Cart).filter(Cart.user_id == user.id, Cart.product_id == product_id).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        new_cart_item = Cart(user_id=user.id, product_id=product_id,name=product.name,price=product.price, quantity=quantity)
        db.add(new_cart_item)

    db.commit()
    return {"message": "Product added to cart"}

# ✅ View cart
@app.get("/cart/")
def view_cart(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    user_data = verify_access_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == user_data["sub"]).first()
    cart_items = db.query(Cart).filter(Cart.user_id == user.id).all()

    return [{"product_id": item.product_id,"name":item.name,"price":item.price, "quantity": item.quantity} for item in cart_items]

# ✅ Delete product from cart
@app.delete("/cart/remove/")
def remove_from_cart(product_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    user_data = verify_access_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == user_data["sub"]).first()
    cart_item = db.query(Cart).filter(Cart.user_id == user.id, Cart.product_id == product_id).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Product not in cart")

    db.delete(cart_item)
    db.commit()
    return {"message": "Product removed from cart"}

# ✅ Place order
@app.post("/orders/place/")
def place_order(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    user_data = verify_access_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == user_data["sub"]).first()
    cart_items = db.query(Cart).filter(Cart.user_id == user.id).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    for item in cart_items:
        new_order = Order(user_id=user.id, product_id=item.product_id,name=item.name,price=item.price, quantity=item.quantity)
        db.add(new_order)
        db.delete(item)  # Remove from cart after ordering

    db.commit()
    return {"message": "Order placed successfully"}

# ✅ Order history
@app.get("/orders/history/")
def order_history(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    user_data = verify_access_token(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == user_data["sub"]).first()
    orders = db.query(Order).filter(Order.user_id == user.id).all()

    return [{"product_id": order.product_id,"name":order.name,"price":order.price, "quantity": order.quantity, "date": order.order_date} for order in orders]

