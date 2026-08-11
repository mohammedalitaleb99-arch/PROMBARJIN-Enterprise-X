import os
import sqlite3
from pathlib import Path

DATABASE_URL = os.getenv('DATABASE_URL', '').strip()
DB_PATH = Path(os.getenv('PROMBARJIN_DB', '/data/prombarjin.db'))


def _postgres():
    return bool(DATABASE_URL)


def connect():
    if _postgres():
        import psycopg
        from psycopg.rows import dict_row
        return psycopg.connect(DATABASE_URL, row_factory=dict_row)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _execute(conn, sql, params=()):
    return conn.execute(sql.replace('?', '%s'), params) if _postgres() else conn.execute(sql, params)


def init_db():
    with connect() as c:
        if _postgres():
            c.execute('CREATE TABLE IF NOT EXISTS memories (id BIGSERIAL PRIMARY KEY, key TEXT NOT NULL, value TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP)')
            c.execute('CREATE TABLE IF NOT EXISTS decisions (id BIGSERIAL PRIMARY KEY, title TEXT NOT NULL, rationale TEXT NOT NULL, confidence INTEGER NOT NULL, status TEXT NOT NULL DEFAULT \'active\', created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP)')
            c.execute('CREATE TABLE IF NOT EXISTS conversations (id BIGSERIAL PRIMARY KEY, role TEXT NOT NULL, content TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at)')
        else:
            c.executescript('''CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY AUTOINCREMENT,key TEXT NOT NULL,value TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);CREATE TABLE IF NOT EXISTS decisions (id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,rationale TEXT NOT NULL,confidence INTEGER NOT NULL,status TEXT NOT NULL DEFAULT 'active',created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY AUTOINCREMENT,role TEXT NOT NULL,content TEXT NOT NULL,created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key);CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at);''')
        c.commit()


def add_memory(key, value):
    with connect() as c:
        _execute(c, 'INSERT INTO memories(key,value) VALUES (?,?)', (key, value)); c.commit()


def get_memories(limit=100):
    with connect() as c:
        return [dict(r) for r in _execute(c, 'SELECT * FROM memories ORDER BY id DESC LIMIT ?', (limit,)).fetchall()]


def add_decision(title, rationale, confidence):
    with connect() as c:
        _execute(c, 'INSERT INTO decisions(title,rationale,confidence) VALUES (?,?,?)', (title, rationale, confidence)); c.commit()


def get_decisions(limit=50):
    with connect() as c:
        return [dict(r) for r in _execute(c, 'SELECT * FROM decisions ORDER BY id DESC LIMIT ?', (limit,)).fetchall()]


def add_message(role, content):
    with connect() as c:
        _execute(c, 'INSERT INTO conversations(role,content) VALUES (?,?)', (role, content)); c.commit()


def get_messages(limit=30):
    with connect() as c:
        rows = [dict(r) for r in _execute(c, 'SELECT * FROM conversations ORDER BY id DESC LIMIT ?', (limit,)).fetchall()]
        return rows[::-1]
