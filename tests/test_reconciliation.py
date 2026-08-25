from datetime import datetime, timezone
from uuid import uuid4

from app.models.reconciliation import EventEnvelope, payload_digest
from app.core.reconciliation import GovernedReconciliationEngine
from app.reconciliation_store import init_reconciliation_db, ledger_verify


def make_event(event_id=None, aggregate=None, base=0, seq=1, action='SET_FIELD', idem=None):
    event_id=event_id or str(uuid4()); aggregate=aggregate or ('a-'+str(uuid4())); idem=idem or str(uuid4())
    payload={'fields':{'risk':'LOW'}}
    e=EventEnvelope(event_id=event_id,aggregate_id=aggregate,device_id='d1',actor_id='u1',base_version=base,sequence_no=seq,client_timestamp=datetime.now(timezone.utc).isoformat(),action=action,payload=payload,payload_hash=payload_digest(payload),prev_event_hash='0'*64,schema_version='1.0',idempotency_key=idem)
    e.integrity_hash=e.calculate_integrity_hash()
    return e


def test_accept_and_idempotency(tmp_path, monkeypatch):
    monkeypatch.setenv('PROMBARJIN_DB', str(tmp_path/'test.db')); init_reconciliation_db(); engine=GovernedReconciliationEngine()
    event=make_event(); first=engine.process_event_batch([event]); assert first['telemetry_summary']['accepted']==1
    second=engine.process_event_batch([event]); assert second['telemetry_summary']['duplicates']==1; assert ledger_verify()['valid']


def test_tamper_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv('PROMBARJIN_DB', str(tmp_path/'test.db')); init_reconciliation_db(); e=make_event(); e.payload['fields']['risk']='HIGH'
    result=GovernedReconciliationEngine().process_event_batch([e]); assert result['telemetry_summary']['rejected']==1


def test_version_conflict_goes_to_review(tmp_path, monkeypatch):
    monkeypatch.setenv('PROMBARJIN_DB', str(tmp_path/'test.db')); init_reconciliation_db(); engine=GovernedReconciliationEngine(); aggregate='conflict-'+str(uuid4())
    assert engine.process_event_batch([make_event(aggregate=aggregate)])['telemetry_summary']['accepted']==1
    conflict=make_event(aggregate=aggregate,base=0,action='UPDATE_RECORD')
    result=engine.process_event_batch([conflict]); assert result['telemetry_summary']['review_required']==1
