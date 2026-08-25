from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from .db import connect

GENESIS_HASH = '0' * 64


def init_reconciliation_db():
    with connect() as c:
        c.executescript('''CREATE TABLE IF NOT EXISTS reconciliation_events (id INTEGER PRIMARY KEY AUTOINCREMENT,event_id TEXT NOT NULL UNIQUE,aggregate_id TEXT NOT NULL,device_id TEXT NOT NULL,actor_id TEXT NOT NULL,base_version INTEGER NOT NULL,sequence_no INTEGER NOT NULL,client_timestamp TEXT NOT NULL,action TEXT NOT NULL,payload TEXT NOT NULL,payload_hash TEXT NOT NULL,prev_event_hash TEXT NOT NULL,integrity_hash TEXT NOT NULL,schema_version TEXT NOT NULL,idempotency_key TEXT NOT NULL UNIQUE,status TEXT NOT NULL,server_sequence INTEGER NOT NULL,server_received_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);CREATE INDEX IF NOT EXISTS idx_recon_aggregate ON reconciliation_events(aggregate_id,server_sequence);CREATE TABLE IF NOT EXISTS reconciliation_checkpoints (id INTEGER PRIMARY KEY CHECK(id=1),last_event_hash TEXT NOT NULL,last_server_sequence INTEGER NOT NULL);INSERT OR IGNORE INTO reconciliation_checkpoints(id,last_event_hash,last_server_sequence) VALUES (1,'0000000000000000000000000000000000000000000000000000000000000000',0);''')
        c.commit()


def get_event_by_idempotency(key):
    with connect() as c:
        row = c.execute('SELECT event_id,server_sequence,status FROM reconciliation_events WHERE idempotency_key=?',(key,)).fetchone()
        return dict(row) if row else None


def aggregate_version(aggregate_id):
    with connect() as c:
        row = c.execute("SELECT COALESCE(MAX(base_version + 1),0) AS v FROM reconciliation_events WHERE aggregate_id=? AND status IN ('ACCEPTED','MERGED')",(aggregate_id,)).fetchone()
        return int(row['v']) if row else 0


def deterministic_merge_possible(event):
    return event.action in {'SET_FIELD','PATCH_NON_OVERLAPPING'} and isinstance(event.payload.get('fields'),dict) and bool(event.payload['fields'])


def apply_reconciliation_event(event,status):
    with connect() as c:
        row=c.execute('SELECT last_event_hash,last_server_sequence FROM reconciliation_checkpoints WHERE id=1').fetchone()
        server_sequence=int(row['last_server_sequence'])+1
        prev_hash=str(row['last_event_hash'])
        event_hash=hashlib.sha256(f'{prev_hash}|{event.event_id}|{server_sequence}'.encode()).hexdigest()
        c.execute('''INSERT INTO reconciliation_events(event_id,aggregate_id,device_id,actor_id,base_version,sequence_no,client_timestamp,action,payload,payload_hash,prev_event_hash,integrity_hash,schema_version,idempotency_key,status,server_sequence,server_received_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',(event.event_id,event.aggregate_id,event.device_id,event.actor_id,event.base_version,event.sequence_no,event.client_timestamp,event.action,json.dumps(event.payload,sort_keys=True),event.payload_hash,prev_hash,event.integrity_hash,event.schema_version,event.idempotency_key,status,server_sequence,datetime.now(timezone.utc).isoformat()))
        c.execute('UPDATE reconciliation_checkpoints SET last_event_hash=?,last_server_sequence=? WHERE id=1',(event_hash,server_sequence))
        c.commit()
        return server_sequence


def ledger_verify():
    with connect() as c:
        rows=c.execute('SELECT * FROM reconciliation_events ORDER BY server_sequence').fetchall()
        previous=GENESIS_HASH
        for row in rows:
            expected=hashlib.sha256(f"{previous}|{row['event_id']}|{row['server_sequence']}".encode()).hexdigest()
            if row['prev_event_hash'] != previous or expected != hashlib.sha256(f"{row['prev_event_hash']}|{row['event_id']}|{row['server_sequence']}".encode()).hexdigest():
                return {'valid':False,'failed_at':row['server_sequence']}
            previous=expected
        return {'valid':True,'events':len(rows),'last_hash':previous}
