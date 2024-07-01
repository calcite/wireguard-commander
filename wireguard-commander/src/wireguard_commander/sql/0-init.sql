
CREATE TABLE db_version
(
    version INTEGER PRIMARY KEY NOT NULL,
    date timestamp DEFAULT NOW() NOT NULL
);


CREATE SEQUENCE server_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1;

CREATE TABLE server
(
    "id"            integer PRIMARY KEY  DEFAULT nextval('server_id_seq') NOT NULL,
    "worker"        character varying(128)                           NOT NULL,
    "interface"     character varying(128)                           NOT NULL,
    "cidr"          character varying(128)                          NOT NULL,
    "name"          character varying(128)                           NOT NULL,
    "listen_port"   integer                                          NOT NULL,
    "enabled"       boolean DEFAULT true                             NOT NULL,
    "private_key"   character varying(128)                           NOT NULL,
    "public_key"    character varying(128)                           NOT NULL,
    "fw_mark"       integer   DEFAULT 0                              NOT NULL,
    "table"         integer DEFAULT 0                                NOT NULL,
    "keep_alived"   integer DEFAULT 25                               NOT NULL,
    "endpoint"      character varying(128)                           NOT NULL,
    "dns"           character varying(128)                           NOT NULL,
    "mtu"           integer DEFAULT 0                                NOT NULL,
    "allow_ips"     character varying(256)                           NOT NULL,
    "created_at"    timestamp DEFAULT NOW()                          NOT NULL,
    "updated_at"    timestamp DEFAULT NOW()                          NOT NULL,
    "pre_up"        character varying(256),
    "post_up"       character varying(256),
    "pre_down"      character varying(256),
    "post_down"     character varying(256),
    "domain_group"  character varying(128),
);
CREATE INDEX idx_worker_server ON server (worker);
CREATE INDEX idx_domain_group_server ON server (domain_group);

CREATE SEQUENCE user_device_id_seq INCREMENT 1 MINVALUE 1 MAXVALUE 2147483647 START 1;

CREATE TABLE user_device
(
    "id"            integer PRIMARY KEY DEFAULT nextval('user_device_id_seq') NOT NULL,
    "username"      character varying(128)                                     NOT NULL,
    "mail"          character varying(128)                                     NOT NULL,
    "ip"            character varying(64)                                      NOT NULL,
    "enabled"       boolean             DEFAULT true                           NOT NULL,
    "server_id"     integer REFERENCES server (id)                             NOT NULL,
    "private_key"   character varying(128)                                     NOT NULL,
    "public_key"    character varying(128)                                     NOT NULL,
    "created_at"    timestamp           DEFAULT NOW()                          NOT NULL,
    "updated_at"    timestamp           DEFAULT NOW()                          NOT NULL,
    "preshared_key" character varying(128),
);
CREATE INDEX idx_user_device_name ON user_device (username);
CREATE INDEX idx_user_device_server ON user_device (server_id);
