from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .db import init_db, add_message, get_messages, add_memory, get_memories, add_decision, get_decisions
from .orchestrator import classify, system_context, quality_gate
from .ai import generate_reply
from .online import quote, fetch_public_source

BASE = Path(__file__).resolve().parent.parent
app = FastAPI(title='PROMBARJIN Ω Enterprise X', version='0.2.0')
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
    return {'status':'ok','service':'prombarjin-enterprise-x','internet_gateway':True,'market_gateway':bool(__import__('os').getenv('TWELVE_DATA_API_KEY'))}

@app.get('/api/state')
def state():
    return {'memories': get_memories(), 'decisions': get_decisions(), 'messages': get_messages()}

@app.post('/api/memory')
def memory(req: MemoryRequest):
    add_memory(req.key, req.value)
    return {'status':'saved'}

@app.post('/api/decision')
def decision(req: DecisionRequest):
    confidence = max(0, min(100, req.confidence))
    add_decision(req.title, req.rationale, confidence)
    return {'status':'saved'}

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
    profile = classify(req.message)
    context = system_context(profile)
    reply = generate_reply(req.message, context, get_messages())
    gate = quality_gate(reply)
    add_message('assistant', reply)
    return JSONResponse({'reply': reply, 'profile': profile.__dict__, 'quality_gate': gate})
