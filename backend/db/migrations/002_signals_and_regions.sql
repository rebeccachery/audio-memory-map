CREATE TABLE regions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    min_lat DOUBLE PRECISION NOT NULL,
    max_lat DOUBLE PRECISION NOT NULL,
    min_lon DOUBLE PRECISION NOT NULL,
    max_lon DOUBLE PRECISION NOT NULL,
    default_language TEXT NOT NULL DEFAULT 'en',
    write_token_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT regions_bbox_lat CHECK (min_lat < max_lat),
    CONSTRAINT regions_bbox_lon CHECK (min_lon < max_lon)
);

CREATE TABLE signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    region_id UUID NOT NULL REFERENCES regions(id),
    type TEXT NOT NULL CHECK (type IN ('need', 'update', 'hazard', 'resource', 'status')),
    urgency TEXT NOT NULL DEFAULT 'normal' CHECK (urgency IN ('critical', 'high', 'normal', 'info')),
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'verified', 'in_progress', 'resolved', 'stale')),
    title TEXT,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    geom GEOGRAPHY(POINT, 4326) GENERATED ALWAYS AS (
        ST_SetSRID(ST_MakePoint(lon, lat), 4326)::geography
    ) STORED,
    accuracy_m DOUBLE PRECISION,
    audio_ref TEXT NOT NULL,
    audio_duration_s DOUBLE PRECISION,
    language_detected TEXT,
    transcript_original TEXT DEFAULT '',
    categories TEXT[] DEFAULT '{}',
    reporter_hash TEXT,
    client_id TEXT,
    local_id TEXT,
    captured_at TIMESTAMPTZ,
    captured_offline BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    synced_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    embedding DOUBLE PRECISION[]
);

CREATE UNIQUE INDEX signals_client_local_unique
    ON signals (client_id, local_id)
    WHERE client_id IS NOT NULL AND local_id IS NOT NULL;

CREATE INDEX signals_region_created_idx ON signals (region_id, created_at DESC);
CREATE INDEX signals_geom_idx ON signals USING GIST (geom);
CREATE INDEX signals_status_urgency_idx ON signals (status, urgency);
