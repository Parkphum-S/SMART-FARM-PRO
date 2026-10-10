import sys
from unittest.mock import patch

import pytest
from fastapi import HTTPException

sys.path.insert(0, "backend")

import dependencies
import persistence


def test_get_farm_user_permissions_queries_farm_scoped_roles():
    with patch("persistence.db.connect") as connect:
        cursor = (
            connect.return_value.__enter__.return_value
            .cursor.return_value.__enter__.return_value
        )
        cursor.fetchall.return_value = [
            ("sensor.view",),
            ("report.view",),
        ]

        result = persistence.get_farm_user_permissions(7, "farm_001")

    assert result == {"sensor.view", "report.view"}
    query, params = cursor.execute.call_args.args
    assert "app.farm_user_roles" in query or "farm_user_roles" in query
    assert "WHERE f.farm_code = %s" in query
    assert "r.name = 'Super Admin'" in query
    assert params == ("farm_001", 7, 7)


def test_get_farm_user_permissions_returns_empty_set_without_grants():
    with patch("persistence.db.connect") as connect:
        cursor = (
            connect.return_value.__enter__.return_value
            .cursor.return_value.__enter__.return_value
        )
        cursor.fetchall.return_value = []

        result = persistence.get_farm_user_permissions(7, "farm_002")

    assert result == set()


def test_require_farm_permission_allows_permission_for_requested_farm():
    dependency = dependencies.require_farm_permission("sensor.view")
    user = {"id": 7, "username": "operator", "is_active": True}

    with patch(
        "dependencies.persistence.get_farm_user_permissions",
        return_value={"sensor.view"},
    ) as get_permissions:
        result = dependency(farm_code="farm_001", user=user)

    assert result == user
    get_permissions.assert_called_once_with(
        user_id=7,
        farm_code="farm_001",
    )


def test_require_farm_permission_rejects_missing_permission():
    dependency = dependencies.require_farm_permission("actuator.control")
    user = {"id": 7, "username": "viewer", "is_active": True}

    with patch(
        "dependencies.persistence.get_farm_user_permissions",
        return_value={"sensor.view"},
    ):
        with pytest.raises(HTTPException) as exc_info:
            dependency(farm_code="farm_001", user=user)

    assert exc_info.value.status_code == 403


def test_require_farm_permission_fails_closed_when_database_unavailable():
    dependency = dependencies.require_farm_permission("sensor.view")
    user = {"id": 7, "username": "operator", "is_active": True}

    with patch(
        "dependencies.persistence.get_farm_user_permissions",
        side_effect=RuntimeError("simulated database failure"),
    ):
        with pytest.raises(HTTPException) as exc_info:
            dependency(farm_code="farm_001", user=user)

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "Farm authorization service unavailable"


def test_list_user_farm_codes_with_permission_uses_farm_roles_and_super_admin():
    with patch("persistence.db.connect") as connect:
        cursor = (
            connect.return_value.__enter__.return_value
            .cursor.return_value.__enter__.return_value
        )
        cursor.fetchall.return_value = [
            ("farm_001",),
            ("farm_002",),
        ]

        result = persistence.list_user_farm_codes_with_permission(
            user_id=7,
            permission="sensor.history",
        )

    assert result == {"farm_001", "farm_002"}
    query, params = cursor.execute.call_args.args
    assert "farm_user_roles" in query
    assert "r.name = 'Super Admin'" in query
    assert "p.name = %s" in query
    assert params == (7, "sensor.history", 7, "sensor.history")


def test_list_user_farm_codes_with_permission_returns_empty_set():
    with patch("persistence.db.connect") as connect:
        cursor = (
            connect.return_value.__enter__.return_value
            .cursor.return_value.__enter__.return_value
        )
        cursor.fetchall.return_value = []

        result = persistence.list_user_farm_codes_with_permission(
            user_id=7,
            permission="sensor.history",
        )

    assert result == set()
