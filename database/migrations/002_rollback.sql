ALTER TABLE enrollment_events 
DROP COLUMN IF EXISTS note;

DELETE FROM schema_migrations WHERE version = '002';