from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..db import (
    apply_reconciliation_event,
    aggregate_version,
    deterministic_merge_possible,
    get_event_by_idempotency,
    init_reconciliation_db,
)
from ..models.reconciliation import ConflictStatus, EventEnvelope, payload_digest


class GovernedReconciliationEngine:
    """Server-authoritative, deterministic offline reconciliation.

    Ordering is based on aggregate version + client sequence, never on client clock.
    AI is deliberately outside this decision path; ambiguous conflicts are held for
    human review rather than delegated to a model.
    """

    def __init__(self) -> None:
        init_reconciliation_db()

    def process_event_batch(self, events: list[EventEnvelope]) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        metrics = {"accepted": 0, "merged": 0, "review_required": 0, "rejected": 0, "duplicates": 0}

        for event in sorted(events, key=lambda e: (e.aggregate_id, e.base_version, e.sequence_no, e.event_id)):
            if event.payload_hash != payload_digest(event.payload) or event.integrity_hash != event.calculate_integrity_hash():
                results.append(self._ack(event, ConflictStatus.REJECTED_GOVERNANCE, "Integrity validation failed."))
                metrics["rejected"] += 1
                continue

            duplicate = get_event_by_idempotency(event.idempotency_key)
            if duplicate is not None:
                results.append(self._ack(event, ConflictStatus.DUPLICATE_SKIPPED, "Idempotency key already processed.", duplicate["server_sequence"]))
                metrics["duplicates"] += 1
                continue

            current = aggregate_version(event.aggregate_id)
            if event.base_version == current:
                server_seq = apply_reconciliation_event(event, "ACCEPTED")
                results.append(self._ack(event, ConflictStatus.ACCEPTED, "Applied at current aggregate version.", server_seq))
                metrics["accepted"] += 1
            elif event.base_version < current and deterministic_merge_possible(event):
                server_seq = apply_reconciliation_event(event, "MERGED")
                results.append(self._ack(event, ConflictStatus.MERGED, f"Deterministic non-overlapping merge at server version {current}.", server_seq))
                metrics["merged"] += 1
            elif event.base_version < current:
                results.append(self._ack(event, ConflictStatus.NEEDS_HUMAN_REVIEW, f"Version conflict: client base v{event.base_version} < server v{current}."))
                metrics["review_required"] += 1
            else:
                results.append(self._ack(event, ConflictStatus.REJECTED_GOVERNANCE, f"Client base v{event.base_version} is ahead of server v{current}."))
                metrics["rejected"] += 1

        return {"batch_ack": results, "telemetry_summary": metrics}

    @staticmethod
    def _ack(event: EventEnvelope, status: ConflictStatus, reason: str, server_sequence: int | None = None) -> dict[str, Any]:
        return {
            "event_id": event.event_id,
            "idempotency_key": event.idempotency_key,
            "status": status.value,
            "server_sequence": server_sequence,
            "server_received_at": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
        }
