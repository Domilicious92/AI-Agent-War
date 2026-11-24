# AI-Agent-War implementation progress

**Updated:** 2026-11-24  
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
