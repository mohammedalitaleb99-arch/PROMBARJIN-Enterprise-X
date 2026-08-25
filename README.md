# PROMBARJIN Ω Enterprise X v3

Enterprise executive intelligence runtime with a server-authoritative **Governed Offline Reconciliation Protocol (GORP)** and Android delivery through GitHub Actions.

## v3 capabilities
- Android/PWA executive workspace
- Local-first outbox with event IDs and idempotency keys
- Deterministic reconciliation using aggregate version + sequence, not client clock
- Conservative deterministic merge; ambiguous conflicts require human review
- Append-only cryptographic ledger with hash-chain checkpoint verification
- Advisory-only OpenAI conflict intelligence with safe fallback
- Existing OMEGA evidence, quality-gate, governance and executive runtime
- Backend tests + compile/security preflight + automated APK build

## Security boundary
The Android client never receives or embeds `OPENAI_API_KEY`. OpenAI access is server-side only through the backend environment/GitHub deployment secret.

## Local backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Tests
```bash
pytest -q
python -m compileall -q app
```

## Reconciliation API
`POST /api/v1/sync/reconcile`

`GET /api/v1/sync/ledger/verify`

The server is authoritative. Duplicate idempotency keys are skipped, integrity failures are rejected, deterministic non-overlapping patches may merge, and unresolved version conflicts are held for human review.

## Android artifact
GitHub Actions builds the debug artifact named **PROMBARJIN-OMEGA-ENTERPRISE-X-v3** and validates its Android package identity before upload.
