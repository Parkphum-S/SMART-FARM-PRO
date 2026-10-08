from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

import auth_config


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(subject: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=auth_config.JWT_EXPIRE_MINUTES
    )
    payload = {
        "sub": subject,
        "exp": expires_at,
    }
    return jwt.encode(
        payload,
        auth_config.JWT_SECRET,
        algorithm=auth_config.JWT_ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        auth_config.JWT_SECRET,
        algorithms=[auth_config.JWT_ALGORITHM],
    )
