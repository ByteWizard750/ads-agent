-- AdGen Phase 1 Supabase Schema Migration
-- All 8 tables scoped by client_id

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Define strict Enum for Kanban lifecycle states (exact spec match)
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'kanban_status') THEN
        CREATE TYPE kanban_status AS ENUM (
            'Todo',
            'Researching',
            'Analyzing',
            'Writing Script',
            'Awaiting Approval',
            'Rendering Video',
            'Completed'
        );
    END IF;
END $$;

-- Script approval status
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'script_approval_status') THEN
        CREATE TYPE script_approval_status AS ENUM (
            'pending',
            'approved',
            'rejected'
        );
    END IF;
END $$;

-- Script variant types
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'script_variant_type') THEN
        CREATE TYPE script_variant_type AS ENUM (
            'variant_a_pain_point',
            'variant_b_stat',
            'variant_c_solution'
        );
    END IF;
END $$;

-- 1. Clients table
CREATE TABLE IF NOT EXISTS clients (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    niche VARCHAR(255) NOT NULL,
    config_path VARCHAR(512) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 2. Runs table
CREATE TABLE IF NOT EXISTS runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id VARCHAR(64) NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    status VARCHAR(32) NOT NULL DEFAULT 'running',
    started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_runs_client_id ON runs(client_id);

-- 3. Ads table (scraped Facebook/Meta Ads Library data & creative metadata)
CREATE TABLE IF NOT EXISTS ads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id VARCHAR(64) NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    apify_ad_id VARCHAR(255),
    advertiser_name VARCHAR(255),
    ad_body TEXT,
    headline TEXT,
    media_urls JSONB DEFAULT '[]'::jsonb,
    started_running_date TIMESTAMPTZ,
    raw_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ads_client_id ON ads(client_id);
CREATE INDEX IF NOT EXISTS idx_ads_run_id ON ads(run_id);

-- 4. Concepts table (extracted marketing angles, pain points, hooks)
CREATE TABLE IF NOT EXISTS concepts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id VARCHAR(64) NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    angle_name VARCHAR(255) NOT NULL,
    pain_point TEXT NOT NULL,
    hook_style VARCHAR(255) NOT NULL,
    pattern_description TEXT NOT NULL,
    source_ad_ids UUID[] DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_concepts_client_id ON concepts(client_id);
CREATE INDEX IF NOT EXISTS idx_concepts_run_id ON concepts(run_id);

-- 5. Scripts table
CREATE TABLE IF NOT EXISTS scripts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id VARCHAR(64) NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    concept_id UUID REFERENCES concepts(id) ON DELETE SET NULL,
    variant_type script_variant_type NOT NULL,
    hook_text TEXT NOT NULL,
    body_script TEXT NOT NULL,
    duration_seconds INT NOT NULL DEFAULT 45,
    approval_status script_approval_status NOT NULL DEFAULT 'pending',
    rejection_reason TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_scripts_client_id ON scripts(client_id);
CREATE INDEX IF NOT EXISTS idx_scripts_run_id ON scripts(run_id);

-- 6. Videos table
CREATE TABLE IF NOT EXISTS videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id VARCHAR(64) NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    script_id UUID NOT NULL REFERENCES scripts(id) ON DELETE CASCADE,
    video_url TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    duration_seconds INT NOT NULL,
    render_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_videos_client_id ON videos(client_id);
CREATE INDEX IF NOT EXISTS idx_videos_run_id ON videos(run_id);
CREATE INDEX IF NOT EXISTS idx_videos_script_id ON videos(script_id);

-- 7. Kanban State table (strictly enforced kanban_status enum)
CREATE TABLE IF NOT EXISTS kanban_state (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id VARCHAR(64) NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    script_id UUID REFERENCES scripts(id) ON DELETE CASCADE,
    current_state kanban_status NOT NULL DEFAULT 'Todo',
    history JSONB NOT NULL DEFAULT '[]'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kanban_state_client_id ON kanban_state(client_id);
CREATE INDEX IF NOT EXISTS idx_kanban_state_run_id ON kanban_state(run_id);

-- 8. Cost Logs table (Structure created empty for Phase 1 as specified)
CREATE TABLE IF NOT EXISTS cost_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id VARCHAR(64) NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    agent_name VARCHAR(100) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    model_or_service VARCHAR(100) NOT NULL,
    tokens_or_units INT NOT NULL DEFAULT 0,
    estimated_cost_usd NUMERIC(10, 6) NOT NULL DEFAULT 0.000000,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_cost_logs_client_id ON cost_logs(client_id);
CREATE INDEX IF NOT EXISTS idx_cost_logs_run_id ON cost_logs(run_id);

-- Enable Row Level Security (RLS) on all tables
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE ads ENABLE ROW LEVEL SECURITY;
ALTER TABLE concepts ENABLE ROW LEVEL SECURITY;
ALTER TABLE scripts ENABLE ROW LEVEL SECURITY;
ALTER TABLE videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE kanban_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE cost_logs ENABLE ROW LEVEL SECURITY;

