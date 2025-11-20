-- Run once on container start
CREATE SCHEMA IF NOT EXISTS common;

CREATE TABLE common.tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    schema_name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create first tenant: "acme_corp"
INSERT INTO common.tenants (name, schema_name)
VALUES ('ACME Corp', 'tenant_acme')
ON CONFLICT DO NOTHING;

