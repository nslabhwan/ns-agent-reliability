# Publication Checklist

Status: 0.1.0rc1 RELEASE CANDIDATE / REPOSITORY CHECKS PASS

## Current public re-audit — 2026-09-14 KST

- [x] Local `main` exactly matches `origin/main` before this re-audit.
- [x] Git tracked tree and `FILE_INDEX.json` match exactly: 90 / 90.
- [x] Deterministic content/mobile QA: 39 text surfaces / 0 issues.
- [x] Public scrub / JSON / package metadata scan: 90 / 90 PASS.
- [x] Full regression suite: 32 / 32 PASS.
- [x] Fresh Python 3.11 package build/install and installed CLI smoke PASS; Doctor fixture returns 15 findings.
- [x] Relative repository links checked: 14 references / 0 missing.
- [x] Public external links checked: 15 URLs / 0 failing at audit time.
- [x] Current GitHub quality workflow and Pages deployment both completed successfully on `dd80ce20689228bd841160214994ee1305d5ad45`.
- [x] GitHub Private Vulnerability Reporting enabled; `SECURITY.md` points to the live private reporting path.
- [x] Public quality workflow extended to run content QA, prepublish scrub, package install, 32-test regression and installed CLI smoke on push/PR.

## First public wedge

- [x] Agent Reliability Doctor selected as the first public wedge.
- [x] Doctor source/example/test are included in `FILE_INDEX.json`.
- [x] Installed CLI entrypoint exists: `ns-reliability`.
- [x] README starts with a first-value Doctor path instead of requiring the reader to understand the full NS architecture first.

## Technical pre-publication checks — 2026-09-08 KST

- [x] Fresh Python 3.11 virtual environment created.
- [x] `pip install .` built and installed the package successfully.
- [x] Installed `ns-reliability examples/doctor_broken_system.json --json` smoke PASS.
- [x] Doctor broken fixture produced 15 findings.
- [x] Full regression suite PASS: 32/32.
- [x] Python source compile PASS.
- [x] JSON parse PASS for candidate JSON files.
- [x] `tools/prepublish_check.py` PASS with Doctor included: 88 tracked files / 88 manifest files.
- [x] Candidate tracked-tree secret/private-path pattern scan PASS.

## Content/maturity checks

- [x] README explicitly separates proven portable components from reference/scaffold/partial components.
- [x] README explicitly states that the public `LeaseRegistry` is an in-memory fencing reference, not a complete durable persistent workflow runtime.
- [x] Trading/financial logic remains excluded from publication scope.
- [x] Complete historical-status audit across long-form docs; dated current/live language is explicitly scoped as historical and Worker Manager maturity conflict corrected.
- [x] Final staged-tree review completed before the first public push; future releases require an exact `FILE_INDEX.json` match.

- [x] Durable technical prepublication receipt: `release/TECHNICAL_PREPUBLICATION_RECEIPT_20260908.json`.

- [x] Public distribution and Python namespace renamed to `ns-agent-reliability` / `ns_agent_reliability` to avoid third-party marks in the public package name.
- [x] Wheel/sdist contents inspected: software wheel carries Apache LICENSE/NOTICE; source distribution carries both Apache and CC BY 4.0 texts with provenance metadata.
- [x] Concrete provenance defects identified by independent review were remediated: neutral package namespace, correct wheel/sdist license scope, current counts/build requirements, SPDX-valid SBOM, and historical-source provenance statement.

## Release-boundary checks

- [x] Select and apply canonical release-candidate licenses: Apache-2.0 software / CC BY 4.0 narrative documentation.
- [x] LICENSE / documentation license / NOTICE / trademark / third-party provenance / SPDX SBOM metadata added and aligned.
- [x] Confirm target GitHub owner/repository.
- [x] Verify authenticated GitHub write path.
- [x] Stage only the approved tracked public tree plus canonical license files.
- [x] Create the first public commit.
- [x] Push.
- [x] Verify remote tree, README rendering and first install command from the public repository.
- [x] Record remote commit SHA/release evidence.
- [x] Post-push stale-state wording sweep added after the README truth hotfix.

## Publication assertions

The first release must not teach or imply an unrestricted remote-shell pattern. Bounded execution examples must preserve explicit scope, timeout/output limits, secret denial, and separation of privileged mutation.

The public tree must not contain credentials, cookies, tokens, keys, private remote URLs, account identifiers, raw private conversations, production SSOT/runtime state, unredacted private logs, or Trading/financial logic.

## Publication rule

Do not silently weaken a failed check to finish the push. Technical readiness is not publication completion. Publication is complete only after the approved public repository is actually pushed and the remote tree/README/install path are verified.
