ALTER TABLE enrollment_events 
ADD COLUMN IF NOT EXISTS note VARCHAR(200);

INSERT INTO schema_migrations (version) VALUES ('002');