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
- [x] Python 3.11+ generic detection implemented.
- [x] missing Python/Git can be installed via Termux pkg.
- [x] default Android workspace is ~/OpenSynapseWorkspace.
- [x] default Android write access is limited to that workspace.
- [x] private NS Phone Local runtime is not a dependency.
- [ ] server regression and public scrub PASS.
- [ ] candidate pushed to public main.
- [ ] fresh public clone on actual Android/Termux.
- [ ] actual Android install PASS.
- [ ] node_type=android-termux verified.
- [ ] phone file write/readback E2E PASS.
- [ ] final Android remote-verification receipt recorded.

## Truth boundary

The private NS Phone Local system is reference knowledge only. The public Android node must remain independently installable from the public repository.

Do not claim broader private Phone Local capabilities such as media extraction, app control, helper recovery, or Wi-Fi/LTE parity until they are separately reimplemented and proven in the public node.
