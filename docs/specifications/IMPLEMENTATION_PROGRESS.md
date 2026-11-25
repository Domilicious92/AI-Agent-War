# AI-Agent-War implementation progress

**Updated:** 2026-11-25  
**Current phase:** P0 — foundation  
**Working branch:** `feature/p0-project-foundation`

## Evidence-based phase tracking
| Phase | Status | Evidence |
|---|---|---|
| P0 | In progress | Initial specification on main; first ADR, threat model and basic project setup proposed |
| P1 | Not started | No UI implementation verified |
| P2 | Not started | No provider implementation verified |
| P2.5 | Not started | No Security Gatekeeper implementation verified |
| P3 | Not started | No orchestration implementation verified |
| P4 | Not started | No memory implementation verified |
| P5 | Not started | No coding tool implementation verified |
| P6 | Not started | No autonomous workflow implementation verified |
| P7 | Not started | No evaluation benchmark verified |

## First iteration (P0)
- Created feature branch.
- Added architectural decision draft (ADR-0001).
- Added initial threat model and security invariants.
- Added a minimal Python scaffold plus unit tests for API health and a local CI workflow.
- Tests have not yet been verified by GitHub Actions; do not mark P0 accepted until results are available.

## Next scope
1. Confirm dependency versions and CI outcomes.
2. Add complete API contracts, project ownership and path safety tests.
3. Implement project/chat persistence with migration strategy.
4. Keep external tools and extensions disabled until P2.5 is accepted.

## Blockers
- OpenAI/Anthropic API keys are not configured; provider integration should use mocks first.
- Local sandbox/runner infrastructure has not been evaluated.
- Human approval needed for security architecture acceptance and any privileged actions.

## Workflow invariants
No unreviewed extension installation/use; no secrets in Git; no unsupported success claims; changes via feature branches and draft PRs.

## Iteration: project path boundary (2026-11-23)
- **Scope:** P0 security foundation supporting PRJ-002, not a completed PRJ-002 implementation.
- Added `backend/app/projects/path_policy.py` with a fail-closed, read-only path resolution helper for an explicitly authorized project root.
- Added five pytest cases: permitted in-root file, parent traversal, absolute outside path, symlink escape, and missing path.
- **Verification:** Code and tests committed to feature branch. Tests were **not executed in this automation run**; GitHub combined commit status previously returned no statuses. Do not mark as passing.
- **Security limitations:** This helper is not an API authorization layer, is vulnerable to TOCTOU if used without descriptor-relative file operations, and does not implement a sandbox. Do not expose it as a tool execution endpoint.
- **Review:** Checked compatibility with existing FastAPI health-only scaffold; no API routes or extension execution permissions were introduced.
- **Next:** Obtain CI results, run Ruff/Pytest, review security assumptions, add API contracts and secure file-worker design. Keep P0 in progress and PR draft.

## Iteration: descriptor-relative secure read (2026-11-23)
- **Scope:** P0 security foundation for PRJ-002; added `backend/app/projects/secure_reader.py` and `backend/tests/test_secure_reader.py`.
- **Behavior:** POSIX-only, descriptor-relative `os.open(..., dir_fd=...)` with `O_NOFOLLOW` on each path component, regular-file-only read, bounded bytes, explicit traversal/absolute-path rejection, descriptor cleanup. No endpoint or extension execution was exposed.
- **Review:** Unlike `path_policy.py`, this read helper avoids the separate resolve-then-open race for descendants. It still requires a trusted, pre-authorized root, worker isolation, per-operation authorization and platform-specific review. In particular, the root path itself is opened by pathname; a trusted root descriptor/identity is needed for stronger binding. No write API was introduced.
- **Tests authored:** in-root regular read, malformed/absolute/traversal paths, file and directory symlink escapes, oversized files, directory-as-file and invalid limits.
- **Verification:** Earlier head `db485de90fc9` has a completed successful GitHub Actions backend job (run 45273559720; lint and test steps succeeded). New secure-reader commits require fresh CI verification; no local test execution claimed.
- **Commits:** `02f9dd65c893` (reader), `6def67df6701` (syntax correction), `66ac73e4b354` (tests).
- **Next:** Check CI on new head; resolve any lint/test issues; formalize API contracts and project authorization. P0 remains in progress, PR #1 stays draft.

