import sys
from unittest.mock import patch

import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

sys.path.insert(0, "backend")

import dependencies


def test_get_current_user_returns_active_user():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid-token",
    )

    with patch(
        "dependencies.auth.decode_access_token",
        return_value={"sub": "7"},
    ), patch(
        "dependencies.persistence.get_user_by_id",
        return_value={
            "id": 7,
            "username": "admin",
            "email": "admin@example.com",
            "password_hash": "hashed-password",
            "is_active": True,
        },
    ):
        result = dependencies.get_current_user(credentials)

    assert result["id"] == 7
    assert result["username"] == "admin"


def test_get_current_user_rejects_invalid_token():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="invalid-token",
    )

    with patch(
        "dependencies.auth.decode_access_token",
        side_effect=jwt.InvalidTokenError,
    ):
        with pytest.raises(HTTPException) as exc_info:
            dependencies.get_current_user(credentials)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication credentials"


def test_get_current_user_rejects_missing_user():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid-token",
    )

    with patch(
        "dependencies.auth.decode_access_token",
        return_value={"sub": "999"},
    ), patch(
        "dependencies.persistence.get_user_by_id",
        return_value=None,
    ):
        with pytest.raises(HTTPException) as exc_info:
            dependencies.get_current_user(credentials)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authentication credentials"


def test_require_permission_allows_user_with_permission():
    dependency = dependencies.require_permission("sensor.view")
    user = {
        "id": 7,
        "username": "admin",
        "email": "admin@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }

    with patch(
        "dependencies.persistence.get_user_permissions",
        return_value={"sensor.view", "actuator.control"},
    ):
        result = dependency(user)

    assert result == user


def test_require_permission_rejects_user_without_permission():
    dependency = dependencies.require_permission("actuator.control")
    user = {
        "id": 7,
        "username": "viewer",
        "email": "viewer@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }

    with patch(
        "dependencies.persistence.get_user_permissions",
        return_value={"sensor.view"},
    ):
        with pytest.raises(HTTPException) as exc_info:
            dependency(user)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Forbidden"


def test_require_permission_fails_closed_when_permission_store_unavailable():
    dependency = dependencies.require_permission("sensor.view")
    user = {
        "id": 7,
        "username": "operator",
        "email": "operator@example.com",
        "password_hash": "hashed-password",
        "is_active": True,
    }

    with patch(
        "dependencies.persistence.get_user_permissions",
        side_effect=RuntimeError("simulated permission store failure"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            dependency(user)

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "Authorization service unavailable"

def test_get_current_user_fails_closed_when_user_store_unavailable():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials="valid-token",
    )

    with patch(
        "dependencies.auth.decode_access_token",
        return_value={"sub": "7"},
    ), patch(
        "dependencies.persistence.get_user_by_id",
        side_effect=RuntimeError("simulated database failure"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            dependencies.get_current_user(credentials)

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "Authentication service unavailable"
