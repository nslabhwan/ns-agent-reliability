# Publication Checklist

Status: **OpenSynapse 0.2.0a1 CANDIDATE READY / NOT YET PUSHED**

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

## Remaining publication boundary

- [ ] Copy the exact tracked candidate tree to the current public repository.
- [ ] Review staged diff.
- [ ] Commit and push.
- [ ] Verify remote HEAD matches the pushed commit.
- [ ] Fresh unauthenticated clone.
- [ ] Fresh public install and `opensynapse` smoke.
- [ ] Record the verified remote SHA.

Until those items pass, **0.2.0a1 is not claimed as live on GitHub**.

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
