# Illustrative Agent Reliability Audit report

> **Illustrative / sanitized example — not an external customer case study.**  
> This sample shows the delivery shape using generalized failure patterns proven in the NS project and the public Doctor fixtures/regressions.

## Executive verdict

**HIGH-RISK** — the bounded example stack has conflicting mutation authority, weak completion evidence and rollback behavior that can restore deprecated surfaces.

## Evidence received

- normalized agent reliability snapshot;
- public tool list and schema versions;
- bounded retry configuration;
- deployment/rollback notes;
- selected run-state evidence.

No credentials, private customer data or unrestricted production access are required for this example.

## Top findings

1. `DUPLICATE_AUTHORITY` — **CRITICAL / OBSERVED** — stale or concurrent writers can overwrite newer state.
2. `EVIDENCE_GAP` — **HIGH / SUPPORTED** — “Done” may be accepted without observing the requested result.
3. `ROLLBACK_RESURRECTS_DEPRECATED_SURFACE` — **CRITICAL / OBSERVED** — rollback can restore an obsolete contract.
4. `UNBOUNDED_RETRY` — **HIGH / OBSERVED** — failure can create uncontrolled repeated execution or cost.
5. `STALE_CLIENT_SERVER_SCHEMA` — **HIGH / SUPPORTED** — stale clients can regain authority over the current contract.

## Finding detail — DUPLICATE_AUTHORITY

**Evidence**  
Two independent writers target the same canonical `run_state`.

**Failure mode**  
Both paths can treat themselves as current mutation authority.

**Blast radius**  
- newer output overwritten by stale work;
- contradictory completion state;
- recovery path can race normal execution;
- incident reconstruction becomes ambiguous.

**Recommended remediation**  
Collapse mutation to one canonical writer. Keep projections, observers and advisory agents read-only unless they explicitly acquire bounded mutation authority.

**Acceptance test**  
- conflicting writer cannot mutate the target;
- canonical path still completes one real E2E;
- stale ownership/fencing evidence is rejected.

## Finding detail — EVIDENCE_GAP

**Evidence**  
Mutation is enabled while result evidence is optional.

**Failure mode**  
Agent/worker self-report can be interpreted as completion even when the requested external state did not change.

**Recommended remediation**  
Define risk-appropriate observed evidence at the actual mutation boundary: resulting state, receipt, version/hash, API response plus read-back, or another bounded verification artifact.

**Acceptance test**  
A successful self-report without observed result evidence cannot close the operation.

## Finding detail — ROLLBACK_RESURRECTS_DEPRECATED_SURFACE

**Evidence**  
Rollback restores a deprecated public tool surface.

**Failure mode**  
Recovery reintroduces a contract that current clients and authority rules had already retired.

**Recommended remediation**  
Rollback to the last verified state in the current generation, not to a historical compatibility surface. Add a regression that rejects deprecated tool resurrection.

## 30-day remediation order

**NOW**
1. collapse duplicate mutation authority;
2. require result evidence for mutations;
3. bound retry attempts and terminal states;
4. prevent deprecated surface resurrection.

**NEXT**
1. reconcile client/server schema authority;
2. verify long-running resume from bounded durable state;
3. reduce public tool surface where capabilities can sit behind stable authority-class contracts.

**LATER**
1. add framework-specific evidence adapters only where repeated customer demand proves value;
2. automate regression evidence collection without making observability an execution dependency.

## Commercial follow-up

The audit is useful without implementation work. If the team wants help applying selected NOW items, the findings can be converted into a separately scoped Safe Deployment / Reliability Hardening Sprint.

## Human review record

Illustrative sign-off shape:

- Reviewer: `[human reviewer]`
- Report version/hash: `[version/hash]`
- CRITICAL findings reviewed: yes
- HIGH findings reviewed: yes
- Findings downgraded/rejected: `[record]`
- Unresolved UNKNOWN items: `[record]`
- Implementation included: no — separate scope required

The presence of a Doctor match alone does not make a customer finding OBSERVED or SUPPORTED. The paid report requires evidence review.