## Iteration: API trust-boundary contract (2026-11-24)
- **Scope:** P0 API contract and authorization design. Added `docs/architecture/API_CONTRACT_V0_1.md` with proposed endpoints, authorization/CSRF requirements, project isolation, typed error shape, extension approval gates, and concrete negative-test criteria.
- **Review:** Cross-checked against current specification and the existing health-only FastAPI application. Contract explicitly labels all other endpoints **not implemented**, avoiding false implementation claims. Secure-reader helpers remain unexposed and require server-owned project roots.
- **Evidence:** Commit `5871baa8f353b191ed493a9a6d9e36c2c0b19c7a` on `feature/p0-project-foundation`.
- **Verification:** Documentation-only change. No local tests executed. GitHub workflow query for prior `ac844077f8e9` returned no matching PR workflow runs; no fresh green CI assertion can be made. The previous recorded green CI applies only to `db485de90fc9`.
- **Blockers:** Authentication/session policy, local runner, and provider API keys are not configured. No plugins, skills, MCP servers or execution tools were installed or activated.
- **Next:** Confirm latest PR CI and implement typed API schemas with isolated tests. Keep P0 in progress and PR draft; no merge/deploy.

## Iteration: typed API boundary models (2026-11-24)
- Added pure Pydantic models for chat creation, message creation, project summaries, pagination and public error envelopes. Unknown fields are rejected; no client-supplied role or project identity is accepted in creation bodies. No routes were added.
- Added 15 parametrized test cases covering bounds, malformed UUIDs, privileged fields and public metadata/error redaction constraints.
- Commits: `9a60eac2968c` (models), `53339a2aa5a3` (tests).
- Review: consistent with API contract v0.1 and health-only application. Validation is not authorization; error code/message pairing and HTTP exception mapping, request body byte limits, authentication and persistence remain outstanding. Pydantic v2 dependency should be explicitly declared before acceptance.
- Verification: no local execution performed. Workflow query for previous abbreviated head returned no runs. New test commit workflow query returned 0 runs; no successful test claim made. P0 remains in progress.
- Next: explicitly declare Pydantic v2, verify CI, complete error mapping and session/persistence design. No extensions activated; no merge or deployment.

## Iteration: CI repair and dependency contract (2026-11-24)
- Reviewed specification, PR #1, branch inventory, API models, application scaffold and dependency manifest.
- CI run 45300281109 on head 4b948526370e failed at Ruff I001 in tests/test_secure_reader.py; pytest was skipped. Dependency installation succeeded. Removed the extra blank line identified by Ruff without changing test semantics (2387a1462f9f5701eb9c53721c4897fef0df96cd).
- Declared Pydantic >=2.9,<3 explicitly because API models directly import v2 APIs (069ca04e3ace2e6ac3ed3a7ebe3ff9db83425e05). Compatible with the Pydantic 2.14.4 observed in the previous CI log.
- Verification: GitHub writes confirmed; fresh CI and pytest results pending. No local execution claimed. P0 remains in progress.
- Next: verify new head CI; fix any failures before proceeding to public error mapping and session/persistence design. No extensions installed or activated, no secrets, merge or deployment.

## Iteration: public HTTP error boundary (2026-11-24)
- Baseline head `3dcce474b03bf13cfdaa6a0015a4d236ed4c0ac4`: GitHub Actions run 45307875879 completed successfully. PR #1 remains open, draft, unmerged.
- Added fixed public error mapping, server-generated UUIDs, no-store responses and handlers for validation, HTTP and unexpected exceptions; wired into health-only application. Preserves Allow on 405. No new production resource routes.
- Commits: 42e579d886d2 (handlers), f8c4959243d5 (registration), 22529b2546cb (eight test cases including parameterization).
- Review: matches API contract envelope; does not implement authentication, authorization, body-size limits, or secure server-side exception logging. Future authentication must define safe WWW-Authenticate handling and rate limiting must define Retry-After handling; current handlers do not forward those headers. ASGI server logging must be independently redacted before sensitive routes are enabled.
- Verification: baseline CI green; new tests authored, not locally executed; new head requires CI. No extension installation, activation, execution, secrets, merge or deployment.
- Next: verify new CI, define session/CSRF and persistence architecture, keep P0 in progress until exit gates are evidenced.

