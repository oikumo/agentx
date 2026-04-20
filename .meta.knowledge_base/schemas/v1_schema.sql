-- Schema v1.0.0 for Meta Project Harness Knowledge Base
-- Optimized for RAG + FTS5 + auto-evolution

-- Main entries table
CREATE TABLE IF NOT EXISTS entries (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK (type IN ('pattern', 'finding', 'correction', 'decision')),
    category TEXT NOT NULL CHECK (category IN ('workflow', 'code', 'test', 'docs', 'tool', 'architecture')),
    title TEXT NOT NULL,
    confidence REAL DEFAULT 0.5 CHECK (confidence >= 0.0 AND confidence <= 1.0),
    context TEXT,
    finding TEXT,
    solution TEXT,
    example TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP,
    reuse_count INTEGER DEFAULT 0,
    is_deprecated INTEGER DEFAULT 0,
    embedding BLOB
);

-- Create index for fast lookups
CREATE INDEX IF NOT EXISTS idx_entries_type ON entries(type);
CREATE INDEX IF NOT EXISTS idx_entries_category ON entries(category);
CREATE INDEX IF NOT EXISTS idx_entries_confidence ON entries(confidence);
CREATE INDEX IF NOT EXISTS idx_entries_created ON entries(created_at);
CREATE INDEX IF NOT EXISTS idx_entries_deprecated ON entries(is_deprecated);

-- Full-text search virtual table
CREATE VIRTUAL TABLE IF NOT EXISTS entries_fts USING fts5(
    title, context, finding, solution, example,
    content='entries',
    content_rowid='rowid'
);

-- Corrections table (auto-correction mechanism)
CREATE TABLE IF NOT EXISTS corrections (
    id TEXT PRIMARY KEY,
    entry_id TEXT NOT NULL REFERENCES entries(id),
    reason TEXT NOT NULL,
    new_finding TEXT,
    confidence_delta REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_resolved INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_corrections_entry ON corrections(entry_id);
CREATE INDEX IF NOT EXISTS idx_corrections_resolved ON corrections(is_resolved);

-- Relationships between entries
CREATE TABLE IF NOT EXISTS relationships (
    from_id TEXT NOT NULL REFERENCES entries(id),
    to_id TEXT NOT NULL REFERENCES entries(id),
    type TEXT NOT NULL CHECK (type IN ('references', 'contradicts', 'extends', 'depends_on')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (from_id, to_id, type)
);

CREATE INDEX IF NOT EXISTS idx_relationships_from ON relationships(from_id);
CREATE INDEX IF NOT EXISTS idx_relationships_to ON relationships(to_id);

-- Evolution log (auto-evolution tracking)
CREATE TABLE IF NOT EXISTS evolution_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL CHECK (event_type IN ('correction', 'merge', 'decay', 'archive', 'confidence_adjust', 'deprecate')),
    entry_id TEXT REFERENCES entries(id),
    old_value TEXT,
    new_value TEXT,
    reason TEXT,
    metadata TEXT  -- JSON
);

CREATE INDEX IF NOT EXISTS idx_evolution_timestamp ON evolution_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_evolution_type ON evolution_log(event_type);

-- Triggers for automatic FTS5 updates
CREATE TRIGGER IF NOT EXISTS entries_ai AFTER INSERT ON entries BEGIN
  INSERT INTO entries_fts(rowid, title, context, finding, solution, example)
  VALUES (new.rowid, new.title, new.context, new.finding, new.solution, new.example);
END;

CREATE TRIGGER IF NOT EXISTS entries_ad AFTER DELETE ON entries BEGIN
  INSERT INTO entries_fts(entries_fts, rowid, title, context, finding, solution, example)
  VALUES ('delete', old.rowid, old.title, old.context, old.finding, old.solution, old.example);
END;

CREATE TRIGGER IF NOT EXISTS entries_au AFTER UPDATE ON entries BEGIN
  INSERT INTO entries_fts(entries_fts, rowid, title, context, finding, solution, example)
  VALUES ('delete', old.rowid, old.title, old.context, old.finding, old.solution, old.example);
  INSERT INTO entries_fts(rowid, title, context, finding, solution, example)
  VALUES (new.rowid, new.title, new.context, new.finding, new.solution, new.example);
END;

-- View for active entries only
CREATE VIEW IF NOT EXISTS active_entries AS
SELECT * FROM entries WHERE is_deprecated = 0;

-- View for high-confidence entries
CREATE VIEW IF NOT EXISTS high_confidence_entries AS
SELECT * FROM entries WHERE confidence >= 0.8 AND is_deprecated = 0;
