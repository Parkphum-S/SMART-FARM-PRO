--
-- PostgreSQL database dump
--

\restrict DxdeyShK3Y3fPkWxtP8C3QQvnFirMeqIKSQeE7D0aktsmggKWNohzgMZ74LZo5h

-- Dumped from database version 17.11 (Debian 17.11-0+deb13u1)
-- Dumped by pg_dump version 17.11 (Debian 17.11-0+deb13u1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: app; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA app;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: actuator_commands; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.actuator_commands (
    id bigint NOT NULL,
    actuator_id bigint NOT NULL,
    command text NOT NULL,
    request_id text NOT NULL,
    requested_at timestamp with time zone NOT NULL,
    acknowledged_at timestamp with time zone,
    result text,
    raw_payload jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: actuator_commands_id_seq; Type: SEQUENCE; Schema: app; Owner: -
--

CREATE SEQUENCE app.actuator_commands_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: actuator_commands_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: -
--

ALTER SEQUENCE app.actuator_commands_id_seq OWNED BY app.actuator_commands.id;


--
-- Name: actuator_states; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.actuator_states (
    id bigint NOT NULL,
    actuator_id bigint NOT NULL,
    state text NOT NULL,
    recorded_at timestamp with time zone NOT NULL,
    raw_payload jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: actuator_states_id_seq; Type: SEQUENCE; Schema: app; Owner: -
--

CREATE SEQUENCE app.actuator_states_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: actuator_states_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: -
--

ALTER SEQUENCE app.actuator_states_id_seq OWNED BY app.actuator_states.id;


--
-- Name: actuators; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.actuators (
    id bigint NOT NULL,
    farm_id bigint NOT NULL,
    zone_id bigint NOT NULL,
    device_id bigint,
    actuator_code text NOT NULL,
    actuator_type text NOT NULL,
    name text,
    state text DEFAULT 'unknown'::text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: actuators_id_seq; Type: SEQUENCE; Schema: app; Owner: -
--

CREATE SEQUENCE app.actuators_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: actuators_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: -
--

ALTER SEQUENCE app.actuators_id_seq OWNED BY app.actuators.id;


--
-- Name: alerts; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.alerts (
    id bigint NOT NULL,
    farm_id bigint NOT NULL,
    zone_id bigint,
    device_id bigint,
    sensor_id bigint,
    actuator_id bigint,
    alert_type text NOT NULL,
    severity text DEFAULT 'warning'::text NOT NULL,
    message text NOT NULL,
    status text DEFAULT 'open'::text NOT NULL,
    triggered_at timestamp with time zone DEFAULT now() NOT NULL,
    resolved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: alerts_id_seq; Type: SEQUENCE; Schema: app; Owner: -
--

CREATE SEQUENCE app.alerts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: alerts_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: -
--

ALTER SEQUENCE app.alerts_id_seq OWNED BY app.alerts.id;


--
-- Name: audit_logs; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.audit_logs (
    id bigint NOT NULL,
    user_id bigint,
    farm_id bigint,
    action text NOT NULL,
    resource_type text,
    resource_id text,
    request_id text,
    details jsonb,
    ip_address inet,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: app; Owner: -
--

CREATE SEQUENCE app.audit_logs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: -
--

ALTER SEQUENCE app.audit_logs_id_seq OWNED BY app.audit_logs.id;


--
-- Name: devices; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.devices (
    id bigint NOT NULL,
    farm_id bigint NOT NULL,
    zone_id bigint,
    device_code text NOT NULL,
    device_type text NOT NULL,
    name text,
    status text DEFAULT 'unknown'::text NOT NULL,
    last_seen_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: devices_id_seq; Type: SEQUENCE; Schema: app; Owner: -
--

CREATE SEQUENCE app.devices_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: devices_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: -
--

ALTER SEQUENCE app.devices_id_seq OWNED BY app.devices.id;


--
-- Name: farm_users; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.farm_users (
    farm_id bigint NOT NULL,
    user_id bigint NOT NULL
);


--
-- Name: farms; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.farms (
    id bigint NOT NULL,
    farm_code text NOT NULL,
    name text NOT NULL,
    description text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: farms_id_seq; Type: SEQUENCE; Schema: app; Owner: -
--

CREATE SEQUENCE app.farms_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: farms_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: -
--

ALTER SEQUENCE app.farms_id_seq OWNED BY app.farms.id;


--
-- Name: permissions; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.permissions (
    id bigint NOT NULL,
    name text NOT NULL,
    description text
);


--
-- Name: permissions_id_seq; Type: SEQUENCE; Schema: app; Owner: -
--

CREATE SEQUENCE app.permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: -
--

ALTER SEQUENCE app.permissions_id_seq OWNED BY app.permissions.id;


--
-- Name: role_permissions; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.role_permissions (
    role_id bigint NOT NULL,
    permission_id bigint NOT NULL
);


--
-- Name: roles; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.roles (
    id bigint NOT NULL,
    name text NOT NULL,
    description text
);


--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: app; Owner: -
--

CREATE SEQUENCE app.roles_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: -
--

ALTER SEQUENCE app.roles_id_seq OWNED BY app.roles.id;


--
-- Name: sensor_readings; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.sensor_readings (
    id bigint NOT NULL,
    sensor_id bigint NOT NULL,
    recorded_at timestamp with time zone NOT NULL,
    temperature_c double precision,
    humidity_pct double precision,
    value double precision,
    raw_payload jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: sensor_readings_id_seq; Type: SEQUENCE; Schema: app; Owner: -
--

CREATE SEQUENCE app.sensor_readings_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sensor_readings_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: -
--

ALTER SEQUENCE app.sensor_readings_id_seq OWNED BY app.sensor_readings.id;


--
-- Name: sensors; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.sensors (
    id bigint NOT NULL,
    farm_id bigint NOT NULL,
    zone_id bigint NOT NULL,
    device_id bigint,
    sensor_code text NOT NULL,
    sensor_type text NOT NULL,
    name text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: sensors_id_seq; Type: SEQUENCE; Schema: app; Owner: -
--

CREATE SEQUENCE app.sensors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: sensors_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: -
--

ALTER SEQUENCE app.sensors_id_seq OWNED BY app.sensors.id;


--
-- Name: user_roles; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.user_roles (
    user_id bigint NOT NULL,
    role_id bigint NOT NULL
);


--
-- Name: users; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.users (
    id bigint NOT NULL,
    username text NOT NULL,
    email text NOT NULL,
    password_hash text NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: app; Owner: -
--

CREATE SEQUENCE app.users_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: -
--

ALTER SEQUENCE app.users_id_seq OWNED BY app.users.id;


--
-- Name: zones; Type: TABLE; Schema: app; Owner: -
--

CREATE TABLE app.zones (
    id bigint NOT NULL,
    farm_id bigint NOT NULL,
    zone_code text NOT NULL,
    name text NOT NULL,
    description text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: zones_id_seq; Type: SEQUENCE; Schema: app; Owner: -
--

CREATE SEQUENCE app.zones_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: zones_id_seq; Type: SEQUENCE OWNED BY; Schema: app; Owner: -
--

ALTER SEQUENCE app.zones_id_seq OWNED BY app.zones.id;


--
-- Name: actuator_commands id; Type: DEFAULT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.actuator_commands ALTER COLUMN id SET DEFAULT nextval('app.actuator_commands_id_seq'::regclass);


--
-- Name: actuator_states id; Type: DEFAULT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.actuator_states ALTER COLUMN id SET DEFAULT nextval('app.actuator_states_id_seq'::regclass);


--
-- Name: actuators id; Type: DEFAULT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.actuators ALTER COLUMN id SET DEFAULT nextval('app.actuators_id_seq'::regclass);


--
-- Name: alerts id; Type: DEFAULT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.alerts ALTER COLUMN id SET DEFAULT nextval('app.alerts_id_seq'::regclass);


--
-- Name: audit_logs id; Type: DEFAULT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.audit_logs ALTER COLUMN id SET DEFAULT nextval('app.audit_logs_id_seq'::regclass);


--
-- Name: devices id; Type: DEFAULT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.devices ALTER COLUMN id SET DEFAULT nextval('app.devices_id_seq'::regclass);


--
-- Name: farms id; Type: DEFAULT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.farms ALTER COLUMN id SET DEFAULT nextval('app.farms_id_seq'::regclass);


--
-- Name: permissions id; Type: DEFAULT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.permissions ALTER COLUMN id SET DEFAULT nextval('app.permissions_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.roles ALTER COLUMN id SET DEFAULT nextval('app.roles_id_seq'::regclass);


--
-- Name: sensor_readings id; Type: DEFAULT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.sensor_readings ALTER COLUMN id SET DEFAULT nextval('app.sensor_readings_id_seq'::regclass);


--
-- Name: sensors id; Type: DEFAULT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.sensors ALTER COLUMN id SET DEFAULT nextval('app.sensors_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.users ALTER COLUMN id SET DEFAULT nextval('app.users_id_seq'::regclass);


--
-- Name: zones id; Type: DEFAULT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.zones ALTER COLUMN id SET DEFAULT nextval('app.zones_id_seq'::regclass);


--
-- Name: actuator_commands actuator_commands_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.actuator_commands
    ADD CONSTRAINT actuator_commands_pkey PRIMARY KEY (id);


--
-- Name: actuator_commands actuator_commands_request_id_key; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.actuator_commands
    ADD CONSTRAINT actuator_commands_request_id_key UNIQUE (request_id);


--
-- Name: actuator_states actuator_states_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.actuator_states
    ADD CONSTRAINT actuator_states_pkey PRIMARY KEY (id);


--
-- Name: actuators actuators_farm_id_actuator_code_key; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.actuators
    ADD CONSTRAINT actuators_farm_id_actuator_code_key UNIQUE (farm_id, actuator_code);


--
-- Name: actuators actuators_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.actuators
    ADD CONSTRAINT actuators_pkey PRIMARY KEY (id);


--
-- Name: alerts alerts_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.alerts
    ADD CONSTRAINT alerts_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: devices devices_farm_id_device_code_key; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.devices
    ADD CONSTRAINT devices_farm_id_device_code_key UNIQUE (farm_id, device_code);


--
-- Name: devices devices_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.devices
    ADD CONSTRAINT devices_pkey PRIMARY KEY (id);


--
-- Name: farm_users farm_users_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.farm_users
    ADD CONSTRAINT farm_users_pkey PRIMARY KEY (farm_id, user_id);


--
-- Name: farms farms_farm_code_key; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.farms
    ADD CONSTRAINT farms_farm_code_key UNIQUE (farm_code);


--
-- Name: farms farms_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.farms
    ADD CONSTRAINT farms_pkey PRIMARY KEY (id);


--
-- Name: permissions permissions_name_key; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.permissions
    ADD CONSTRAINT permissions_name_key UNIQUE (name);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.role_permissions
    ADD CONSTRAINT role_permissions_pkey PRIMARY KEY (role_id, permission_id);


--
-- Name: roles roles_name_key; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.roles
    ADD CONSTRAINT roles_name_key UNIQUE (name);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: sensor_readings sensor_readings_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.sensor_readings
    ADD CONSTRAINT sensor_readings_pkey PRIMARY KEY (id);


--
-- Name: sensors sensors_farm_id_sensor_code_key; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.sensors
    ADD CONSTRAINT sensors_farm_id_sensor_code_key UNIQUE (farm_id, sensor_code);


--
-- Name: sensors sensors_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.sensors
    ADD CONSTRAINT sensors_pkey PRIMARY KEY (id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (user_id, role_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: zones zones_farm_id_zone_code_key; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.zones
    ADD CONSTRAINT zones_farm_id_zone_code_key UNIQUE (farm_id, zone_code);


--
-- Name: zones zones_pkey; Type: CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.zones
    ADD CONSTRAINT zones_pkey PRIMARY KEY (id);


--
-- Name: idx_actuator_commands_actuator_time; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX idx_actuator_commands_actuator_time ON app.actuator_commands USING btree (actuator_id, requested_at DESC);


--
-- Name: idx_actuator_states_actuator_time; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX idx_actuator_states_actuator_time ON app.actuator_states USING btree (actuator_id, recorded_at DESC);


--
-- Name: idx_alerts_farm_time; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX idx_alerts_farm_time ON app.alerts USING btree (farm_id, triggered_at DESC);


--
-- Name: idx_alerts_status_time; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX idx_alerts_status_time ON app.alerts USING btree (status, triggered_at DESC);


--
-- Name: idx_audit_logs_action_time; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX idx_audit_logs_action_time ON app.audit_logs USING btree (action, created_at DESC);


--
-- Name: idx_audit_logs_farm_time; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX idx_audit_logs_farm_time ON app.audit_logs USING btree (farm_id, created_at DESC);


--
-- Name: idx_audit_logs_user_time; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX idx_audit_logs_user_time ON app.audit_logs USING btree (user_id, created_at DESC);


--
-- Name: idx_sensor_readings_sensor_time; Type: INDEX; Schema: app; Owner: -
--

CREATE INDEX idx_sensor_readings_sensor_time ON app.sensor_readings USING btree (sensor_id, recorded_at DESC);


--
-- Name: actuator_commands actuator_commands_actuator_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.actuator_commands
    ADD CONSTRAINT actuator_commands_actuator_id_fkey FOREIGN KEY (actuator_id) REFERENCES app.actuators(id) ON DELETE CASCADE;


--
-- Name: actuator_states actuator_states_actuator_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.actuator_states
    ADD CONSTRAINT actuator_states_actuator_id_fkey FOREIGN KEY (actuator_id) REFERENCES app.actuators(id) ON DELETE CASCADE;


--
-- Name: actuators actuators_device_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.actuators
    ADD CONSTRAINT actuators_device_id_fkey FOREIGN KEY (device_id) REFERENCES app.devices(id) ON DELETE SET NULL;


--
-- Name: actuators actuators_farm_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.actuators
    ADD CONSTRAINT actuators_farm_id_fkey FOREIGN KEY (farm_id) REFERENCES app.farms(id) ON DELETE CASCADE;


--
-- Name: actuators actuators_zone_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.actuators
    ADD CONSTRAINT actuators_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES app.zones(id) ON DELETE CASCADE;


--
-- Name: alerts alerts_actuator_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.alerts
    ADD CONSTRAINT alerts_actuator_id_fkey FOREIGN KEY (actuator_id) REFERENCES app.actuators(id) ON DELETE SET NULL;


--
-- Name: alerts alerts_device_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.alerts
    ADD CONSTRAINT alerts_device_id_fkey FOREIGN KEY (device_id) REFERENCES app.devices(id) ON DELETE SET NULL;


--
-- Name: alerts alerts_farm_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.alerts
    ADD CONSTRAINT alerts_farm_id_fkey FOREIGN KEY (farm_id) REFERENCES app.farms(id) ON DELETE CASCADE;


--
-- Name: alerts alerts_sensor_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.alerts
    ADD CONSTRAINT alerts_sensor_id_fkey FOREIGN KEY (sensor_id) REFERENCES app.sensors(id) ON DELETE SET NULL;


--
-- Name: alerts alerts_zone_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.alerts
    ADD CONSTRAINT alerts_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES app.zones(id) ON DELETE SET NULL;


--
-- Name: audit_logs audit_logs_farm_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.audit_logs
    ADD CONSTRAINT audit_logs_farm_id_fkey FOREIGN KEY (farm_id) REFERENCES app.farms(id) ON DELETE SET NULL;


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES app.users(id) ON DELETE SET NULL;


--
-- Name: devices devices_farm_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.devices
    ADD CONSTRAINT devices_farm_id_fkey FOREIGN KEY (farm_id) REFERENCES app.farms(id) ON DELETE CASCADE;


--
-- Name: devices devices_zone_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.devices
    ADD CONSTRAINT devices_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES app.zones(id) ON DELETE SET NULL;


--
-- Name: farm_users farm_users_farm_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.farm_users
    ADD CONSTRAINT farm_users_farm_id_fkey FOREIGN KEY (farm_id) REFERENCES app.farms(id) ON DELETE CASCADE;


--
-- Name: farm_users farm_users_user_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.farm_users
    ADD CONSTRAINT farm_users_user_id_fkey FOREIGN KEY (user_id) REFERENCES app.users(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.role_permissions
    ADD CONSTRAINT role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES app.permissions(id) ON DELETE CASCADE;


--
-- Name: role_permissions role_permissions_role_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.role_permissions
    ADD CONSTRAINT role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES app.roles(id) ON DELETE CASCADE;


--
-- Name: sensor_readings sensor_readings_sensor_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.sensor_readings
    ADD CONSTRAINT sensor_readings_sensor_id_fkey FOREIGN KEY (sensor_id) REFERENCES app.sensors(id) ON DELETE CASCADE;


--
-- Name: sensors sensors_device_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.sensors
    ADD CONSTRAINT sensors_device_id_fkey FOREIGN KEY (device_id) REFERENCES app.devices(id) ON DELETE SET NULL;


--
-- Name: sensors sensors_farm_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.sensors
    ADD CONSTRAINT sensors_farm_id_fkey FOREIGN KEY (farm_id) REFERENCES app.farms(id) ON DELETE CASCADE;


--
-- Name: sensors sensors_zone_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.sensors
    ADD CONSTRAINT sensors_zone_id_fkey FOREIGN KEY (zone_id) REFERENCES app.zones(id) ON DELETE CASCADE;


--
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES app.roles(id) ON DELETE CASCADE;


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES app.users(id) ON DELETE CASCADE;


--
-- Name: zones zones_farm_id_fkey; Type: FK CONSTRAINT; Schema: app; Owner: -
--

ALTER TABLE ONLY app.zones
    ADD CONSTRAINT zones_farm_id_fkey FOREIGN KEY (farm_id) REFERENCES app.farms(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict DxdeyShK3Y3fPkWxtP8C3QQvnFirMeqIKSQeE7D0aktsmggKWNohzgMZ74LZo5h

