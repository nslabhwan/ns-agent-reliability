# Publication Checklist

Status: OpenSynapse 0.2.0a2 PUBLIC LIVE / 0.2.0a3 ANDROID TERMUX CANDIDATE

Public repository: nslabhwan/ns-agent-reliability

## Existing public evidence

- [x] Linux one-install PASS.
- [x] HTTP MCP write/readback/bounded-command E2E PASS.
- [x] OpenAI Secure MCP Tunnel prepare path PASS.
- [x] 0.2.0a2 remote verification PASS.

## 0.2.0a3 Android / Termux candidate

- [x] same OpenSynapse core reused; no separate Android control plane.
- [x] Termux environment detection implemented.
- [x] default Android workspace is ~/OpenSynapseWorkspace.
- [x] default Android write access is limited to that workspace.
- [x] private NS Phone Local runtime is not a dependency.
- [x] FastMCP removed from mandatory base dependencies.
- [x] dependency-free stdlib MCP stdio transport added.
- [x] same 7 dc_* MCP tool names preserved.
- [x] Linux HTTP transport retained as optional http extra.
- [x] Android simulation installs without FastMCP/Rust/watchfiles.
- [x] Linux http simulation installs FastMCP 4.0.5.
- [x] full regression suite: 49/49 PASS.
- [x] HTTP MCP E2E PASS.
- [x] tracked-tree public scrub PASS.
- [x] first real phone base wheel build/install PASS without FastMCP.
- [x] actual Android platform guard regression found and fixed.
- [x] Android platform regression test added.
- [ ] portability fix pushed to public main.
- [ ] fresh public clone on actual Android/Termux after fix.
- [ ] actual Android install PASS.
- [ ] node_type=android-termux and authority=SELF_HOSTED_ANDROID verified.
- [ ] actual stdlib MCP write/readback PASS on phone.
- [ ] final Android remote-verification receipt recorded.

## Truth boundary

The first real-phone attempt found the Linux FastMCP/watchfiles dependency chain was not portable to Android. The candidate was refactored rather than bypassed: Android now uses the dependency-free stdlib MCP stdio transport.

Do not claim broader private Phone Local capabilities such as media extraction, app control, helper recovery, or Wi-Fi/LTE parity until they are separately reimplemented and proven in the public node.
