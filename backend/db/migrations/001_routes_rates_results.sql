-- 001: routes, route_rates, analysis_results

CREATE TABLE IF NOT EXISTS routes (
    id                  SERIAL PRIMARY KEY,
    route_code          TEXT UNIQUE NOT NULL,
    mode                TEXT NOT NULL CHECK (mode IN ('sea', 'rail', 'road', 'air', 'multimodal')),
    origin              TEXT NOT NULL,
    destination         TEXT NOT NULL,
    distance_km         DOUBLE PRECISION,
    transit_days_base   INTEGER,
    border_crossings    INTEGER DEFAULT 0,
    port_calls          INTEGER DEFAULT 0,
    gauge_change_count  INTEGER DEFAULT 0,
    carrier             TEXT,
    active              BOOLEAN NOT NULL DEFAULT TRUE,
    meta                JSONB DEFAULT '{}'::jsonb,
    created_at          TIMESTAMP NOT NULL DEFAULT now(),
    updated_at          TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_routes_mode        ON routes (mode);
CREATE INDEX IF NOT EXISTS idx_routes_origin_dest ON routes (origin, destination);

CREATE TABLE IF NOT EXISTS route_rates (
    id                  SERIAL PRIMARY KEY,
    route_id            INTEGER NOT NULL REFERENCES routes(id) ON DELETE CASCADE,
    rate_usd            DOUBLE PRECISION NOT NULL,
    unit                TEXT NOT NULL DEFAULT 'per_teu' CHECK (unit IN ('per_teu', 'per_ton', 'per_container', 'per_shipment')),
    source              TEXT NOT NULL,
    valid_from          TIMESTAMP NOT NULL,
    valid_to            TIMESTAMP,
    fetched_at          TIMESTAMP NOT NULL DEFAULT now(),
    raw                 JSONB
);

CREATE INDEX IF NOT EXISTS idx_route_rates_route_valid ON route_rates (route_id, valid_from DESC);
CREATE INDEX IF NOT EXISTS idx_route_rates_source      ON route_rates (source);

CREATE TABLE IF NOT EXISTS analysis_results (
    id            SERIAL PRIMARY KEY,
    analysis_id   INTEGER NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    route_id      INTEGER REFERENCES routes(id) ON DELETE SET NULL,
    route_code    TEXT,
    mode          TEXT,
    origin        TEXT,
    destination   TEXT,
    cost_usd      DOUBLE PRECISION NOT NULL,
    time_days     INTEGER NOT NULL,
    risk_index    DOUBLE PRECISION NOT NULL,
    emissions     DOUBLE PRECISION NOT NULL,
    score         DOUBLE PRECISION NOT NULL,
    breakdown     JSONB NOT NULL,
    created_at    TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_analysis_results_analysis ON analysis_results (analysis_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_route    ON analysis_results (route_id);
CREATE INDEX IF NOT EXISTS idx_analysis_results_score    ON analysis_results (score DESC);
