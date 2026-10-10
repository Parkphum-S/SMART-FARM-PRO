import sys
from unittest.mock import MagicMock, patch

sys.path.insert(0, "backend")

import persistence


def _mock_cursor():
    connection = MagicMock()
    cursor = (
        connection.__enter__.return_value
        .cursor.return_value.__enter__.return_value
    )
    return connection, cursor


def test_list_farm_members_returns_farm_scoped_roles():
    connection, cursor = _mock_cursor()
    cursor.fetchall.return_value = [
        (7, "operator1", "operator@example.com", True, "Operator"),
        (8, "viewer1", "viewer@example.com", True, "Viewer"),
        (9, "unassigned", "unassigned@example.com", True, None),
    ]

    with patch("persistence.db.connect", return_value=connection):
        result = persistence.list_farm_members("farm_001")

    assert result == [
        {
            "id": 7,
            "username": "operator1",
            "email": "operator@example.com",
            "is_active": True,
            "role": "Operator",
        },
        {
            "id": 8,
            "username": "viewer1",
            "email": "viewer@example.com",
            "is_active": True,
            "role": "Viewer",
        },
        {
            "id": 9,
            "username": "unassigned",
            "email": "unassigned@example.com",
            "is_active": True,
            "role": None,
        },
    ]
    query, params = cursor.execute.call_args.args
    assert "WHERE f.farm_code = %s" in query
    assert "LEFT JOIN farm_user_roles" in query
    assert params == ("farm_001",)


def test_list_farm_members_returns_empty_list_when_no_members():
    connection, cursor = _mock_cursor()
    cursor.fetchall.return_value = []

    with patch("persistence.db.connect", return_value=connection):
        result = persistence.list_farm_members("farm_missing")

    assert result == []


def test_assign_farm_role_uses_farm_scoped_authorization():
    connection, cursor = _mock_cursor()
    cursor.fetchone.return_value = (1,)

    with patch("persistence.db.connect", return_value=connection):
        result = persistence.assign_farm_role(
            farm_code="farm_001",
            user_id=8,
            role_name="Operator",
            assigned_by_user_id=7,
        )

    assert result is True
    query, params = cursor.execute.call_args.args
    assert "actor_is_super_admin" in query
    assert "actor_is_farm_admin" in query
    assert "target_is_member" in query
    assert "ON CONFLICT (farm_id, user_id)" in query
    assert params == (
        8,
        7,
        7,
        "Operator",
        "farm_001",
        8,
        7,
        "Operator",
    )


def test_assign_farm_role_returns_false_when_sql_authorization_fails():
    connection, cursor = _mock_cursor()
    cursor.fetchone.return_value = None

    with patch("persistence.db.connect", return_value=connection):
        result = persistence.assign_farm_role(
            farm_code="farm_001",
            user_id=8,
            role_name="Viewer",
            assigned_by_user_id=7,
        )

    assert result is False


def test_assign_farm_role_rejects_super_admin_without_database_access():
    with patch("persistence.db.connect") as connect:
        result = persistence.assign_farm_role(
            farm_code="farm_001",
            user_id=8,
            role_name="Super Admin",
            assigned_by_user_id=7,
        )

    assert result is False
    connect.assert_not_called()


def test_assign_farm_role_rejects_unknown_role_without_database_access():
    with patch("persistence.db.connect") as connect:
        result = persistence.assign_farm_role(
            farm_code="farm_001",
            user_id=8,
            role_name="Unknown Role",
            assigned_by_user_id=7,
        )

    assert result is False
    connect.assert_not_called()
