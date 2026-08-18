import os
from datetime import datetime, timezone
from urllib.parse import urlparse, quote as urlquote
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
    """Return a no-key market quote from Yahoo Finance's chart endpoint."""
    symbol = symbol.strip().upper()
    if not symbol:
        return {'status': 'error', 'message': 'Symbol is required.'}

    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urlquote(symbol, safe='')}"
    params = {
        'range': '1d',
        'interval': '1m',
        'includePrePost': 'true',
        'events': 'div,splits',
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Android; PROMBARJIN/1.0)',
        'Accept': 'application/json',
    }
    with httpx.Client(timeout=10, follow_redirects=True, headers=headers) as client:
        r = client.get(url, params=params)
        r.raise_for_status()
        payload = r.json()

    result = (payload.get('chart') or {}).get('result') or []
    if not result:
        error = (payload.get('chart') or {}).get('error') or {}
        return {
            'status': 'error',
            'provider': 'Yahoo Finance',
            'symbol': symbol,
            'message': error.get('description') or 'No quote data returned.',
        }

    meta = result[0].get('meta') or {}
    price = meta.get('regularMarketPrice')
    if price is None:
        price = meta.get('previousClose')

    currency = meta.get('currency')
    exchange = meta.get('exchangeName')
    market_state = meta.get('marketState')

    return {
        'status': 'ok' if price is not None else 'error',
        'provider': 'Yahoo Finance',
        'symbol': symbol,
        'price': price,
        'currency': currency,
        'exchange': exchange,
        'market_state': market_state,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'raw': meta,
    }
