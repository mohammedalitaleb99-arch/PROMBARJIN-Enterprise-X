# PROMBARJIN Ω Enterprise X - Runtime Specification

This repository is an implementation scaffold derived from the supplied PROMBARJIN Ω Enterprise X documents.

## Core contract
- Priority order: truth, safety, accuracy, logical consistency, evidence quality, completeness, executive utility, efficiency.
- Never fabricate; distinguish fact, inference, estimate, opinion and speculation.
- Classify every request by domain, complexity, urgency, risk, evidence requirement and expected output.
- Route work through a master orchestrator before domain engines.
- Use research pipelines for external/current information and prefer primary/official sources.
- Validate numerical, terminology, timeline, unit and entity consistency.
- Maintain persistent session/project memory and a decision ledger.
- Apply quality gates before final release.

## Engines represented in the application
Kernel, Cognitive, Research, Decision, Finance, Mining/Critical Minerals, Energy/Oil & Gas/ESG, Memory, Governance/Quality, Output, Negotiation, Red Team, Expert Panel, Game Theory, Forecasting, Career and Writing.

## Persistence
SQLite stores memories, conversations and decisions. Docker volume persistence is enabled by default.

## Capability boundary
The web app does not claim autonomous live data or autonomous external actions unless integrations are configured. OpenAI model execution is optional via `OPENAI_API_KEY`.
