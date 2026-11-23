# ADR-0001: Initial architecture

**Status:** Proposed (not yet accepted)  
**Date:** 2026-11-23

## Context
A local web application needs two LLM provider adapters, durable task orchestration, project-scoped memory and a strict extension security gate.

## Proposal
- FastAPI/Python for API, React/TypeScript for client.
- SQLite initially for relational task state; Markdown + Git for readable memory.
- A custom, deterministic task state machine before selecting LangGraph.
- Provider interfaces for OpenAI and Anthropic; credential-free mocks in tests.
- Separate execution worker with default-deny policies.
- No extension installation or execution until gatekeeper verification and approved permissions.
- Reviewers inspect relevant project-wide compatibility, not just a local diff.

## Alternatives
- Streamlit was considered but is a weaker fit for custom IDE-like interactions.
- PostgreSQL is deferred until transactional load requires it.
- Full agent framework adoption is deferred pending checkpoint and testability validation.

## Decision
Pending review. This file does not authorize any privileged tool execution.

## Consequences
Good testability and provider separation; additional integration code and operational complexity.
