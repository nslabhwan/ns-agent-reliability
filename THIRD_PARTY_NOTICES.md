# Third-party notices and provenance

Audit snapshot: 2026-09-19.

## Bundled material

No third-party source code, binary libraries, logos, fonts, screenshots, or copied third-party documentation are intentionally bundled in the tracked public source tree.

## Runtime dependency

OpenSynapse 0.2.0a1 declares:

- `fastmcp>=4.0.3,<5` — MCP server/client framework used by the portable Direct Channel component.
  - tested candidate environment: 4.0.5
  - observed upstream package metadata: `License-Expression: Apache-2.0`
  - installed externally by Python packaging; FastMCP source is not copied into this repository.

FastMCP has its own transitive dependencies. Those packages are installed by the Python package resolver and remain governed by their respective upstream licenses; they are not relicensed by this repository.

## Build and test tooling

External tools used during candidate verification include `setuptools`, `wheel`, `pytest`, and Python virtual environments. They are not copied into the tracked release tree and remain governed by their upstream licenses.

## External standards and product names

Documentation references MCP / Model Context Protocol and third-party AI/agent products descriptively. No ownership is claimed over third-party product names. See `TRADEMARKS.md`.

## NS historical-source provenance

Historical architecture and incident narratives are original NS project summaries/reconstructions prepared from NS-owned project records. Private source records, logs, conversations, credentials, account identifiers, private endpoints and Trading state are not copied into the public tree.

If a future release adds another third-party runtime dependency, code asset, binary asset or copied documentation, this notice and the release SBOM must be updated before publication.
