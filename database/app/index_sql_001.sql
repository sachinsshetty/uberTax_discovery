-- Run ONCE in your database (safe, zero downtime)
ALTER TABLE entity_connections 
ADD CONSTRAINT IF NOT EXISTS uniq_connection 
UNIQUE (from_type, from_id, to_type, to_id, relation);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_connections_from 
ON entity_connections (from_type, from_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_connections_to 
ON entity_connections (to_type, to_id);