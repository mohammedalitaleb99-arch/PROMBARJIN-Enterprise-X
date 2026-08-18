import os, tempfile
os.environ['PROMBARJIN_DB'] = tempfile.mktemp(suffix='.db')
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r=client.get('/health'); assert r.status_code==200; assert r.json()['status']=='ok'

def test_chat_offline_mode():
    r=client.post('/api/chat', json={'message':'Analyze an oil and gas investment decision with NPV and risks.'})
    assert r.status_code==200
    data=r.json(); assert data['profile']['primary_domain']=='finance'
    assert 'quality_gate' in data

def test_memory_and_decision():
    assert client.post('/api/memory',json={'key':'mission','value':'Build PROMBARJIN'}).status_code==200
    assert client.post('/api/decision',json={'title':'MVP','rationale':'Start local-first','confidence':90}).status_code==200
    state=client.get('/api/state').json(); assert state['memories']; assert state['decisions']

def test_market_without_key_uses_public_gateway():
    os.environ.pop('TWELVE_DATA_API_KEY', None)
    r=client.get('/api/market/quote?symbol=AAPL')
    assert r.status_code==200
    data = r.json()
    assert data['status']=='ok'
    assert data['provider']=='Yahoo Finance'
    assert data['symbol']=='AAPL'
