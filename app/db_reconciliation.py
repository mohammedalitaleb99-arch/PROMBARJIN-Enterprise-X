from __future__ import annotations

# Reconciliation persistence is isolated from the legacy application tables.
# This module is imported by app.db so SQLite and PostgreSQL share the same API.

from .db import (
    init_reconciliation_db,
    aggregate_version,
    deterministic_merge_possible,
    get_event_by_idempotency,
    apply_reconciliation_event,
)
