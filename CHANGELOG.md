# Changelog

## 0.2.0a7 autostart migration hardening — 2026-09-20

- Hardened migration from the earlier nohup tunnel to the systemd user service by terminating the tracked child process tree before managed restart.
- Avoids orphaned tunnel-client/MCP children and duplicate tunnel connections during upgrade.
- Public onboarding still preserves the existing config and stored runtime key.

## 0.2.0a6 real ChatGPT E2E + autostart — 2026-09-20

- Real authorized ChatGPT → OpenAI Secure MCP Tunnel → OpenSynapse stdio MCP E2E **PASS**.
- ChatGPT created and read back a 97-byte workspace artifact; independent host SHA-256 matched exactly.
- Added `opensynapse autostart install|status|remove` for Linux systemd user services.
- Service uses `Restart=always`, key-file references only, and mode-600 unit storage.
- Recovery state distinguishes `READY` from `READY_AFTER_LOGIN`; unattended servers are told when `loginctl enable-linger` is still required.
- `connect-openai.sh` now prefers autostart and falls back to a managed background process if the user service manager is unavailable.
- Updated public truth boundary: the real-account E2E is no longer pending.

## 0.2.0a5 secure runtime key file — 2026-09-20

- Added `opensynapse connect openai --runtime-key-file PATH`.
- OpenSynapse now passes only a `file:` secret reference to the official `tunnel-client`; it never reads or writes the key value.
- Preserved the existing environment-variable flow for compatibility.
- Added regression coverage proving the raw key never appears in tunnel-client argv.
- This change was triggered by real onboarding: the Direct Channel service uses `PrivateTmp=yes`, so files created in its `/tmp` are intentionally invisible to the operator SSH shell.

## 0.2.0a4 first-value proof — 2026-09-20

- Added `opensynapse demo` to perform a real bounded write -> readback verification inside the configured writable workspace.
- Demo leaves an observable `OPENSYNAPSE_DEMO.txt` proof file and verifies content + SHA-256 readback.
- When safe host commands are enabled, the demo also exercises the bounded `uptime` command with `shell=false`.
- Added `try.sh` so a new Linux/Termux user can create a dedicated workspace, install, run Doctor, and complete the proof path from one command.
- Fresh isolated Linux install smoke passed end-to-end.
- Full regression suite: **51/51 PASS**.
- This release does not change the truth boundary: real-account OpenAI tunnel -> ChatGPT -> OpenSynapse invocation remains pending until authorized E2E evidence exists.

## 0.2.0a3 Android / Termux verified — 2026-09-19

- Added GETTING_STARTED.md as the canonical first-use guide for current Linux, Android/Termux, and OpenAI tunnel paths.

- Extended the existing one-install bootstrap to detect Android/Termux.
- Added generic Python 3.11+ discovery instead of requiring version-suffixed executables.
- Added Termux prerequisite bootstrap for Python/Git when missing.
- Added a safe default Android workspace at ~/OpenSynapseWorkspace.
- Android defaults to read/write only inside that dedicated workspace.
- Reuses the same OpenSynapse bounded core; no private Phone Local or server runtime dependency is introduced.
- First real-device run found and drove fixes for Android dependency portability and actual platform detection.
- Final fresh public clone and install.sh PASS on actual Android/Termux.
- Final identity: node_type=android-termux / authority=SELF_HOSTED_ANDROID.
- Android base confirmed to install without FastMCP.
- Dependency-free stdlib MCP exposed the same seven dc_* tools.
- Real stdio MCP write/readback PASS with readback ANDROID_REAL_PHONE_OK.
- Private Phone Local runtime dependency and server runtime dependency both verified zero.

## 0.2.0a2 OpenAI Secure MCP Tunnel prepare path — 2026-09-19

