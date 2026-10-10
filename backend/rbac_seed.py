"""Canonical RBAC definitions for Smart Farm Pro.

This module is intentionally data-only: importing it does not connect to
PostgreSQL or modify any application state.
"""

from types import MappingProxyType


ROLE_DESCRIPTIONS = MappingProxyType({
    "Super Admin": "Full system governance.",
    "Farm Admin": "Manages assigned farms, users, zones, and devices.",
    "Operator": "Monitors assigned zones and controls permitted actuators.",
    "Viewer": "Read-only monitoring and reports.",
})

PERMISSION_DESCRIPTIONS = MappingProxyType({
    "dashboard.view": "View the farm dashboard.",
    "sensor.view": "View current sensor readings.",
    "sensor.history": "View persisted sensor reading history.",
    "actuator.view": "View actuator states.",
    "actuator.control": "Control permitted actuators.",
    "device.view": "View device status.",
    "device.manage": "Manage farm devices.",
    "user.view": "View users.",
    "user.create": "Create users.",
    "user.edit": "Edit users.",
    "farm.manage": "Manage assigned farms.",
    "report.view": "View reports.",
    "audit.view": "View audit records.",
    "system.manage": "Manage system settings.",
})


def validate_definitions() -> None:
    """Fail fast if canonical RBAC definitions become invalid."""
    if len(ROLE_DESCRIPTIONS) != 4:
        raise ValueError("Expected exactly four canonical roles")

    if len(PERMISSION_DESCRIPTIONS) != 14:
        raise ValueError("Expected exactly fourteen canonical permissions")

    if any(not name.strip() for name in ROLE_DESCRIPTIONS):
        raise ValueError("Role names must not be empty")

    if any(not name.strip() for name in PERMISSION_DESCRIPTIONS):
        raise ValueError("Permission names must not be empty")

    if any(not description.strip() for description in ROLE_DESCRIPTIONS.values()):
        raise ValueError("Role descriptions must not be empty")

    if any(
        not description.strip()
        for description in PERMISSION_DESCRIPTIONS.values()
    ):
        raise ValueError("Permission descriptions must not be empty")


# Canonical role-to-permission policy.
# Farm-scoped permissions are evaluated within each farm membership.
ROLE_PERMISSIONS = MappingProxyType({
    "Super Admin": frozenset(PERMISSION_DESCRIPTIONS),
    "Farm Admin": frozenset({
        "dashboard.view",
        "sensor.view",
        "sensor.history",
        "actuator.view",
        "device.view",
        "device.manage",
        "user.view",
        "user.create",
        "user.edit",
        "farm.manage",
        "report.view",
        "audit.view",
    }),
    "Operator": frozenset({
        "dashboard.view",
        "sensor.view",
        "sensor.history",
        "actuator.view",
        "actuator.control",
        "device.view",
        "report.view",
    }),
    "Viewer": frozenset({
        "dashboard.view",
        "sensor.view",
        "sensor.history",
        "actuator.view",
        "device.view",
        "report.view",
    }),
})


def validate_role_permissions() -> None:
    """Validate the canonical role-to-permission policy."""
    if set(ROLE_PERMISSIONS) != set(ROLE_DESCRIPTIONS):
        raise ValueError("Every canonical role must have a permission policy")

    known_permissions = set(PERMISSION_DESCRIPTIONS)
    for role, permissions in ROLE_PERMISSIONS.items():
        unknown = set(permissions) - known_permissions
        if unknown:
            raise ValueError(
                f"Role {role!r} contains unknown permissions: {sorted(unknown)}"
            )

    if "actuator.control" in ROLE_PERMISSIONS["Farm Admin"]:
        raise ValueError("Farm Admin must not control actuators")

    if "actuator.control" not in ROLE_PERMISSIONS["Operator"]:
        raise ValueError("Operator must be allowed to control permitted actuators")

    if "actuator.control" in ROLE_PERMISSIONS["Viewer"]:
        raise ValueError("Viewer must not control actuators")

    if not {
        "user.view", "user.create", "user.edit", "farm.manage"
    }.issubset(ROLE_PERMISSIONS["Farm Admin"]):
        raise ValueError("Farm Admin is missing member-management permissions")

    if ROLE_PERMISSIONS["Farm Admin"] & {
        "system.manage",
    }:
        raise ValueError("Farm Admin must not manage system-wide settings")

    if ROLE_PERMISSIONS["Operator"] & {
        "user.view", "user.create", "user.edit",
        "farm.manage", "system.manage",
    }:
        raise ValueError("Operator must not manage users or farms")

    if ROLE_PERMISSIONS["Viewer"] & {
        "user.view", "user.create", "user.edit",
        "farm.manage", "device.manage",
        "actuator.control", "system.manage",
    }:
        raise ValueError("Viewer must remain read-only")
