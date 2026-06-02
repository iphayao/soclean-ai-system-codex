CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS brands (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  name TEXT NOT NULL,
  slug TEXT NOT NULL UNIQUE,
  description TEXT,
  voice TEXT,
  compliance_notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS products (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  brand_id TEXT NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  slug TEXT NOT NULL UNIQUE,
  category TEXT NOT NULL,
  description TEXT,
  key_benefits JSONB NOT NULL DEFAULT '[]'::jsonb,
  price_cents INTEGER,
  active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS campaigns (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  brand_id TEXT NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  objective TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft',
  start_date DATE,
  end_date DATE,
  target_audience TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS content_items (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  campaign_id TEXT NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  product_id TEXT REFERENCES products(id) ON DELETE SET NULL,
  title TEXT NOT NULL,
  channel TEXT NOT NULL,
  format TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft',
  body TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS approvals (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  content_item_id TEXT NOT NULL REFERENCES content_items(id) ON DELETE CASCADE,
  reviewer_name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  feedback TEXT,
  decided_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_runs (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  campaign_id TEXT NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  workflow_name TEXT NOT NULL DEFAULT 'content_factory',
  status TEXT NOT NULL DEFAULT 'running',
  retry_count INTEGER NOT NULL DEFAULT 0,
  run_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  output_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS agent_run_steps (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  agent_run_id TEXT NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
  step_order INTEGER NOT NULL,
  step_name TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'completed',
  input_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  output_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  error TEXT,
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS brand_memories (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
  brand_id TEXT NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_products_brand_id ON products(brand_id);
CREATE INDEX IF NOT EXISTS idx_campaigns_brand_id ON campaigns(brand_id);
CREATE INDEX IF NOT EXISTS idx_content_items_campaign_id ON content_items(campaign_id);
CREATE INDEX IF NOT EXISTS idx_approvals_content_item_id ON approvals(content_item_id);
CREATE INDEX IF NOT EXISTS idx_agent_runs_campaign_id ON agent_runs(campaign_id);
CREATE INDEX IF NOT EXISTS idx_agent_run_steps_agent_run_id ON agent_run_steps(agent_run_id);
CREATE INDEX IF NOT EXISTS idx_brand_memories_embedding ON brand_memories USING ivfflat (embedding vector_cosine_ops);

INSERT INTO brands (id, name, slug, description, voice, compliance_notes)
VALUES (
  'brand-soclean',
  'SoClean',
  'soclean',
  'SoClean builds premium cleaning and sanitization systems for people who want easy, consistent daily upkeep.',
  'Clear, helpful, confident, and practical. Avoid hype; focus on ease, routine, freshness, and peace of mind.',
  'Do not make unverified medical claims. Avoid promising disease prevention or treatment. Keep claims tied to product documentation.'
)
ON CONFLICT (slug) DO NOTHING;

INSERT INTO products (id, brand_id, name, slug, category, description, key_benefits, price_cents, active)
VALUES
  (
    'product-soclean-3',
    'brand-soclean',
    'SoClean 3',
    'soclean-3',
    'CPAP maintenance',
    'A connected daily maintenance system designed to simplify CPAP equipment upkeep.',
    '["Automated daily routine", "Modern connected experience", "Designed for CPAP equipment care"]'::jsonb,
    39900,
    true
  ),
  (
    'product-soclean-air',
    'brand-soclean',
    'SoClean Air',
    'soclean-air',
    'Air purification',
    'A home air purification product focused on fresher everyday spaces.',
    '["Cleaner-feeling home air", "Quiet daily operation", "Simple household setup"]'::jsonb,
    29900,
    true
  )
ON CONFLICT (slug) DO NOTHING;

INSERT INTO campaigns (id, brand_id, name, objective, status, start_date, end_date, target_audience)
VALUES
  (
    'campaign-spring-refresh',
    'brand-soclean',
    'Spring Refresh',
    'Increase awareness of SoClean products as part of a simple seasonal cleaning reset.',
    'active',
    '2026-03-01',
    '2026-05-31',
    'Current and prospective customers who value low-friction home care routines.'
  ),
  (
    'campaign-cpap-routine',
    'brand-soclean',
    'CPAP Routine Confidence',
    'Educate CPAP users about consistent equipment maintenance routines without making medical claims.',
    'draft',
    '2026-06-15',
    '2026-08-31',
    'CPAP users and caregivers looking for practical daily upkeep guidance.'
  )
ON CONFLICT (id) DO NOTHING;

INSERT INTO content_items (id, campaign_id, product_id, title, channel, format, status, body, metadata)
VALUES
  (
    'content-spring-email',
    'campaign-spring-refresh',
    'product-soclean-air',
    'Refresh the Rooms You Use Every Day',
    'email',
    'newsletter',
    'in_review',
    'A concise seasonal email draft about adding air purification to a spring cleaning routine.',
    '{"tone": "practical", "approval_required": true}'::jsonb
  ),
  (
    'content-cpap-social',
    'campaign-cpap-routine',
    'product-soclean-3',
    'A Simpler Daily CPAP Upkeep Habit',
    'social',
    'linkedin_post',
    'draft',
    'A draft social post focused on habit formation and ease of use.',
    '{"tone": "educational", "approval_required": true}'::jsonb
  )
ON CONFLICT (id) DO NOTHING;

INSERT INTO approvals (id, content_item_id, reviewer_name, status, feedback, decided_at)
VALUES
  (
    'approval-spring-email',
    'content-spring-email',
    'Brand Review',
    'pending',
    'Confirm seasonal language and keep product claims conservative.',
    NULL
  )
ON CONFLICT (id) DO NOTHING;

INSERT INTO brand_memories (id, brand_id, title, content, embedding)
VALUES
  (
    'memory-soclean-voice',
    'brand-soclean',
    'SoClean Voice',
    'SoClean content should be clear, practical, confident, and grounded in everyday cleaning routines.',
    NULL
  ),
  (
    'memory-soclean-compliance',
    'brand-soclean',
    'Compliance Boundary',
    'Avoid unsupported health or disease-prevention claims. Prefer routine, freshness, convenience, and documented product features.',
    NULL
  )
ON CONFLICT (id) DO NOTHING;
