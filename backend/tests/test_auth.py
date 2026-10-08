import sys
from datetime import datetime, timezone

import jwt
import pytest

sys.path.insert(0, "backend")

import auth


def test_hash_and_verify_password():
    password = "SmartFarm-Test-Password"
    hashed = auth.hash_password(password)

    assert hashed != password
    assert auth.verify_password(password, hashed)
    assert not auth.verify_password("wrong-password", hashed)


def test_create_and_decode_access_token():
    token = auth.create_access_token("user-42")

    payload = auth.decode_access_token(token)

    assert payload["sub"] == "user-42"
    assert "exp" in payload
    assert payload["exp"] > datetime.now(timezone.utc).timestamp()


def test_decode_access_token_rejects_invalid_token():
    with pytest.raises(jwt.InvalidTokenError):
        auth.decode_access_token("invalid-token")
