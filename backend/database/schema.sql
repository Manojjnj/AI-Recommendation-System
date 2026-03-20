-- ============================================================
-- E-Commerce Recommendation System – PostgreSQL Schema
-- ============================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ----------------------------------------------------------------
-- USERS
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(120)        NOT NULL,
    email       VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    avatar_url  TEXT,
    created_at  TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ         NOT NULL DEFAULT NOW()
);

-- ----------------------------------------------------------------
-- PRODUCTS
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(255)    NOT NULL,
    category     VARCHAR(100)    NOT NULL,
    description  TEXT            NOT NULL,
    price        NUMERIC(10, 2)  NOT NULL CHECK (price >= 0),
    image_url    TEXT,
    stock        INTEGER         NOT NULL DEFAULT 0 CHECK (stock >= 0),
    rating_avg   NUMERIC(3, 2)   DEFAULT 0.0,
    created_at   TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

-- ----------------------------------------------------------------
-- INTERACTIONS
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS interactions (
    id               SERIAL PRIMARY KEY,
    user_id          INTEGER         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id       INTEGER         NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    rating           NUMERIC(3, 1)   CHECK (rating >= 1.0 AND rating <= 5.0),
    interaction_type VARCHAR(20)     NOT NULL DEFAULT 'view'
                         CHECK (interaction_type IN ('view','click','purchase','wishlist')),
    timestamp        TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, product_id)     -- one record per user-product pair
);

CREATE INDEX IF NOT EXISTS idx_interactions_user    ON interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_interactions_product ON interactions(product_id);
CREATE INDEX IF NOT EXISTS idx_interactions_ts      ON interactions(timestamp DESC);

-- ----------------------------------------------------------------
-- AB TESTS  (bonus feature)
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ab_experiments (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    variant_a   VARCHAR(80)  NOT NULL,  -- e.g. 'collaborative'
    variant_b   VARCHAR(80)  NOT NULL,  -- e.g. 'content_based'
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ab_assignments (
    id             SERIAL PRIMARY KEY,
    experiment_id  INTEGER NOT NULL REFERENCES ab_experiments(id) ON DELETE CASCADE,
    user_id        INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    variant        CHAR(1) NOT NULL CHECK (variant IN ('A','B')),
    assigned_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (experiment_id, user_id)
);

-- ----------------------------------------------------------------
-- ANALYTICS EVENTS  (bonus feature)
-- ----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS analytics_events (
    id          BIGSERIAL PRIMARY KEY,
    user_id     INTEGER      REFERENCES users(id) ON DELETE SET NULL,
    event_type  VARCHAR(50)  NOT NULL,
    properties  JSONB        NOT NULL DEFAULT '{}',
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_analytics_user  ON analytics_events(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_type  ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_props ON analytics_events USING gin(properties);

-- ----------------------------------------------------------------
-- Helper: auto-update updated_at
-- ----------------------------------------------------------------
CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$ BEGIN
  CREATE TRIGGER set_timestamp_users
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TRIGGER set_timestamp_products
    BEFORE UPDATE ON products
    FOR EACH ROW EXECUTE PROCEDURE trigger_set_timestamp();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;