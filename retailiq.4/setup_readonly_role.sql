-- Run this once against your Postgres database (e.g. in Neon's SQL editor
-- or via psql) to create a role that can only ever SELECT — used as
-- DATABASE_URL_READONLY so LLM-generated and playground SQL runs against a
-- connection that's read-only at the database level, not just app-level
-- validation.

CREATE ROLE retailiq_reader WITH LOGIN PASSWORD 'choose-a-strong-password-here';
GRANT CONNECT ON DATABASE <your_database_name> TO retailiq_reader;
GRANT USAGE ON SCHEMA public TO retailiq_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO retailiq_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO retailiq_reader;

-- Then set, as a Streamlit secret:
-- DATABASE_URL_READONLY = "postgresql://retailiq_reader:choose-a-strong-password-here@<host>/<your_database_name>"
