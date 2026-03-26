-- E-Waste Plant Data Schema
-- Normalized from HTML research documents

PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    full_name TEXT NOT NULL,
    codes TEXT,
    items TEXT,
    priority INTEGER DEFAULT 3,          -- 1=essential, 2=recommended, 3=supplementary, 0=skip
    epr_min_per_tonne INTEGER,           -- Rs
    epr_max_per_tonne INTEGER,           -- Rs
    supply_level TEXT,
    market_volume TEXT,
    extra_machinery TEXT,
    machinery_trigger TEXT,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS materials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id TEXT NOT NULL REFERENCES categories(id),
    material TEXT NOT NULL,              -- gold, copper, aluminum, iron, plastic
    pct REAL NOT NULL,                   -- percentage composition
    price_per_unit REAL,                 -- Rs per unit
    unit TEXT DEFAULT 'kg',             -- kg or g
    UNIQUE(category_id, material)
);

CREATE TABLE IF NOT EXISTS machines (
    id INTEGER PRIMARY KEY,             -- CPCB Annexure 1 number (1-21)
    name TEXT NOT NULL,
    group_name TEXT NOT NULL,           -- core, appliance, specialized, support
    badge TEXT,
    price_min_lakhs REAL,
    price_max_lakhs REAL,
    power_kw_min REAL,
    power_kw_max REAL,
    capacity TEXT,
    description TEXT,
    specs TEXT
);

CREATE TABLE IF NOT EXISTS category_machines (
    category_id TEXT NOT NULL REFERENCES categories(id),
    machine_id INTEGER NOT NULL REFERENCES machines(id),
    requirement TEXT DEFAULT 'core',    -- core or extra
    PRIMARY KEY (category_id, machine_id)
);

CREATE TABLE IF NOT EXISTS configurations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    display_name TEXT,
    price_min_lakhs REAL,
    price_max_lakhs REAL,
    target_tpa INTEGER,
    description TEXT,
    recommended BOOLEAN DEFAULT 0
);

CREATE TABLE IF NOT EXISTS config_machines (
    config_id TEXT NOT NULL REFERENCES configurations(id),
    machine_id INTEGER NOT NULL REFERENCES machines(id),
    included BOOLEAN DEFAULT 1,
    PRIMARY KEY (config_id, machine_id)
);

CREATE TABLE IF NOT EXISTS revenue_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_id TEXT REFERENCES configurations(id),
    stream TEXT NOT NULL,
    yield_per_tonne_kg REAL,
    price_per_kg REAL,
    revenue_per_tonne REAL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS cost_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_id TEXT REFERENCES configurations(id),
    item TEXT NOT NULL,
    cost_per_tonne_min REAL,
    cost_per_tonne_max REAL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS sourcing_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id TEXT REFERENCES categories(id),
    source TEXT DEFAULT 'kabadiwala',
    percentage REAL,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS rental_locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT NOT NULL,
    rate_min_psf REAL,
    rate_max_psf REAL,
    monthly_800sqm_min_lakhs REAL,
    monthly_800sqm_max_lakhs REAL,
    pros TEXT,
    cons TEXT
);

CREATE TABLE IF NOT EXISTS space_zones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone_name TEXT NOT NULL,
    required_sqm INTEGER,
    contents TEXT
);

-- Full-text search index
CREATE VIRTUAL TABLE IF NOT EXISTS search_index USING fts5(
    entity_type,
    entity_id,
    title,
    content,
    tokenize='porter unicode61'
);

-- Vector embeddings (optional, populated by vectorize.py)
CREATE TABLE IF NOT EXISTS embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    text TEXT NOT NULL,
    embedding BLOB,
    model TEXT,
    UNIQUE(entity_type, entity_id)
);