- Added `opensynapse connect openai`.
- Reuses the official `openai/tunnel-client` rather than implementing a competing tunnel protocol.
- Pins verified tunnel-client `v0.0.14` for reproducible Alpha behavior.
- Downloads the official release archive and `SHA256SUMS.txt`, then verifies SHA256 before extraction.
- Installs both `tunnel-client` and the bundled `cloudflared` companion.
- Generates an official stdio MCP profile targeting the OpenSynapse node.
- Stores `CONTROL_PLANE_API_KEY` only as an environment reference in the generated profile.
- Uses an ephemeral loopback health listener to avoid fixed-port collisions.
- Full local regression suite: **45/45 PASS**.
- Official tunnel-client prepare-path E2E PASS.
- Public push, remote SHA verification, GitHub quality gate, fresh clone/install, and official tunnel prepare-only path all passed. Real OpenAI account tunnel / ChatGPT invocation remains **PENDING** and is not claimed as complete.

## 0.2.0a1 OpenSynapse Alpha — 2026-09-19

- Shifted the public product identity from a Doctor-first wedge to the **OpenSynapse** umbrella while preserving Reliability Doctor as a module.
- Consolidated the portable Direct Channel MCP core into the existing publication candidate instead of creating a competing repository.
- Added `opensynapse install`, `doctor`, `status`, and `serve`.
- Added a Linux one-install bootstrap with read-only-by-default configuration.
- Added product-facing HTTP MCP E2E covering real write, readback, bounded command execution, and `shell=false`.
- Full collected regression suite: **41/41 PASS**.
- Declared `fastmcp>=4.0.3,<5` and updated provenance/SBOM.
- Added `UNIFIED_BASE.md`, `USER_VALUE.md`, `QUICKSTART.md`, and preserved the former Doctor README under `docs/RELIABILITY_DOCTOR.md`.
- Tracked public scope expanded for the OpenSynapse candidate.
- Published to the public repository and verified by remote SHA match, fresh unauthenticated clone, fresh `install.sh`, installed Doctor, and real HTTP MCP write/readback/bounded-command E2E.
- Repositioned the GitHub Pages landing surface around OpenSynapse user value, Linux Alpha installation, current evidence, safety boundaries, and an explicit early-user feedback path.

## Main — distribution/social preview asset — 2026-09-09

- Added a 1280×640 PNG social-preview asset built around the real Doctor terminal findings.
- Public tracked scope expanded to 88 files.
- GitHub Settings upload remains a manual platform boundary; committing the image does not automatically set the Social Preview slot.

## Main — professional service assurance — 2026-09-08

- Added public professional-service assurance and responsibility boundary.
- Paid Audit/Hardening positioned as AI-assisted, evidence-reviewed and human-reviewed.
- Added OBSERVED / SUPPORTED / UNKNOWN truth states and CRITICAL/HIGH human sign-off requirement.
- Audit read-only / Hardening explicit production-change approval boundaries stated.
- Global public pricing changed to USD primary with fixed Korea KRW secondary pricing.
- Public tracked scope expanded to 87 files.

## Main — public packaging enhancement — 2026-09-08

Repository is public and remotely verified. Added the first conversion/discovery layer without changing the Doctor core:

- visual terminal demo based on actual Doctor output;
- symptom-first “Use this if…” triage near the top of README;
- LangGraph, CrewAI, OpenAI Agents SDK and MCP evidence-mapping guide;
- neutral normalized snapshot template;
- illustrative/sanitized audit report clearly labeled as **not** an external customer case;
- commercial service scope/pricing sourced from NS Package Factory;
- public no-secret Audit Fit Check issue form;
- lightweight GitHub Pages sales surface;
- tracked public scope expanded from 77 to 86 files; clean install, 32/32 tests, Doctor 15 findings, snapshot-template 0 findings, public scrub and package-license boundary all reverified.

## 0.1.0rc1-prepublication — 2026-09-08

Doctor-first release candidate prepared for external publication.

Added/changed:

