# Smart Farm Pro — Application Architecture v1

## Architecture

Web App (Next.js/React/TypeScript) + Mobile App (React Native/Expo/TypeScript)

Authentication + RBAC

FastAPI API

PostgreSQL + MQTT (Mosquitto) + Gateway + ESP32

## Principles

- Preserve the existing Gateway, MQTT, and FastAPI foundation.
- Web and Mobile share one product language and design system.
- Authentication and authorization are enforced by FastAPI.
- PostgreSQL is the target persistent application data store.
- MQTT remains the device communication layer.
- Existing MQTT topics remain stable unless explicitly versioned.
- Existing state_store.py remains until database migration is validated.

## RBAC

Initial roles:

1. Super Admin — full system governance.
2. Farm Admin — manages assigned farms, users, zones, and devices.
3. Operator — monitors assigned zones and controls permitted actuators.
4. Viewer — read-only monitoring and reports.

Initial permissions:

- dashboard.view
- sensor.view
- sensor.history
- actuator.view
- actuator.control
- device.view
- device.manage
- user.view
- user.create
- user.edit
- farm.manage
- report.view
- audit.view
- system.manage

Frontend permission visibility is not a security boundary. Backend authorization is mandatory.

## Database Entities

- users
- roles
- permissions
- user_roles
- role_permissions
- farms
- farm_users
- zones
- devices
- sensors
- actuators
- sensor_readings
- actuator_states
- actuator_commands
- alerts
- audit_logs

## API Direction

Base namespace: /api/v1

Planned resources:

- auth
- users
- roles
- permissions
- farms
- zones
- devices
- sensors
- actuators
- alerts
- reports
- audit

Existing validated endpoints remain during migration:

- GET /health
- POST /api/v1/actuators/{actuator_id}/command
- GET /api/v1/esp32/status
- GET /api/v1/sensors/readings
- GET /api/v1/actuators/states

The current actuator command endpoint internally uses zone_01. This will be evolved explicitly in a later API step.

## Authentication Flow

Login -> Authentication -> JWT/session -> Roles -> Permissions -> Farm selection -> Dashboard

## Actuator Safety

User -> Permission Check -> Confirmation -> request_id -> FastAPI -> MQTT Command -> ESP32 -> ACK/State -> Persistence -> Audit Log

An accepted HTTP request does not by itself prove that the physical actuator changed state.

## Frontend Product Areas

Web: Dashboard, Sensors, Actuators, Devices, Alerts, Reports, Admin

Mobile: Dashboard, Sensors, Actuators, Devices, Alerts, Reports

## Implementation Phases

Phase A — Foundation: Architecture, database schema, API contracts, authentication, RBAC.
Phase B — Persistent Data: PostgreSQL persistence for sensors, devices, actuators, alerts, audit logs.
Phase C — Web: Next.js application using the approved Smart Farm Pro design system.
Phase D — Mobile: React Native / Expo application using the same product language.
Phase E — Hardening: Security, RBAC, API, MQTT integration, audit, end-to-end testing.

## Compatibility Rules

- Do not remove state_store.py before database migration is validated.
- Do not change MQTT topics implicitly.
- Do not store credentials in source code.
- Do not rely on frontend-only RBAC.
- Keep Gateway and Backend responsibilities separate.
- Test and commit each stable checkpoint.
