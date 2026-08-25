from __future__ import annotations

import os
from typing import Any
from pydantic import BaseModel


class ConflictAnalysisResponse(BaseModel):
    conflict_type: str
    impact_level: str
    suggested_action: str
    reasoning_rationale: str
    affected_fields: list[str]


class AIConflictAdvisor:
    """Advisory-only model integration. It can recommend; it cannot mutate the ledger."""
    def analyze_conflict(self, server_state: dict[str, Any], client_payload: dict[str, Any]) -> dict[str, Any]:
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return {'recommendation':'HUMAN_REVIEW_REQUIRED','reasoning':'AI Advisor unavailable; safe fallback engaged.','ai_used':False}
        try:
            from openai import OpenAI
            client=OpenAI(api_key=api_key)
            response=client.responses.parse(model=os.getenv('OPENAI_MODEL','gpt-5-mini'),input=[
                {'role':'system','content':'You are an advisory conflict classifier. Never authorize writes. Return a structured recommendation only.'},
                {'role':'user','content':f'Server state: {server_state}\nOffline client payload: {client_payload}'}],text_format=ConflictAnalysisResponse)
            parsed=response.output_parsed
            return parsed.model_dump() | {'ai_used':True}
        except Exception:
            return {'recommendation':'HUMAN_REVIEW_REQUIRED','reasoning':'AI Advisor failed safely; no state mutation performed.','ai_used':False}
