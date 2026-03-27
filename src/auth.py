"""Authentication: JWT token generation and verification."""

import jwt
import datetime

SECRET_KEY = "rotated-secret-key-v2"
TOKEN_TTL_HOURS = 1


def generate_token(user_id: int) -> str:
    """Generate a signed JWT for the given user."""
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=TOKEN_TTL_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def verify_token(token: str) -> dict:
    """Decode and verify a JWT. Raises on expiry or bad signature."""
    return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
