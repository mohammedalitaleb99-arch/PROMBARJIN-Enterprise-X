from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from ..reconciliation_store import aggregate_version, apply_reconciliation_event, deterministic_merge_possible, get_event_by_idempotency
from ..models.reconciliation import ConflictStatus, EventEnvelope, payload_digest


class GovernedReconciliationEngine:
    """Server-authoritative deterministic reconciliation; AI never commits state."""
    def process_event_batch(self, events: list[EventEnvelope]) -> dict[str, Any]:
        results=[]
        metrics={"accepted":0,"merged":0,"review_required":0,"rejected":0,"duplicates":0}
        for event in sorted(events,key=lambda e:(e.aggregate_id,e.base_version,e.sequence_no,e.event_id)):
            if event.payload_hash != payload_digest(event.payload) or event.integrity_hash != event.calculate_integrity_hash():
                results.append(self._ack(event,ConflictStatus.REJECTED_GOVERNANCE,"Integrity validation failed.")); metrics["rejected"]+=1; continue
            duplicate=get_event_by_idempotency(event.idempotency_key)
            if duplicate:
                results.append(self._ack(event,ConflictStatus.DUPLICATE_SKIPPED,"Idempotency key already processed.",duplicate["server_sequence"])); metrics["duplicates"]+=1; continue
            current=aggregate_version(event.aggregate_id)
            if event.base_version == current:
                seq=apply_reconciliation_event(event,"ACCEPTED"); results.append(self._ack(event,ConflictStatus.ACCEPTED,"Applied at current aggregate version.",seq)); metrics["accepted"]+=1
            elif event.base_version < current and deterministic_merge_possible(event):
                seq=apply_reconciliation_event(event,"MERGED"); results.append(self._ack(event,ConflictStatus.MERGED,f"Deterministic merge at server version {current}.",seq)); metrics["merged"]+=1
            elif event.base_version < current:
                results.append(self._ack(event,ConflictStatus.NEEDS_HUMAN_REVIEW,f"Version conflict: client base v{event.base_version} < server v{current}.")); metrics["review_required"]+=1
            else:
                results.append(self._ack(event,ConflictStatus.REJECTED_GOVERNANCE,f"Client base v{event.base_version} is ahead of server v{current}.")); metrics["rejected"]+=1
        return {"batch_ack":results,"telemetry_summary":metrics}

    @staticmethod
    def _ack(event,status,reason,server_sequence=None):
        return {"event_id":event.event_id,"idempotency_key":event.idempotency_key,"status":status.value,"server_sequence":server_sequence,"server_received_at":datetime.now(timezone.utc).isoformat(),"reason":reason}
