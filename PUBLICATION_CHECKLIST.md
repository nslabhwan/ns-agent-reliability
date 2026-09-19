# Publication Checklist

Status: OpenSynapse 0.2.0a3 PUBLIC LIVE / REAL ANDROID VERIFIED

Public repository: nslabhwan/ns-agent-reliability

## Linux and shared core

- [x] Linux one-install PASS.
- [x] optional FastMCP HTTP transport PASS.
- [x] HTTP MCP write/readback/bounded-command E2E PASS.
- [x] OpenAI Secure MCP Tunnel prepare path PASS.
- [x] full regression suite: 49/49 PASS.
- [x] tracked-tree public scrub PASS.

## Android / Termux

- [x] same bounded core reused; no separate Android control plane.
- [x] base package has no mandatory FastMCP/Rust/watchfiles dependency.
- [x] dependency-free stdlib MCP stdio transport.
- [x] same seven dc_* tool names.
- [x] dedicated default workspace.
- [x] actual public GitHub fresh clone on Android PASS.
- [x] actual public install.sh on Android PASS.
- [x] FastMCP absent from Android base.
- [x] platform=Android and Python 3.13.13 observed.
- [x] node_type=android-termux.
- [x] authority=SELF_HOSTED_ANDROID.
- [x] actual stdio MCP write PASS.
- [x] actual stdio MCP readback PASS: ANDROID_REAL_PHONE_OK.
- [x] private Phone Local runtime dependency = 0.
- [x] server runtime dependency = 0.

Tested public code commit:
4a27f49b564f93911850d1f30560b42302cfae59

## Still not claimed

- portable public Android media/device modules;
- real OpenAI account tunnel -> ChatGPT -> OpenSynapse E2E;
- multi-device pairing/routing;
- desktop packaging;
- resumable long-running jobs.

Private NS Phone Local remains reference knowledge only and is not a runtime dependency of the public Android node.
