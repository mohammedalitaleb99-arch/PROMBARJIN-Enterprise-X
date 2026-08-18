from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .db import init_db, add_message, get_messages, add_memory, get_memories, add_decision, get_decisions
from .ai import generate_reply
from .online import quote, fetch_public_source
from .omega_engine import build_runtime_context, final_quality_gate
from .omega_compliance import master_runtime, action_engine, output_profile
from .omega_strict import build_strict_runtime

BASE = Path(__file__).resolve().parent.parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title='PROMBARJIN Ω Enterprise X', version='1.2.0', lifespan=lifespan)
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
        'strict_spec_version': '1.0',
        'strict_runtime': True,
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
    strict = build_strict_runtime(req.message, evidence_count=0)
    compliance = master_runtime(req.message)
    runtime = build_runtime_context(req.message)
    profile = runtime['profile']
    context = (
        'PROMBARJIN OMEGA STRICT MASTER RUNTIME. '
        'Priorities=P1 Truth>P2 Safety>P3 Accuracy>P4 Logical Consistency>P5 Evidence Quality>'
        'P6 Completeness>P7 Executive Utility>P8 Efficiency. '
        f"Mission={profile.mission}; Primary={profile.primary_domain}; Secondary={profile.secondary_domains}; "
        f"Complexity={profile.complexity}; Urgency={profile.urgency}; Risk={profile.decision_risk}; "
        f"Evidence={profile.evidence_requirement}; Depth={profile.required_depth}; Output={profile.expected_output}. "
        f"Strict spec gate={strict['gate']}; compliance engines={compliance['engines']}; execution_mode={compliance['execution_mode']}. "
        'Apply all 11 OMEGA parts; never fabricate; never invent sources; identify assumptions; separate fact/inference/estimate/opinion/speculation; '
        'use research discipline; alternatives; risk; financial/domain controls; memory; governance; audit traceability; output compilation. '
        'Never expose internal chain-of-thought.'
    )
    reply = generate_reply(req.message, context, get_messages())
    gate = final_quality_gate(answer=reply, profile=profile, evidence=[], risks=[], audit=runtime['audit'])
    if not strict['gate']['release_ready'] and profile.evidence_requirement == 'high':
        reply = (
            'OMEGA RELEASE GATE: BLOCKED. Verified evidence is required for this high-evidence mission.\n\n'
            'Provide/retrieve sufficient independent evidence, validate assumptions and contradictions, then rerun the mission.'
        )
    elif not gate.release_ready:
        reply = (
            'OMEGA QUALITY GATE: additional validation required before a definitive recommendation.\n\n'
            f"Failed controls: {', '.join(gate.issues) or 'insufficient validation'}"
        )
    add_message('assistant', reply)
    return JSONResponse({
        'reply': reply,
        'profile': profile.__dict__,
        'strict_spec': strict,
        'compliance_profile': compliance['profile'],
        'engines': compliance['engines'],
        'execution_mode': compliance['execution_mode'],
        'output_profile': output_profile(req.message),
        'actions': action_engine(),
        'hypotheses': runtime['hypotheses'],
        'five_whys': runtime['five_whys'],
        'scenarios': runtime['scenarios'],
        'assumptions': runtime['assumptions'],
        'quality_gate': gate.__dict__ | {'release_ready': gate.release_ready},
    })
