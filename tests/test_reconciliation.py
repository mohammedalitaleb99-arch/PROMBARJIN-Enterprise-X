import time

import pytest

from app import db
from app.reconciliation import init_reconciliation_db, reconcile


def setup_function():
    db.DB_PATH = __import__('pathlib').Path('/tmp/prombarjin-reconciliation-test.db')
    try:
        db.DB_PATH.unlink()
    except FileNotFoundError:
        pass
    db.DATABASE_URL = ''
    db.init_db()
    init_reconciliation_db()


def _batch(batch_id='batch-1', key='key-1'):
    return {
        'device_id': 'device-1',
        'sync_batch_id': batch_id,
        'operations': [{
            'local_id': 'local-1',
            'timestamp': int(time.time()),
            'event_type': 'OFFLINE_FACT_RECORDED',
            'idempotency_key': key,
            'payload': {'fact': 'offline event'},
        }],
    }


def test_accepts_and_then_deduplicates_batch_and_operation():
    first = reconcile(_batch(), actor='offline-sync-service')
    assert first['details'][0]['status'] == 'ACCEPTED'
    server_hash = first['details'][0]['server_hash']

    second = reconcile(_batch('batch-2'), actor='offline-sync-service')
    assert second['details'][0]['status'] == 'SKIPPED_DUPLICATE'
    assert second['details'][0]['server_hash'] == server_hash

    third = reconcile(_batch('batch-1'), actor='offline-sync-service')
    assert third['status'] == 'SKIPPED_BATCH_DUPLICATE'


def test_rejects_stale_event_and_quarantines_batch():
    batch = _batch()
    batch['operations'][0]['timestamp'] = 0
    with pytest.raises(ValueError, match='timestamp_outside_allowed_skew'):
        reconcile(batch, actor='offline-sync-service')

    with db.connect() as c:
        row = c.execute('SELECT status FROM reconciliation_batches WHERE sync_batch_id=?', ('batch-1',)).fetchone()
        assert dict(row)['status'] == 'QUARANTINED'


def test_idempotency_key_cannot_cross_devices():
    reconcile(_batch(), actor='offline-sync-service')
    other = _batch('batch-2')
    other['device_id'] = 'device-2'
    with pytest.raises(ValueError, match='idempotency_key_device_mismatch'):
        reconcile(other, actor='offline-sync-service')


def test_ledger_is_hash_chained():
    reconcile(_batch(), actor='offline-sync-service')
    second = _batch('batch-2', 'key-2')
    second['operations'][0]['local_id'] = 'local-2'
    reconcile(second, actor='offline-sync-service')

    with db.connect() as c:
        rows = c.execute('SELECT sequence,prev_hash,server_hash FROM reconciliation_ledger ORDER BY sequence').fetchall()
        assert len(rows) == 2
        assert rows[0]['prev_hash'] == '0' * 64
        assert rows[1]['prev_hash'] == rows[0]['server_hash']
