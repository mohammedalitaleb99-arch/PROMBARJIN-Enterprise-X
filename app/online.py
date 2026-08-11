import os
from datetime import datetime, timezone
from urllib.parse import urlparse
import httpx

ALLOWED_HOSTS = {
    'reuters.com', 'www.reuters.com',
    'bbc.com', 'www.bbc.com',
    'apnews.com', 'www.apnews.com',
    'sec.gov', 'www.sec.gov',
    'eia.gov', 'www.eia.gov',
    'iea.org', 'www.iea.org',
    'worldbank.org', 'www.worldbank.org',
    'imf.org', 'www.imf.org',
    'fred.stlouisfed.org',
}


def _allowed(url: str) -> bool:
    host = (urlparse(url).hostname or '').lower()
    return host in ALLOWED_HOSTS or any(host.endswith('.' + h) for h in ALLOWED_HOSTS)


def fetch_public_source(url: str) -> dict:
    if not _allowed(url):
        raise ValueError('Domain is not on PROMBARJIN public-source allowlist.')
    with httpx.Client(timeout=12, follow_redirects=True, headers={'User-Agent': 'PROMBARJIN/1.0'}) as client:
        r = client.get(url)
        r.raise_for_status()
        text = r.text
    return {
        'url': str(r.url),
        'status_code': r.status_code,
        'fetched_at': datetime.now(timezone.utc).isoformat(),
        'content': text[:30000],
    }


def quote(symbol: str) -> dict:
    key = os.getenv('TWELVE_DATA_API_KEY')
    if not key:
        return {'status': 'not_configured', 'symbol': symbol, 'message': 'Set TWELVE_DATA_API_KEY on the server.'}
    with httpx.Client(timeout=10) as client:
        r = client.get('https://api.twelvedata.com/price', params={'symbol': symbol, 'apikey': key})
        r.raise_for_status()
        data = r.json()
    return {
        'status': 'ok' if 'price' in data else 'error',
        'provider': 'Twelve Data',
        'symbol': symbol,
        'price': data.get('price'),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'raw': data,
    }
