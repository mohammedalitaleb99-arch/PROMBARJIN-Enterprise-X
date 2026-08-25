from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class ConflictStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    MERGED = "MERGED"
    NEEDS_HUMAN_REVIEW = "NEEDS_HUMAN_REVIEW"
    REJECTED_GOVERNANCE = "REJECTED_GOVERNANCE"
    DUPLICATE_SKIPPED = "DUPLICATE_SKIPPED"


def payload_digest(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class EventEnvelope(BaseModel):
    event_id: str = Field(min_length=1, max_length=128)
    aggregate_id: str = Field(min_length=1, max_length=128)
    device_id: str = Field(min_length=1, max_length=128)
    actor_id: str = Field(min_length=1, max_length=128)
    base_version: int = Field(ge=0)
    sequence_no: int = Field(ge=1)
    client_timestamp: str
    action: str = Field(min_length=1, max_length=128)
    payload: dict[str, Any]
    payload_hash: str = Field(min_length=64, max_length=64)
    prev_event_hash: str = Field(min_length=64, max_length=64)
    integrity_hash: str | None = None
    schema_version: str = "1.0"
    idempotency_key: str = Field(min_length=1, max_length=256)

    def calculate_integrity_hash(self) -> str:
        canonical = "|".join([
            self.event_id,
            self.aggregate_id,
            self.device_id,
            self.actor_id,
            str(self.base_version),
            str(self.sequence_no),
            self.action,
            self.payload_hash,
            self.prev_event_hash,
            self.schema_version,
            self.idempotency_key,
        ])
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def integrity_valid(self) -> bool:
        return self.payload_hash == payload_digest(self.payload) and self.integrity_hash == self.calculate_integrity_hash()


class ReconcileBatch(BaseModel):
    events: list[EventEnvelope] = Field(min_length=1, max_length=500)


class BatchAck(BaseModel):
    event_id: str
    idempotency_key: str
    status: ConflictStatus
    server_sequence: int | None = None
    server_received_at: str
    reason: str


class ReconcileResponse(BaseModel):
    batch_ack: list[BatchAck]
    telemetry_summary: dict[str, int]
