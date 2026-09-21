-- toolbox schema v0.1 (T1) — SSOT for toolbox/index.sqlite3
-- Proposal: .sandbox/meta_harness_toolbox_idea.md §5
CREATE TABLE IF NOT EXISTS categories(id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS tools(
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL REFERENCES categories(id),
  bash_entry TEXT NOT NULL,
  python_impl TEXT NOT NULL,
  description TEXT NOT NULL,
  tags TEXT NOT NULL DEFAULT '',
  version TEXT NOT NULL DEFAULT '0.1.0',
  deprecated_by TEXT,
  uses INTEGER NOT NULL DEFAULT 0,
  successes INTEGER NOT NULL DEFAULT 0,
  created_by TEXT,
  created_at TEXT,
  promoted_at TEXT
);
CREATE VIRTUAL TABLE IF NOT EXISTS tools_fts USING fts5(name, description, tags, content='tools', content_rowid='rowid');
CREATE TABLE IF NOT EXISTS usage_log(ts TEXT, tool_id TEXT, session TEXT, ok INTEGER, ms INTEGER, note TEXT);
CREATE TABLE IF NOT EXISTS proposals(id TEXT PRIMARY KEY, title TEXT, category TEXT, motive TEXT,
  status TEXT DEFAULT 'staged',
  draft_path TEXT, uses_seen INTEGER DEFAULT 1, created_at TEXT);
CREATE TABLE IF NOT EXISTS toolbox_meta(k TEXT PRIMARY KEY, v TEXT);
