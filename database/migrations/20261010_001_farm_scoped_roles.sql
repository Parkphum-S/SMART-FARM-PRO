BEGIN;

-- Assign exactly one role to each user within each farm.
-- Existing global user_roles are intentionally not migrated automatically.
CREATE TABLE app.farm_user_roles (
    farm_id bigint NOT NULL,
    user_id bigint NOT NULL,
    role_id bigint NOT NULL,
    assigned_by_user_id bigint,
    assigned_at timestamp with time zone NOT NULL DEFAULT now(),

    CONSTRAINT farm_user_roles_pkey
        PRIMARY KEY (farm_id, user_id),

    CONSTRAINT farm_user_roles_membership_fkey
        FOREIGN KEY (farm_id, user_id)
        REFERENCES app.farm_users (farm_id, user_id)
        ON DELETE CASCADE,

    CONSTRAINT farm_user_roles_role_fkey
        FOREIGN KEY (role_id)
        REFERENCES app.roles (id)
        ON DELETE RESTRICT,

    CONSTRAINT farm_user_roles_assigned_by_fkey
        FOREIGN KEY (assigned_by_user_id)
        REFERENCES app.users (id)
        ON DELETE SET NULL
);

CREATE INDEX farm_user_roles_role_id_idx
    ON app.farm_user_roles (role_id);

COMMENT ON TABLE app.farm_user_roles IS
    'Farm-scoped role assignments; one role per farm membership.';

COMMENT ON COLUMN app.farm_user_roles.assigned_by_user_id IS
    'User who assigned the role; NULL when the assigning account is deleted.';

COMMIT;
