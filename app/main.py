from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .db import init_db, add_message, get_messages, add_memory, get_memories, add_decision, get_decisions
from .ai import generate_reply
from .online import quote, fetch_public_source
from .omega_engine import build_runtime_context, final_quality_gate

BASE = Path(__file__).resolve().parent.parent
app = FastAPI(title='PROMBARJIN Ω Enterprise X', version='1.0.0')
app.mount('/static', StaticFiles(directory=BASE / 'static'), name='static')
init_db()

class ChatRequest(BaseModel):
    message: str

class MemoryRequest(BaseModel):
    key: str
    value: str

class DecisionRequest(BaseModel):
    title: str
    rationale: str
    confidence: int = 75

@app.on_event('startup')
def startup():
    init_db()

@app.get('/', response_class=HTMLResponse)
def home():
    return (BASE/'static/index.html').read_text(encoding='utf-8')

@app.get('/health')
def health():
    return {
        'status': 'ok',
        'service': 'prombarjin-enterprise-x',
        'internet_gateway': True,
        'market_gateway': True,
        'omega_runtime': True,
        'governance_gate': True,
    }

@app.get('/api/state')
def state():
    return {'memories': get_memories(), 'decisions': get_decisions(), 'messages': get_messages()}

@app.post('/api/memory')
def memory(req: MemoryRequest):
    add_memory(req.key, req.value)
    return {'status': 'saved'}

@app.post('/api/decision')
def decision(req: DecisionRequest):
    confidence = max(0, min(100, req.confidence))
    add_decision(req.title, req.rationale, confidence)
    return {'status': 'saved'}

@app.get('/api/market/quote')
def market_quote(symbol: str):
    try:
        return quote(symbol.upper())
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))

@app.get('/api/source')
def source(url: str):
    try:
        return fetch_public_source(url)
    except ValueError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))

@app.post('/api/chat')
def chat(req: ChatRequest):
    add_message('user', req.message)
    runtime = build_runtime_context(req.message)
    profile = runtime['profile']
    context = (
        'PROMBARJIN OMEGA EXECUTABLE MASTER RUNTIME. '
        'Priorities=P1 Truth>P2 Safety>P3 Accuracy>P4 Logical Consistency>P5 Evidence Quality>'
        'P6 Completeness>P7 Executive Utility>P8 Efficiency. '
        f"Mission={profile.mission}; Primary={profile.primary_domain}; Secondary={profile.secondary_domains}; "
        f"Complexity={profile.complexity}; Urgency={profile.urgency}; Risk={profile.decision_risk}; "
        f"Evidence={profile.evidence_requirement}; Depth={profile.required_depth}; Output={profile.expected_output}. "
        f"Active engines={runtime['engines']}. "
        'Required analysis controls: alternative hypotheses>=3; root-cause checks; assumptions audit; '
        'scenario analysis; uncertainty disclosure; evidence discipline; risk identification; executive conclusion; '
        'no fabricated sources or facts. Do not expose internal chain-of-thought. '
    )
    reply = generate_reply(req.message, context, get_messages())
    gate = final_quality_gate(
        answer=reply,
        profile=profile,
        evidence=[],
        risks=[],
        audit=runtime['audit'],
    )
    if not gate.release_ready:
        reply = (
            'Execution gate blocked release because the required OMEGA validation conditions were not satisfied.\n\n'
            f"Missing/failed controls: {', '.join(gate.issues) or 'none reported'}\n"
            'Required next action: provide or retrieve sufficient evidence, validate assumptions, and rerun the mission.'
        )
    add_message('assistant', reply)
    return JSONResponse({
        'reply': reply,
        'profile': profile.__dict__,
        'engines': runtime['engines'],
        'hypotheses': runtime['hypotheses'],
        'five_whys': runtime['five_whys'],
        'scenarios': runtime['scenarios'],
        'assumptions': runtime['assumptions'],
        'quality_gate': gate.__dict__ | {'release_ready': gate.release_ready},
    })
