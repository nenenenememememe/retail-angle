-- Retail Angle ledger schema (Postgres)

CREATE TABLE influencers (
    id              SERIAL PRIMARY KEY,
    handle          TEXT NOT NULL,
    platform        TEXT NOT NULL CHECK (platform IN ('reddit', 'instagram')),
    claimed_perf    TEXT,               -- the influencer's own claim, e.g. "+200% this year"
    claim_source    TEXT,               -- URL or screenshot path backing the claim
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (handle, platform)
);

CREATE TABLE callouts (
    id              SERIAL PRIMARY KEY,
    influencer_id   INTEGER NOT NULL REFERENCES influencers(id),
    ticker          TEXT NOT NULL,      -- e.g. 'SOFI'
    direction       TEXT NOT NULL CHECK (direction IN ('BUY', 'SELL')),
    called_at       TIMESTAMPTZ NOT NULL,
    price_at_call   NUMERIC,            -- close on call date, filled by price job
    post_url        TEXT NOT NULL,
    reasoning       TEXT,               -- influencer's stated thesis, summarized
    claim           TEXT,               -- performance claim attached to this call, if any
    status          TEXT NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open', 'reversed', 'removed')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE prices (
    ticker          TEXT NOT NULL,
    day             DATE NOT NULL,
    close           NUMERIC NOT NULL,
    PRIMARY KEY (ticker, day)
);

CREATE TABLE insider_flags (
    id              SERIAL PRIMARY KEY,
    callout_id      INTEGER NOT NULL REFERENCES callouts(id),
    flag            TEXT NOT NULL,      -- e.g. 'cluster_buy', 'cluster_sell'
    detail          TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
