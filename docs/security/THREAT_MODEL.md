# Threat model — initial P0 baseline

**Status:** Draft; security acceptance not complete.

## Assets
API keys, project files, Git history, local host, runtime configuration, markdown memory, user prompts, audit logs, third-party credentials.

## Trust boundaries
1. Browser ↔ local backend: cross-origin and CSRF exposure, unauthenticated requests.
2. Backend ↔ OpenAI/Anthropic APIs: content export and third-party responses.
3. Backend ↔ project filesystem: path traversal, symlink escapes, cross-project access.
4. Orchestrator ↔ tool runner: untrusted generated commands, RCE, container escape.
5. Extension registry ↔ external skills/servers: supply-chain compromise and prompt injection.
6. Memory ↔ model context: malicious instructions hidden in documents or tool outputs.

## Abuse cases and required controls
| Threat | Invariant |
|---|---|
| Skill instructs agent to read .env | Skill treated as untrusted data; independent tool authorization denies |
| Modified approved extension | Content hash mismatch invalidates authorization |
| Cross-project or symlink path | Canonical path containment verified at access time |
| Dangerous command or package hook | No execution in quarantine; sandbox and explicit command allowlist |
| Extension exfiltrates secrets | No secrets inside runner; network default-deny and egress controls |
| Prompt injection in memory/tool output | No privilege elevation through model text |
| Unexpected localhost request | Authentication, CSRF/origin protections and explicit listener bind |
| Agent infinite revision loop | Cost, iteration, time and resource limits |
| Scanner failure | Fail closed; never approve unknown state |
| Privileged Git change | Explicit user approval for merge, push to protected targets and deployment |

## Security validation plan
Test each denial case with fixture inputs. Verify static analysis and sandbox restrictions independently of LLM evaluations. Maintain append-only audit semantics and expiry/revocation checks. A clean scan does **not** imply malicious behavior cannot occur.

## Residual risks
Zero-day dependencies, model collusion or shared hallucinations, host runtime vulnerabilities, side-channel leaks, false negatives, inadvertent provider data disclosure. Reassess when extending scope.
