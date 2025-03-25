import os
import jwt
from datetime import datetime, timedelta
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import base64

# OAuth2 Token Authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# RSA Key Paths
PRIVATE_KEY_FILE = "private_key.pem"
PUBLIC_KEY_FILE = "public_key.pem"

# Generate keys if missing
if not os.path.exists(PRIVATE_KEY_FILE) or not os.path.exists(PUBLIC_KEY_FILE):
    print("🔑 Generating RSA keys...")
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    with open(PRIVATE_KEY_FILE, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    public_key = private_key.public_key()
    with open(PUBLIC_KEY_FILE, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

# Load RSA keys
with open(PRIVATE_KEY_FILE, "rb") as f:
    PRIVATE_KEY = serialization.load_pem_private_key(f.read(), password=None)

with open(PUBLIC_KEY_FILE, "rb") as f:
    PUBLIC_KEY = serialization.load_pem_public_key(f.read())

# Encrypt Password
def encrypt_password(password: str) -> str:
    encrypted_bytes = PUBLIC_KEY.encrypt(
        password.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    encrypted_b64 = base64.b64encode(encrypted_bytes).decode()
    print(f"🔐 Encrypted Password (Base64): {encrypted_b64}")  # Debugging
    return encrypted_b64

    # return base64.b64encode(encrypted_bytes).decode()  # Convert bytes to string before storing


# Decrypt Password

def decrypt_password(encrypted_password: str) -> str:
    encrypted_password_bytes = base64.b64decode(encrypted_password)  # Convert string back to bytes

    return PRIVATE_KEY.decrypt(
        encrypted_password_bytes,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    ).decode()
    print(f"🔓 Decrypted Password: {decrypted_password}")  # Debugging
        
    

# JWT Authentication
SECRET_KEY = "supersecret"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_access_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

