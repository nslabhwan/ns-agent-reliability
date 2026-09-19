# Publication Checklist

Status: **OpenSynapse 0.2.0a1 PUBLIC LIVE / REMOTE VERIFIED**

Public repository: `nslabhwan/ns-agent-reliability`

## Historical public release

- [x] 0.1.0rc1 Agent Reliability Doctor is public and remotely verified.
- [x] Apache-2.0 software / CC BY 4.0 narrative-documentation boundary established.

## OpenSynapse 0.2.0a1 candidate — 2026-09-19

- [x] Public identity changed from Doctor-first product page to OpenSynapse umbrella.
- [x] Existing Reliability Doctor preserved as a module/history page.
- [x] Portable Direct Channel core consolidated into the existing publication candidate.
- [x] `opensynapse install / doctor / status / serve` CLI added.
- [x] Linux one-install bootstrap passed in an isolated temporary install home.
- [x] Direct Channel security defaults retained: explicit roots, bounded actions, shell disabled.
- [x] Full collected regression suite PASS: **41/41**.
- [x] Installed HTTP MCP E2E PASS:
  - product = OpenSynapse
  - write = OK
  - readback = `OPENSYNAPSE_E2E_OK`
  - bounded command = OK
  - shell = false
- [x] Runtime dependency `fastmcp>=4.0.3,<5` declared.
- [x] Tested FastMCP version 4.0.5 reports `License-Expression: Apache-2.0`.
- [x] SBOM and third-party notice updated for the new runtime dependency.
- [x] OpenSynapse files added to `FILE_INDEX.json`.
- [x] Full tracked-tree public-content scrub PASS.

## Remote publication verification

- [x] Exact tracked candidate tree pushed to the current public repository.
- [x] Staged diff reviewed.
- [x] Commit and push completed.
- [x] Remote HEAD matched the pushed commit.
- [x] Fresh unauthenticated clone PASS.
- [x] Fresh public `install.sh` PASS.
- [x] Installed `opensynapse doctor` PASS.
- [x] Real HTTP MCP write/readback/bounded-command E2E PASS.
- [x] Verified remote SHA recorded: `43525fd95889bc56d49afaa260dea5851b61d8f5`.

OpenSynapse 0.2.0a1 Linux Alpha is **public live and remotely verified**.

## Product boundaries that remain NOT public-ready

- authenticated zero-config HTTPS gateway;
- public ChatGPT plugin connection flow;
- portable Android Phone Local package;
- multi-device pairing/routing;
- desktop packaging;
- resumable long-running jobs.

## Publication assertions

The release must not expose credentials, private endpoints, account identifiers, private conversations, production Trading/financial state, unredacted logs, or environment-specific secrets.

The public node must not teach or enable an unrestricted unauthenticated remote shell by default.

Publication is complete only after the remote tree and a fresh public install are verified.
