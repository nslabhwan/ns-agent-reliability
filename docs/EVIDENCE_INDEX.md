# Evidence Index

> Provenance note: the private filenames and SHA-256 values below identify NS-owned source evidence used to write these original public summaries. The underlying private files are not redistributed, quoted wholesale, or licensed through this repository.


This file records the private engineering artifacts used to reconstruct the public history. Private absolute paths are intentionally omitted. Digests are included where directly verified during reconstruction.

## Evidence records

- **`GPT_COLLAB_ROLES.md`**
  - Date: 2026-07-05
  - Digest/status: SHA256 `5b953eb7eb3e30d3d1ea1a44029063accb372efce78ecf815a640faf92daa9e8`
  - Public use: earliest explicit GPT/Claude role split and GPT direct-access limitation.
- **`GPT_PLAYWRIGHT_MANUAL.md`**
  - Date: 2026-07-08 onward
  - Digest/status: SHA256 `e8f2fe799cee2f3a4d466ad436060be0a1980daf0d4be929a9eb8c0d9aa39787`
  - Public use: first server-side Claude↔ChatGPT direct dialogue and bridge lineage.
- **`NS_DC_V2_CANONICAL_PLAN.md`**
  - Date: 2026-08-08
  - Digest/status: SHA256 `0d7a9e928fb0f51a7812d2df94ec50c1d19defd85b732ef8aa4903fcfb80fe72`
  - Public use: Direct Channel genesis, authority, phases, Context/DNA.
- **`phase0_outputs/CURRENT_ARCHITECTURE.md`**
  - Date: 2026-08-08
  - Digest/status: SHA256 `944f416852807c286c2b7a7a3a7b96f28f0125bdac20d1e309f5ab60ff01213f`
  - Public use: initial Direct Channel runtime architecture and boundaries.
- **`phase11_outputs/TEST_RESULTS.md`**
  - Date: 2026-08-08
  - Digest/status: SHA256 `cdb4abdfe0840e36d204cf4d92a5c19c514fb68281126b4abbf72109d5ed9d8b`
  - Public use: security/functional test history.
- **`phase12_outputs/P12B_UAT_RESULTS.md`**
  - Date: 2026-08-08
  - Digest/status: SHA256 `2e503cae24e892b598572056646b3fc4f9123a3165da381800f48e798423ab1e`
  - Public use: historical initial P12-B judgement.
- **`phase12_outputs/P12B_UAT_RETRACTION.md`**
  - Date: 2026-08-08
  - Digest/status: SHA256 `0d2358150363b18c49fb914ceb789b1778d4294a7df91278967fa022a5f3a3c4`
  - Public use: retraction and actual external UAT findings.
- **`NS_GPT_SERVER_FINAL_CONNECTION_PLAN_V2_20260811.md`**
  - Date: 2026-08-11
  - Digest/status: SHA256 `573c70619679977c20e651c1b10f1c39fc148279ae8131677e17bb98193350a8`
  - Public use: Worker Manager/Goal Session/DAG/resource final architecture.
- **`GPT_CONTROL_PLANE.md`**
  - Date: 2026-08-11
  - Digest/status: current during reconstruction.
  - Public use: N control-plane/scaffold-first operating contract.
- **`GITHUB_FRESHNESS_GUARD_V1.json`**
  - Date: 2026-08-10
  - Digest/status: SHA256 `d39a090b444381ba532ce987e7ce494ec9704cdf83b49d62a14a113f80febef8`
  - Public use: Git vs GitHub Issue freshness incident.
- **`STAGE0_HEALTH_COLLECTOR_REVIEW_R1/R2/R3`**
  - Date: 2026-08-11
  - Digest/status: review lineage.
  - Public use: health semantic lessons.
- **`ns_health_collector.py` R3 in-progress**
  - Date: 2026-08-11
  - Digest/status: SHA256 `1b7e8ce03ed20709eadb16f918022064285520045f9a3ace405ea25d01eda2b4` at last direct read.
  - Public use: current Stage 0 cutoff.
- **`NS_CONTROL_HUB_V2_SCAFFOLD/`**
  - Date: 2026-08-11
  - Digest/status: plan-wide scaffold.
  - Public use: portable reference source/contracts.

## Reconstruction rule

When artifacts disagree, later stronger evidence does not delete earlier history. The earlier claim is labelled `REVOKED` or `SUPERSEDED`, and the correction is preserved.

## Private evidence not copied

Raw private conversation exports, browser authentication material, credentials, environment files, operational SSOT, provider credential stores, and unredacted logs were intentionally excluded from this publication tree.

## Public release-candidate evidence

- `release/TECHNICAL_PREPUBLICATION_RECEIPT_20260908.json` — clean Python 3.11 install, installed CLI smoke, 32/32 regressions, compile/JSON checks, license hashes and remaining remote-publication boundaries. This receipt proves the public candidate checks it records; it does not expose or replace private operational evidence.
