# Security, Gate and Authority

> Historical-context note: words such as “current”, “live”, “healthy”, “blocked” or “verified” in dated sections describe the historical snapshot of that section, not the 2026-09-08 public release candidate or current private runtime. Current publication status is defined by the root README, manifest and publication checklist.


## Trust model

The conversational control plane is powerful because it can observe, reason, coordinate workers, and prepare changes. It is intentionally not equivalent to unrestricted production root access.

The public architecture separates four authority classes:

```text
OBSERVE
  safe current-state reads

SANDBOX
  isolated non-SSOT artifacts/reference implementations

PREPARE
  validated change candidate / Gate request

APPLY
  external operational Gate with explicit evidence and rollback
```

A tool capable only of PREPARE must never report that it APPLIED a change.

## Secret event horizon

Secrets are excluded by path policy and by output redaction. A public deployment should deny credential material even when the broader parent directory is readable.

Examples of classes to exclude:

- environment files containing credentials;
- private keys and certificates;
- provider credential caches;
- authorization files;
- tunnel secret files;
- remote URLs containing embedded credentials;
- raw logs that may contain authentication material.

## Capability-oriented execution

Chat input should map to predefined capabilities rather than arbitrary shell strings. Worker runner execution should use pinned/verified executables, fixed argument construction, bounded stdin/output, timeouts, and `shell=False`-style semantics.

## Safe write root

GPT-generated files should be isolated from operational SSOT. A sandbox candidate can be reviewed, tested, hashed, and later promoted through a separate path.

## Change procedure

Before an operational change, the project uses a pattern similar to:

```text
full original verification
 -> current SHA/baseline
 -> dependencies/symlinks/execution path
 -> SSOT/STAGING boundary
 -> immutable/permission state
 -> rollback artifact
 -> one logical change
 -> bounded test/canary
 -> evidence
```

The exact production Gate is deployment-specific; the open-source contract keeps it behind an adapter.

## Human approval boundaries

Normal observation, sandbox implementation, safe worker tasks, and progress inspection should not require repeated human approval.

Human involvement is reserved for actual boundaries such as:

- operational/SSOT apply;
- external OAuth/login;
- broader permissions/read roots;
- paid provider plan changes;
- capital or irreversible actions.

## Security regression philosophy

Negative tests are first-class. Historical tests covered examples such as traversal writes, secret-path reads, non-allowed service access, journal metacharacter injection, unsafe process metadata, Git roots outside the allowed boundary, and compare-and-swap mismatch.

## Open-source scrub requirement

This public release candidate intentionally uses portable aliases. Before each public update, a scrub must scan all tracked files for:

- private home/server paths;
- usernames/account identifiers;
- tokens/keys/cookies;
- private Git remotes;
- raw conversation identifiers if not intentionally public;
- production-specific service/environment details that create unnecessary attack surface.
