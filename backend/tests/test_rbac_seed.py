import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import rbac_seed


def test_canonical_roles_match_architecture():
    assert set(rbac_seed.ROLE_DESCRIPTIONS) == {
        "Super Admin",
        "Farm Admin",
        "Operator",
        "Viewer",
    }


def test_canonical_permissions_match_architecture():
    assert set(rbac_seed.PERMISSION_DESCRIPTIONS) == {
        "dashboard.view",
        "sensor.view",
        "sensor.history",
        "actuator.view",
        "actuator.control",
        "device.view",
        "device.manage",
        "user.view",
        "user.create",
        "user.edit",
        "farm.manage",
        "report.view",
        "audit.view",
        "system.manage",
    }


def test_definitions_are_valid_and_have_no_duplicate_names():
    rbac_seed.validate_definitions()

    assert len(rbac_seed.ROLE_DESCRIPTIONS) == len(set(rbac_seed.ROLE_DESCRIPTIONS))
    assert len(rbac_seed.PERMISSION_DESCRIPTIONS) == len(
        set(rbac_seed.PERMISSION_DESCRIPTIONS)
    )


def test_definitions_are_immutable():
    try:
        rbac_seed.ROLE_DESCRIPTIONS["Unexpected Role"] = "Should not be added."
    except TypeError:
        pass
    else:
        raise AssertionError("Role definitions must be immutable")


def test_role_permission_matrix_matches_approved_policy():
    rbac_seed.validate_role_permissions()

    assert set(rbac_seed.ROLE_PERMISSIONS) == set(rbac_seed.ROLE_DESCRIPTIONS)
    assert rbac_seed.ROLE_PERMISSIONS["Super Admin"] == frozenset(
        rbac_seed.PERMISSION_DESCRIPTIONS
    )


def test_operator_can_control_actuators_but_farm_admin_cannot():
    assert "actuator.control" in rbac_seed.ROLE_PERMISSIONS["Operator"]
    assert "actuator.control" not in rbac_seed.ROLE_PERMISSIONS["Farm Admin"]
    assert "actuator.control" not in rbac_seed.ROLE_PERMISSIONS["Viewer"]


def test_farm_admin_can_manage_devices_without_actuator_control():
    assert "device.manage" in rbac_seed.ROLE_PERMISSIONS["Farm Admin"]
    assert "device.manage" in rbac_seed.ROLE_PERMISSIONS["Super Admin"]
    assert "device.manage" not in rbac_seed.ROLE_PERMISSIONS["Operator"]
    assert "device.manage" not in rbac_seed.ROLE_PERMISSIONS["Viewer"]
    assert "actuator.control" not in rbac_seed.ROLE_PERMISSIONS["Farm Admin"]


def test_all_roles_can_view_sensor_history():
    for role in ("Super Admin", "Farm Admin", "Operator", "Viewer"):
        assert "sensor.history" in rbac_seed.ROLE_PERMISSIONS[role]


def test_only_farm_admin_and_super_admin_have_member_management_permissions():
    for permission in ("user.view", "user.create", "user.edit", "farm.manage"):
        assert permission in rbac_seed.ROLE_PERMISSIONS["Super Admin"]
        assert permission in rbac_seed.ROLE_PERMISSIONS["Farm Admin"]
        assert permission not in rbac_seed.ROLE_PERMISSIONS["Operator"]
        assert permission not in rbac_seed.ROLE_PERMISSIONS["Viewer"]


def test_role_permission_matrix_is_immutable():
    try:
        rbac_seed.ROLE_PERMISSIONS["Unexpected Role"] = frozenset()
    except TypeError:
        pass
    else:
        raise AssertionError("Role permission matrix must be immutable")

    try:
        rbac_seed.ROLE_PERMISSIONS["Viewer"].add("actuator.control")
    except AttributeError:
        pass
    else:
        raise AssertionError("Individual role permissions must be immutable")
