# PROMBARJIN Ω Enterprise X

Persistent, local-first executive intelligence workspace based on the supplied PROMBARJIN Ω Enterprise X specification.

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Open http://localhost:8000

## Run with Docker
```bash
cp .env.example .env
# Put OPENAI_API_KEY in .env only when model-backed responses are needed.
docker compose up --build -d
```
The SQLite database lives in the `prombarjin_data` named volume and survives container restarts.

## Tests
```bash
pytest -q
```

## Architecture
`UI -> API -> Orchestrator -> Domain Routing -> Model Adapter -> Quality Gate -> Persistent Ledger`

The design deliberately keeps the policy/specification separate from the model provider so the system can evolve without rewriting the core runtime.
