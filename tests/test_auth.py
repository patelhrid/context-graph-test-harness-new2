"""Tests for src/auth.py"""


def test_generate_and_verify_roundtrip():
    from src.auth import generate_token, verify_token
    token = generate_token(user_id=42)
    payload = verify_token(token)
    assert payload["user_id"] == 42


def test_secret_key_nonempty():
    from src.auth import SECRET_KEY
    assert len(SECRET_KEY) > 0
