import hashlib
import json
import time
import uuid
from typing import Any

from .db import connect, _execute, _postgres

MAX_OPERATIONS = 500
MAX_PAYLOAD_BYTES = 512 * 1024
MAX_CLOCK_SKEW_SECONDS = 24 * 60 * 60


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _hash_event(prev_hash: str, event: dict[str, Any]) -> str:
    material = f"{prev_hash}|{_canonical(event)}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def init_reconciliation_db() -> None:
    with connect() as c:
        if _postgres():
            c.execute("CREATE TABLE IF NOT EXISTS reconciliation_batches (sync_batch_id TEXT PRIMARY KEY, device_id TEXT NOT NULL, received_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP, status TEXT NOT NULL, operation_count INTEGER NOT NULL, error TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS reconciliation_idempotency (idempotency_key TEXT PRIMARY KEY, local_id TEXT NOT NULL, device_id TEXT NOT NULL, server_hash TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP)")
            c.execute("CREATE TABLE IF NOT EXISTS reconciliation_ledger (sequence BIGSERIAL PRIMARY KEY, event_id TEXT UNIQUE NOT NULL, event_type TEXT NOT NULL, actor TEXT NOT NULL, device_id TEXT NOT NULL, local_id TEXT NOT NULL, idempotency_key TEXT NOT NULL, offline_timestamp BIGINT NOT NULL, reconciled_at DOUBLE PRECISION NOT NULL, prev_hash TEXT NOT NULL, server_hash TEXT UNIQUE NOT NULL, payload_json TEXT NOT NULL)")
            c.execute("CREATE TABLE IF NOT EXISTS reconciliation_quarantine (id BIGSERIAL PRIMARY KEY, sync_batch_id TEXT, device_id TEXT, reason TEXT NOT NULL, payload_json TEXT NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        else:
            c.executescript('''
                CREATE TABLE IF NOT EXISTS reconciliation_batches (sync_batch_id TEXT PRIMARY KEY, device_id TEXT NOT NULL, received_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, status TEXT NOT NULL, operation_count INTEGER NOT NULL, error TEXT);
                CREATE TABLE IF NOT EXISTS reconciliation_idempotency (idempotency_key TEXT PRIMARY KEY, local_id TEXT NOT NULL, device_id TEXT NOT NULL, server_hash TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
                CREATE TABLE IF NOT EXISTS reconciliation_ledger (sequence INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT UNIQUE NOT NULL, event_type TEXT NOT NULL, actor TEXT NOT NULL, device_id TEXT NOT NULL, local_id TEXT NOT NULL, idempotency_key TEXT NOT NULL, offline_timestamp INTEGER NOT NULL, reconciled_at REAL NOT NULL, prev_hash TEXT NOT NULL, server_hash TEXT UNIQUE NOT NULL, payload_json TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS reconciliation_quarantine (id INTEGER PRIMARY KEY AUTOINCREMENT, sync_batch_id TEXT, device_id TEXT, reason TEXT NOT NULL, payload_json TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            ''')
        c.commit()


def _ledger_tail(c) -> str:
    row = _execute(c, "SELECT server_hash FROM reconciliation_ledger ORDER BY sequence DESC LIMIT 1").fetchone()
    return (dict(row)["server_hash"] if row else "0" * 64)


def _quarantine(c, batch_id: str | None, device_id: str | None, reason: str, payload: Any) -> None:
    _execute(c, "INSERT INTO reconciliation_quarantine(sync_batch_id,device_id,reason,payload_json) VALUES (?,?,?,?)", (batch_id, device_id, reason, _canonical(payload)))


def reconcile(batch: dict[str, Any], actor: str) -> dict[str, Any]:
    batch_id = batch.get("sync_batch_id")
    device_id = batch.get("device_id")
    operations = batch.get("operations")
    if not isinstance(batch_id, str) or not batch_id or not isinstance(device_id, str) or not device_id:
        raise ValueError("invalid_batch_identity")
    if not isinstance(operations, list) or len(operations) > MAX_OPERATIONS:
        raise ValueError("invalid_operation_count")
    if len(_canonical(batch).encode("utf-8")) > MAX_PAYLOAD_BYTES:
        raise ValueError("payload_too_large")

    now = int(time.time())
    results: list[dict[str, Any]] = []
    with connect() as c:
        if _postgres():
            c.execute("SELECT pg_advisory_xact_lock(918273645)")
        else:
            c.execute("BEGIN IMMEDIATE")
        existing_batch = _execute(c, "SELECT status FROM reconciliation_batches WHERE sync_batch_id=?", (batch_id,)).fetchone()
        if existing_batch:
            status = dict(existing_batch)["status"]
            c.rollback()
            return {"sync_batch_id": batch_id, "status": "SKIPPED_BATCH_DUPLICATE", "batch_status": status, "processed_count": 0, "details": []}

        _execute(c, "INSERT INTO reconciliation_batches(sync_batch_id,device_id,status,operation_count) VALUES (?,?,?,?)", (batch_id, device_id, "PROCESSING", len(operations)))
        try:
            prev_hash = _ledger_tail(c)
            for op in operations:
                if not isinstance(op, dict):
                    raise ValueError("invalid_operation")
                local_id = op.get("local_id")
                key = op.get("idempotency_key")
                event_type = op.get("event_type")
                timestamp = op.get("timestamp")
                payload = op.get("payload", {})
                if not all(isinstance(x, str) and x for x in (local_id, key, event_type)) or not isinstance(timestamp, int) or not isinstance(payload, dict):
                    raise ValueError("invalid_operation_schema")
                if abs(now - timestamp) > MAX_CLOCK_SKEW_SECONDS:
                    raise ValueError("timestamp_outside_allowed_skew")
                if len(_canonical(payload).encode("utf-8")) > MAX_PAYLOAD_BYTES:
                    raise ValueError("operation_payload_too_large")

                duplicate = _execute(c, "SELECT server_hash,device_id FROM reconciliation_idempotency WHERE idempotency_key=?", (key,)).fetchone()
                if duplicate:
                    d = dict(duplicate)
                    if d["device_id"] != device_id:
                        raise ValueError("idempotency_key_device_mismatch")
                    results.append({"local_id": local_id, "status": "SKIPPED_DUPLICATE", "server_hash": d["server_hash"]})
                    continue

                reconciled_at = time.time()
                event = {"event_type": f"RECONCILED::{event_type}", "actor": actor, "device_id": device_id, "local_id": local_id, "idempotency_key": key, "offline_timestamp": timestamp, "reconciled_at": reconciled_at, "payload": payload}
                server_hash = _hash_event(prev_hash, event)
                _execute(c, "INSERT INTO reconciliation_ledger(event_id,event_type,actor,device_id,local_id,idempotency_key,offline_timestamp,reconciled_at,prev_hash,server_hash,payload_json) VALUES (?,?,?,?,?,?,?,?,?,?,?)", (str(uuid.uuid4()), event["event_type"], actor, device_id, local_id, key, timestamp, reconciled_at, prev_hash, server_hash, _canonical(payload)))
                _execute(c, "INSERT INTO reconciliation_idempotency(idempotency_key,local_id,device_id,server_hash) VALUES (?,?,?,?)", (key, local_id, device_id, server_hash))
                prev_hash = server_hash
                results.append({"local_id": local_id, "status": "ACCEPTED", "server_hash": server_hash})
            _execute(c, "UPDATE reconciliation_batches SET status=? WHERE sync_batch_id=?", ("COMPLETED", batch_id))
            c.commit()
        except Exception as exc:
            _quarantine(c, batch_id, device_id, type(exc).__name__ + ":" + str(exc), batch)
            _execute(c, "UPDATE reconciliation_batches SET status=?,error=? WHERE sync_batch_id=?", ("QUARANTINED", str(exc), batch_id))
            c.commit()
            raise

    return {"sync_batch_id": batch_id, "status": "COMPLETED", "processed_count": len(results), "details": results}