## Iteration: browser origin policy (2026-11-24)
- Baseline PR #1 head `2a249f780b310f9e31869d6310bdc14f046287e0`: GitHub Actions run 45315157472 completed successfully. P0 remains in progress.
- Added pure browser origin policy in `backend/app/browser_origin.py` (041ef7b5d29f) and 16 parametrized test cases in `backend/tests/test_browser_origin.py` (11403a18aebd).
- Unsafe methods require exactly one Origin matching server-owned configuration. Missing, null, foreign and duplicate origins are rejected. Safe methods may omit Origin; supplied foreign origins are rejected.
- Review: consistent with API contract and threat model; no middleware or resource routes exposed. This helper is not authentication, host validation, or complete CSRF protection. Configuration must validate the canonical origin; future integration must preserve duplicate headers, reject untrusted Host, enforce session-bound CSRF tokens, and ensure safe methods never mutate state. No provider or extension changes.
- Verification: baseline CI success confirmed via GitHub workflow API. New tests authored; local execution not performed and new CI pending. No extension installation, execution, merge or deployment.
- Next: verify new CI; define local session lifecycle, CSRF token binding, trusted Host/origin configuration and persistence migration strategy. Keep PR draft.

## Iteration: isolated session lifecycle (2026-11-24)
- Re-read specification v0.1.0, ADR, threat model, API contract, branch inventory, PR file inventory, application and origin helper. PR #1 open/draft; baseline head `7805cb6ad8a8` verified by Actions run 45329028207, including successful Ruff and pytest steps.
- Implemented process-local bounded session storage with random opaque credentials, digest-only stored tokens, monotonic absolute expiry, revocation and session-bound CSRF checks. Commits `dfbe0605e1b9` (implementation), `bb4c9137c793` (seven test cases including parameterization).
- Review: no new HTTP routes, provider calls or extension execution. Session issuance assumes a trusted authenticated principal; it is not credential verification. Restart invalidates sessions; multi-worker sharing, secure bootstrap, cookie policy, trusted Host/origin integration, request limits and in-flight authorization remain unresolved. Mutation callers must use authorize_mutation, not authenticate alone. No secrets, merge or deployment.
- Verification: baseline CI green; new tests authored, not locally executed. New CI must be verified before accepting this component. P0 remains in progress.
- Next: verify new CI; define trusted local bootstrap and HTTP session integration, then SQLite migration strategy. Human security acceptance and isolated runner remain open; external extensions remain disabled.

## Iteration: canonical local HTTP authority (2026-11-24)
- Re-read specification, progress, API contract, session and origin helpers, FastAPI entry point, dependency manifest, branches and open PR. Baseline head `ff7832f9bf8306ff596ecf31d0b9fff8f7b2182b`: Backend CI run 45387737658 completed successfully; isolated session and CSRF tests now have CI evidence.
- Added immutable server-owned loopback host/port/scheme configuration and exact raw Host/Origin checks, rejecting duplicate headers and ignoring forwarded authority. Implementation `b7f9d6eba49a8`; 18 test cases `c53b8c21c3a8`.
- Review: supports specification section 8 and API trust boundary; deliberately not wired into HTTP yet. Does not authenticate, enforce actual socket binding, configure TLS/proxy trust, or issue cookies. Exact canonical authority intentionally rejects aliases. No new routes or extension execution.
- Verification: baseline CI successful; new tests authored, not executed locally; fresh CI required. P0 remains in progress.
- Next: verify fresh CI, define trusted local bootstrap and integrate host/origin/session checks with HTTP and secure cookies; then SQLite migrations. No secrets, extension activation, merge or deployment.

## Iteration: one-time local bootstrap (2026-11-24)
- Re-read specification v0.1.0, progress, API contract, HTTP policy, session store, application and dependency manifest. Branch inventory contains main and feature/p0-project-foundation; PR #1 is open/draft.
- Baseline commit a1b97896cccb19893c565cec34abf3628d972990: Backend CI run 45452838004 completed successfully, providing evidence for the previous HTTP authority component.
- Added local bootstrap challenge with digest-only storage, 120-second default expiry, server-owned principal, atomic single-use exchange and invalidation on reissue. Implementation e9867731936ac938e2363695e2c3f7db0303ef31; 12 parametrized regression cases in 9db1fe012eac035b06657d073507b80d561e89e6.
- Review: uses existing SessionStore without changing its contract; challenge consumption precedes session issuance and fails closed on capacity errors. No HTTP route, launcher delivery, cookie or network binding implemented. Trusted launcher must deliver challenge privately, never via URL/logs; HTTP integration needs host/origin checks, bounded input and rate limiting. No extensions or provider calls introduced.
- Verification: baseline CI green; new tests authored, not executed locally; fresh CI pending. P0 remains in progress.
- Next: verify new CI, implement trusted launcher delivery and HTTP integration with secure cookies and negative tests, then SQLite migrations. No secrets, extension activation, merge or deployment.

