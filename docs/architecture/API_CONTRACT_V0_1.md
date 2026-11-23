# API contract v0.1 — local workspace foundation

**Status:** Proposed, P0; no endpoints below are implemented except `GET /api/health`.

## Trust boundaries

- Browser -> FastAPI: untrusted input; local binding is not authentication. Every state-changing route requires an authenticated local session and CSRF protection when cookie-based.
- FastAPI -> project registry: project IDs resolve to server-owned, pre-authorized roots. Clients never supply arbitrary filesystem roots to file operations.
- Orchestrator -> model providers: only approved, redacted context is transmitted; credentials remain server-side.
- Orchestrator -> extension/worker: no tool/skill/plugin/MCP invocation until independent gatekeeper authorization is verified on **each call**.
- Database: SQLite transactional writes and migrations; project and chat ownership must be enforced in query predicates.

## Common response shape

Successful JSON responses follow resource schemas. Errors use:
```json
{"error":{"code":"NOT_FOUND","message":"Resource unavailable","request_id":"opaque-id"}}
```
No stack traces, secrets, local absolute paths or upstream API payloads in public errors.

## Proposed routes (not yet implemented)

| Method | Route | Purpose | Security requirement |
|---|---|---|---|
| GET | /api/health | Minimal readiness | No sensitive information |
| GET | /api/projects | List authorized projects | Session required |
| POST | /api/projects | Register project | Explicit local root approval; validate canonical identity |
| GET | /api/projects/{project_id} | Project details | Owner authorization |
| GET | /api/projects/{project_id}/chats | List chats | Project authorization |
| POST | /api/projects/{project_id}/chats | Create chat | Project authorization + CSRF |
| GET | /api/chats/{chat_id}/messages | Paginated messages | Chat-to-project authorization |
| POST | /api/chats/{chat_id}/messages | Add message | Authorization, content limits, CSRF |
| POST | /api/projects/{project_id}/tasks | Start planned task | Explicit mode, budget, allowlist |
| GET | /api/tasks/{task_id} | Task status | Project authorization |
| POST | /api/tasks/{task_id}/cancel | Request cancellation | Authorization + CSRF |
| GET | /api/tasks/{task_id}/events | Stream progress | Authorized short-lived subscription |
| GET | /api/projects/{project_id}/memory | Read curated memory | Project authorization |
| GET | /api/extensions | List registry status | Session required |
| POST | /api/extensions/{extension_id}/approve | Approve exact digest + permissions | Separate human approval and security proof |

## Stable identifiers and constraints

- Resource IDs: opaque UUID strings, never filesystem paths.
- Chat messages: server-assigned ID, chat ID, role, content, creation timestamp and delivery status.
- Task: project ID, immutable requested scope, state, budget, revision count, implementer/reviewer, review evidence and checkpoint ID.
- Extension: source, version, content digest, dependency digest, permission profile, security scan evidence and approval identity.
- Use UTC timestamps with explicit offset; enforce input size limits and bounded pagination.

## Implementation order and acceptance

1. Define Pydantic request/response models and typed errors without enabling file or tool operations.
2. Add isolated SQLite repository and migrations; test restart persistence and cross-project denial.
3. Add session and CSRF defenses **before** any mutating endpoints.
4. Add project/chat routes, mock event streaming and integration tests.
5. Gatekeeper remains fail-closed for all extension endpoints until P2.5 is fully verified.

**Contract test criteria:** unauthenticated reads fail, cross-project IDs do not disclose data, invalid identifiers and oversize payloads fail, errors leak no paths/secrets, cancelled tasks cannot continue tool execution, and extension activation without valid security proof fails.

## Open decisions

Local authentication mechanism; browser origin policy; session expiry; request size and rate limits; SQLite migration tooling; event replay and cancellation semantics. These must be resolved and tested before declaring P0/P1 complete.
