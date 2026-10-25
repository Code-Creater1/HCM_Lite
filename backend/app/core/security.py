import bcrypt
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings
ALGORITHM = "HS256"

def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def verify_password(pw: str, hashed: str) -> bool:
    try: return bcrypt.checkpw(pw.encode(), hashed.encode())
    except Exception: return False

def create_token(user_id: int, role: str) -> str:
    return jwt.encode({
        "sub": str(user_id), "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=settings.jwt_expires_minutes),
        "iat": datetime.utcnow(),
    }, settings.jwt_secret, algorithm=ALGORITHM)

def decode_token(t: str) -> dict:
    return jwt.decode(t, settings.jwt_secret, algorithms=[ALGORITHM])