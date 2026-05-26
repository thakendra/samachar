"""SQLite schema, migration and connection helpers for samachar.ai."""
import sqlite3
import os
import time

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'samachar.db')

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT NOT NULL,
  email         TEXT UNIQUE,
  password_hash TEXT,
  ward          TEXT DEFAULT 'Ward 5, Lalitpur',
  language      TEXT DEFAULT 'en',
  theme         TEXT DEFAULT 'light',
  accent        TEXT DEFAULT '#C92A2A',
  density       TEXT DEFAULT 'comfortable',
  show_frame    INTEGER DEFAULT 1,
  plan          TEXT DEFAULT 'free',
  ai_quota      INTEGER DEFAULT 10,
  ai_quota_date TEXT,
  onboarded     INTEGER DEFAULT 0,
  avatar_color  TEXT DEFAULT '#14171C',
  streak_days   INTEGER DEFAULT 1,
  created_at    INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS articles (
  id              TEXT PRIMARY KEY,
  category        TEXT,
  tag             TEXT,
  source          TEXT,
  source_url      TEXT,
  source_color    TEXT DEFAULT '#14171C',
  title           TEXT NOT NULL,
  title_np        TEXT,
  dek             TEXT,
  icon            TEXT,
  img_label       TEXT,
  img_url         TEXT,
  bias            INTEGER DEFAULT 50,
  bias_label      TEXT DEFAULT 'Center',
  verified        INTEGER DEFAULT 0,
  verified_count  INTEGER DEFAULT 0,
  comments_count  INTEGER DEFAULT 0,
  likes           INTEGER DEFAULT 0,
  developing      INTEGER DEFAULT 0,
  is_video        INTEGER DEFAULT 0,
  body            TEXT,
  key_points      TEXT,
  why_matters     TEXT,
  full_text       TEXT,
  published_at    INTEGER,
  time_label      TEXT,
  scraped_at      INTEGER,
  ai_processed    INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_articles_tag       ON articles(tag);
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_source    ON articles(source);
CREATE INDEX IF NOT EXISTS idx_articles_ai        ON articles(ai_processed);

CREATE TABLE IF NOT EXISTS bookmarks (
  user_id     INTEGER NOT NULL,
  article_id  TEXT NOT NULL,
  created_at  INTEGER NOT NULL,
  PRIMARY KEY (user_id, article_id)
);

CREATE TABLE IF NOT EXISTS read_history (
  user_id     INTEGER NOT NULL,
  article_id  TEXT NOT NULL,
  read_at     INTEGER NOT NULL,
  PRIMARY KEY (user_id, article_id)
);

CREATE TABLE IF NOT EXISTS comments (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  article_id  TEXT NOT NULL,
  user_id     INTEGER,
  name        TEXT NOT NULL,
  initials    TEXT,
  place       TEXT,
  text        TEXT NOT NULL,
  likes       INTEGER DEFAULT 0,
  dislikes    INTEGER DEFAULT 0,
  verified    INTEGER DEFAULT 0,
  created_at  INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_comments_article ON comments(article_id, created_at DESC);

CREATE TABLE IF NOT EXISTS comment_reactions (
  user_id     INTEGER NOT NULL,
  comment_id  INTEGER NOT NULL,
  vote        INTEGER NOT NULL,
  PRIMARY KEY (user_id, comment_id)
);

CREATE TABLE IF NOT EXISTS ai_log (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id     INTEGER NOT NULL,
  question    TEXT NOT NULL,
  answer      TEXT NOT NULL,
  sources     TEXT,
  created_at  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS notifications (
  id          TEXT PRIMARY KEY,
  icon        TEXT,
  tone        TEXT,
  title       TEXT,
  sub         TEXT,
  created_at  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS notif_read (
  user_id     INTEGER NOT NULL,
  notif_id    TEXT NOT NULL,
  read_at     INTEGER NOT NULL,
  PRIMARY KEY (user_id, notif_id)
);

CREATE TABLE IF NOT EXISTS user_topics (
  user_id     INTEGER NOT NULL,
  topic_id    TEXT NOT NULL,
  PRIMARY KEY (user_id, topic_id)
);

CREATE TABLE IF NOT EXISTS trends (
  rank        INTEGER PRIMARY KEY,
  title       TEXT,
  sub         TEXT,
  heat        TEXT
);

CREATE TABLE IF NOT EXISTS scrape_log (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  run_at      INTEGER NOT NULL,
  sources_ok  TEXT,
  sources_err TEXT,
  new_articles INTEGER DEFAULT 0
);
"""

# Columns added after initial schema — safe to run on existing DB
_MIGRATIONS = [
    "ALTER TABLE articles ADD COLUMN source_url    TEXT",
    "ALTER TABLE articles ADD COLUMN source_color  TEXT DEFAULT '#14171C'",
    "ALTER TABLE articles ADD COLUMN full_text     TEXT",
    "ALTER TABLE articles ADD COLUMN scraped_at    INTEGER",
    "ALTER TABLE articles ADD COLUMN ai_processed  INTEGER DEFAULT 0",
    "ALTER TABLE articles ADD COLUMN img_url       TEXT",
    "ALTER TABLE users    ADD COLUMN email         TEXT",
    "ALTER TABLE users    ADD COLUMN password_hash TEXT",
    "ALTER TABLE users    ADD COLUMN avatar_color  TEXT DEFAULT '#14171C'",
    "ALTER TABLE users    ADD COLUMN streak_days   INTEGER DEFAULT 1",
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    conn.execute('PRAGMA journal_mode = WAL')
    return conn


def init_db():
    conn = get_db()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
        # Run migrations (ignore "duplicate column" errors)
        for sql in _MIGRATIONS:
            try:
                conn.execute(sql)
                conn.commit()
            except Exception:
                pass
    finally:
        conn.close()


def now():
    return int(time.time())


def row_to_dict(row):
    if row is None:
        return None
    return {k: row[k] for k in row.keys()}
