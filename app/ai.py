import os
from typing import List, Dict


def generate_reply(user_text: str, context: str, history: List[Dict]) -> str:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return (
            'PROMBARJIN local mode is active.\n\n'
            f'Classification: {context}\n\n'
            'No OPENAI_API_KEY is configured, so the app is running in deterministic offline mode. '
            'The persistent memory, decision ledger, routing, and quality-gate layers remain active. '
            'Add an API key through the server environment to enable model-backed answers.'
        )

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        messages = [
            {'role': 'system', 'content': context},
            *({'role': m['role'], 'content': m['content']} for m in history[-20:] if m['role'] in ('user','assistant')),
            {'role': 'user', 'content': user_text},
        ]
        resp = client.responses.create(model=os.getenv('OPENAI_MODEL','gpt-5-mini'), input=messages)
        return resp.output_text
    except Exception as exc:
        return f'OpenAI integration error: {type(exc).__name__}: {exc}'
