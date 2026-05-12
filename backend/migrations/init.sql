CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

CREATE TABLE IF NOT EXISTS devices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  api_key_hash TEXT UNIQUE NOT NULL,
  api_key_prefix TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS heartbeats (
  id UUID DEFAULT gen_random_uuid(),
  device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  time TIMESTAMPTZ NOT NULL,
  file TEXT,
  language TEXT,
  project TEXT,
  branch TEXT,
  is_write BOOLEAN DEFAULT false,
  PRIMARY KEY (id, time)
);
SELECT create_hypertable('heartbeats', 'time', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  device_id UUID NOT NULL REFERENCES devices(id) ON DELETE CASCADE,
  project TEXT,
  branch TEXT,
  started_at TIMESTAMPTZ NOT NULL,
  ended_at TIMESTAMPTZ NOT NULL,
  duration_seconds INT NOT NULL,
  languages JSONB DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS repos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  local_path TEXT NOT NULL,
  last_analyzed TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS health_snapshots (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  repo_id UUID NOT NULL REFERENCES repos(id) ON DELETE CASCADE,
  taken_at TIMESTAMPTZ DEFAULT now(),
  test_coverage FLOAT DEFAULT 0,
  avg_complexity FLOAT DEFAULT 0,
  dead_code_count INT DEFAULT 0,
  high_churn_files JSONB DEFAULT '[]',
  health_score FLOAT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS summaries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  week_start DATE NOT NULL,
  content TEXT NOT NULL,
  generated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_heartbeats_device_time ON heartbeats (device_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_device ON sessions (device_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_health_repo ON health_snapshots (repo_id, taken_at DESC);