- installed `ns-reliability` CLI and 60-second first-value README path;
- Agent Reliability Doctor source, broken fixture and tests included in the tracked public scope;
- clean Python 3.11 wheel build/install + installed CLI smoke verified;
- full candidate regression suite: **32/32 PASS**;
- Doctor-inclusive tracked-tree scrub and manifest verification;
- Apache-2.0 software license, CC BY 4.0 narrative-documentation scope, NOTICE, trademark policy, third-party provenance note and SPDX SBOM;
- historical/live wording corrected so historical provider states are not presented as current runtime truth.

Still not public:

- target GitHub owner/repository and authenticated write path are not yet bound;
- no public push or remote install verification has occurred.

## 0.0.2-publication-candidate — 2026-09-02

Harvested two verified reliability patterns from real operational incidents without creating a second runtime or publication system.

Added:

- build-once / verify-once / one-atomic-production-commit reference primitive with live-SHA CAS, validation-evidence binding, rollback-once and failed-candidate-SHA replay denial;
- portable lease/fencing primitive that separates client-session lifetime from workflow mutation ownership;
- monotonic fencing epoch on every successful lease acquisition;
- regression coverage for released/expired lease reacquisition, active foreign-lease takeover denial and stale-holder rejection;
- sanitized incident notes for deployment-Gate expansion and released-lease/live-session coupling;
- prepared license recommendation: Apache-2.0 target for software, CC BY 4.0 target for eligible narrative documentation, separate trademark treatment, and original third-party provenance controls.

Verified in the publication candidate:

- one-live-commit focused regression: 7 cases;
- lease/session independence focused regression: 5 cases;
- full current publication-candidate test suite: 27 passed in the independent read-only verification run;
- bounded scan of the newly harvested lease incident files found no flagged private server paths, credentials, private endpoints/account IDs or Trading content.

Still a publication candidate:

- final canonical LICENSE/NOTICE/SPDX metadata have not been applied;
- dependency/SBOM/provenance and clean-room release verification remain release-gate work;
- public repository exposure remains a human release boundary.

## 0.0.1-publication-candidate — 2026-08-12

V3 architecture update layered on the existing V2 Control Hub/Worker Manager design.

Added:

- bounded Deterministic Executor policy/reference module;
- deterministic-first routing principle;
- zero-unnecessary-AI Chat-share/DNA continuity design;
- explicit DNA target and bounded inheritance-packet reference logic;
- Atomic `FlowEvent` / Event Ledger reference model;
- Machine Flowboard + Human Cockpit dual projection contracts;
- V3 executor/DNA/observability schemas and tests;
- incident lessons for deterministic-work provider leakage and report-format retry coupling;
- progressive GPT/N direct-execution reduction model;
- updated roadmap and architecture diagrams.

Clarified:

- the objective is not zero model usage; it is zero **unnecessary** model usage for deterministic work;
- a bounded executor is not unrestricted root shell and never bypasses secret/SSOT/Gate boundaries;
- Human Cockpit must derive from machine truth rather than maintain a competing collector;
- scaffold/reference code is not production acceptance evidence.

Still not claimed as production-complete:

- live bounded Direct Executor integration;
- end-to-end zero-unnecessary-AI DNA UAT;
- live universal Worker Manager/Goal Session authority;
- normal multi-provider routing acceptance;
- durable live Atomic Event Ledger and dashboard projections;
- final reproducible public UAT;
- public repository push;
- final open-source license selection.

## 0.0.0-publication-candidate — 2026-08-11

Initial reconstructed open-source package covering the private project's connection work through the V2 Control Hub/Worker Manager architecture.

Included:

- Direct Channel architecture and security boundary;
- historical test/UAT evidence summary and preservation of revoked claims;
- Context/DNA and baseline/delta continuity design;
- Control Hub architecture;
- Worker Manager + Goal Session architecture;
- evidence-weighted Goal DAG/progress;
- resource/context/session governance;
- provider model/runtime/version governance;
- security/Gate authority model;
- incident/lesson catalogue;
- portable reference Python contracts and JSON schemas;
- current status and roadmap.