## Iteration: private launcher handoff adapter (2026-11-25)
- Re-read specification v0.1.0, progress, API contract, bootstrap, session store, application, tests and dependency manifest. Branch inventory main and feature/p0-project-foundation; PR #1 open/draft.
- Baseline head 2dba555b297e0496c88781a94930b34cfc6f12c0: Actions run 45474264552 completed successfully, providing CI evidence for the prior bootstrap component.
- Added explicit challenge invalidation (8b35c17b40d926b89b8e042b0ee95ac31df3424a) and an injectable private delivery adapter (30533b4c62d38fe8dc422224ed053a110c78ac96). Adapter returns no token, revokes outstanding challenge on delivery failure and suppresses the original exception in normal traceback output.
- Three regression tests authored (93a9272a542c2c4bd5e9b58f97c7bf7d2fc42b2c): successful single-use handoff, partial delivery failure, idempotent revocation.
- Review: no new dependencies or HTTP routes; existing session contract unchanged. Transport is a stub boundary, not an authenticated private channel implementation. Launcher must serialize handoffs; concurrent reissue can invalidate a newer challenge on failure. A recipient that exchanges before delivery fails may already have a session; actual transport must prevent consumption before successful delivery or support session rollback. Exception context may remain inspectable by privileged logging; no claim of complete redaction. Do not expose adapter to untrusted callbacks or enable resource routes yet.
- Verification: baseline CI green; new tests not locally executed. Workflow query for test commit returned 0 matching runs; new section not accepted pending CI and transport design.
- Next: verify fresh CI, address handoff atomicity and private transport design, then integrate host/origin/session/CSRF checks and cookies; SQLite migrations remain open. No extensions activated, secrets used, merge or deployment. P0 remains in progress.

## Iteration: launcher CI repair and scoped revocation (2026-11-25)
- Re-read specification v0.1.0, progress, branches, draft PR #1 and its diff, bootstrap, launcher, sessions, tests, dependency manifest and health-only application. Baseline head 99d8e7bf1b37.
- CI run 45555687388, job 139007056224: dependency installation passed, Ruff failed BLE001 in launcher_handoff.py:20, pytest skipped. Corrected with a narrowly justified suppression at the transport trust boundary and moved the generic error outside the handler (c4533ab644ba).
- Added lock-protected digest-matching invalidation (09064d3c71ff), switched launcher failure cleanup to scoped invalidation (097e8f0f8eb9), and added two regression tests for stale failure preserving a newer challenge, exception context, and idempotent scoped revocation (ee63d90c890e).
- Review: existing global invalidate and session APIs remain compatible. No routes or dependencies added. Generic error avoids ordinary transport exception chaining, but traceback locals or an enclosing exception context can still expose sensitive data; secure logging remains required. Early exchange before transport success remains unresolved; do not expose this adapter via HTTP until a staged handoff or rollback is implemented. Actual authenticated private transport remains a stub boundary.
- Verification: new test commit workflow query returned []. No local tests executed; no new green CI claimed. P0 remains in progress.
- Next: verify CI for current head, prevent early exchange during handoff, add negative tests, then concrete private transport and HTTP integration. No extensions installed or activated, secrets used, merge or deployment.

## Iteration: staged bootstrap activation (2026-11-25)
- Re-read specification v0.1.0, progress, branch inventory, draft PR #1, bootstrap, launcher, session store, tests, application and API contract. Baseline b4a0f5448c25: Actions run 45618179930 completed successfully.
- Added pending challenge creation and lock-protected, digest-specific activation with expiry checks (d1ecc30cce21). Existing trusted direct issue API remains compatible; launcher now prepares and activates only after delivery returns successfully (21e571fb9e37).
- Added four regression tests for early exchange, failed delivery without session allocation, exact expiry boundary and stale successful delivery preserving newer pending challenge (208179344b97).
- Review: no new routes or dependencies; session interface unchanged. Pending challenges cannot be exchanged; stale activation cannot activate or revoke a replacement. Transport must coordinate recipient retry/readiness after activation; callback success is not proof of authenticated delivery. Direct issue remains trusted-only. Actual private transport, secure logging, HTTP integration and SQLite migrations remain open.
- Verification: baseline CI green; new tests authored, no local execution. New test commit workflow status at query: []. P0 remains in progress pending fresh CI and security acceptance.
- Next: verify new CI and inspect activation/cancellation edge cases; design authenticated local transport and HTTP host/origin/session/CSRF integration. No extension installation or execution, secrets, merge or deployment.
