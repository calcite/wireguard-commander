ALTER TABLE server
    ADD COLUMN domain_group character varying(128);
CREATE INDEX idx_domain_group_server ON server (domain_group);
