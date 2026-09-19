# Third-party notices and provenance

Audit snapshot: 2026-09-19.

## Bundled material

No third-party source code, binary libraries, logos, fonts, screenshots, or copied third-party documentation are committed into the tracked public source tree.

## Declared Python runtime dependency

OpenSynapse declares:

- `fastmcp>=4.0.3,<5` — MCP server/client framework used by the portable Direct Channel component.
  - tested environment: 4.0.5
  - observed upstream package metadata: `License-Expression: Apache-2.0`
  - installed externally by Python packaging; FastMCP source is not copied into this repository.

FastMCP has transitive dependencies. Those packages remain governed by their respective upstream licenses.

## Optional OpenAI tunnel runtime

The `opensynapse connect openai` helper can download an official release from `openai/tunnel-client` when the user does not already provide a tunnel-client binary.

Current verified pin:
- `openai/tunnel-client v0.0.14`
- Linux amd64 asset tested: `tunnel-client-v0.0.14-linux-amd64.zip`
- verified SHA256: `15bd17e805cad39d412199115bb9e10a978dd35258a114cdf25dd2ae6681c7d3`
- the official archive includes `tunnel-client`, `cloudflared`, license/notice material and SPDX/license evidence.
- the top-level official archive license observed during verification is Apache-2.0 with OpenAI NOTICE.

These binaries are downloaded at user runtime and are not committed into this repository. Their upstream licenses and bundled third-party notices govern them.

OpenSynapse verifies the downloaded archive against the official release `SHA256SUMS.txt` before extraction.

## Build and test tooling

External tools used during verification include `setuptools`, `wheel`, `pytest`, and Python virtual environments. They are not copied into the tracked release tree and remain governed by their upstream licenses.

## External standards and product names

Documentation references MCP / Model Context Protocol and third-party AI/agent products descriptively. No ownership is claimed over third-party product names. See `TRADEMARKS.md`.

## NS historical-source provenance

Historical architecture and incident narratives are original NS project summaries/reconstructions prepared from NS-owned project records. Private source records, logs, conversations, credentials, account identifiers, private endpoints and Trading state are not copied into the public tree.

If a future release adds another third-party runtime dependency, code asset, binary asset or copied documentation, this notice and the release SBOM must be updated before publication.
