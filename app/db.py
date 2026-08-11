import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv('PROMBARJIN_DB', '/data/promb arjin.db'))


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS memories (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          key TEXT NOT NULL,
          value TEXT NOT NULL,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS decisions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          title TEXT NOT NULL,
          rationale TEXT NOT NULL,
          confidence INTEGER NOT NULL,
          status TEXT NOT NULL DEFAULT 'active',
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS conversations (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          role TEXT NOT NULL,
          content TEXT NOT NULL,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key);
        CREATE INDEX IF NOT EXISTS idx_conversations_created ON conversations(created_at);
        ''')


def add_memory(key, value):
    with connect() as c:
        c.execute('INSERT INTO memories(key,value) VALUES (?,?)', (key, value))


def get_memories(limit=100):
    with connect() as c:
        return [dict(r) for r in c.execute('SELECT * FROM memories ORDER BY id DESC LIMIT ?', (limit,)).fetchall()]


def add_decision(title, rationale, confidence):
    with connect() as c:
        c.execute('INSERT INTO decisions(title,rationale,confidence) VALUES (?,?,?)', (title, rationale, confidence))


def get_decisions(limit=50):
    with connect() as c:
        return [dict(r) for r in c.execute('SELECT * FROM decisions ORDER BY id DESC LIMIT ?', (limit,)).fetchall()]


def add_message(role, content):
    with connect() as c:
        c.execute('INSERT INTO conversations(role,content) VALUES (?,?)', (role, content))


def get_messages(limit=30):
    with connect() as c:
        return [dict(r) for r in c.execute('SELECT * FROM conversations ORDER BY id DESC LIMIT ?', (limit,)).fetchall()][::-1]
