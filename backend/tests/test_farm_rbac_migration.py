from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MIGRATION = (
    ROOT
    / "database"
    / "migrations"
    / "20261010_001_farm_scoped_roles.sql"
)


def test_migration_creates_farm_scoped_role_assignments():
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert "begin;" in sql
    assert "commit;" in sql
    assert "create table app.farm_user_roles" in sql
    assert "primary key (farm_id, user_id)" in sql


def test_role_assignment_requires_existing_farm_membership():
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert "foreign key (farm_id, user_id)" in sql
    assert "references app.farm_users (farm_id, user_id)" in sql
    assert "on delete cascade" in sql


def test_role_assignment_requires_existing_role():
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert "foreign key (role_id)" in sql
    assert "references app.roles (id)" in sql
    assert "on delete restrict" in sql


def test_migration_does_not_automatically_reassign_legacy_roles():
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert "insert into app.farm_user_roles" not in sql
    assert "delete from app.user_roles" not in sql
    assert "update app.user_roles" not in sql


def test_role_assignment_records_who_assigned_it():
    sql = MIGRATION.read_text(encoding="utf-8").lower()

    assert "assigned_by_user_id bigint" in sql
    assert "references app.users (id)" in sql
    assert "assigned_at timestamp with time zone not null default now()" in sql
