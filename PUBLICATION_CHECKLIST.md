# Publication Checklist

Status: **OpenSynapse 0.2.0a1 PUBLIC LIVE / 0.2.0a2 TUNNEL CANDIDATE**

Public repository: `nslabhwan/ns-agent-reliability`

## Current public release

- [x] OpenSynapse 0.2.0a1 Linux Alpha is public and remotely verified.
- [x] Fresh public install PASS.
- [x] Real HTTP MCP write/readback/bounded-command E2E PASS.
- [x] Public landing and feedback route are live.

## 0.2.0a2 Secure MCP Tunnel candidate

- [x] `opensynapse connect openai` implemented.
- [x] Official `openai/tunnel-client v0.0.14` pinned.
- [x] Official Linux release archive download PASS.
- [x] Official `SHA256SUMS.txt` verification PASS.
- [x] `tunnel-client` executable installation PASS.
- [x] bundled `cloudflared` companion installation PASS.
- [x] official `tunnel-client init` profile generation PASS.
- [x] `CONTROL_PLANE_API_KEY` stored as environment reference only.
- [x] fixed health port avoided with `127.0.0.1:0`.
- [x] full local regression suite PASS: **45/45**.
- [ ] tracked-tree content and public scrub PASS after final docs.
- [ ] fresh candidate package install + tests PASS after final docs.
- [ ] sync to public repository.
- [ ] push and remote HEAD verification.
- [ ] fresh public clone/install smoke for 0.2.0a2.

## Truth boundary

The OpenAI tunnel **prepare path is proven**.

The following are **not yet claimed**:
- real OpenAI runtime API key/control-plane Doctor PASS;
- real authorized tunnel long-running health;
- ChatGPT connector discovery;
- ChatGPT invoking a real OpenSynapse node through the tunnel.

Those claims require a real authorized account E2E.

## Publication assertions

Do not publish credentials, private endpoints, account identifiers, private conversations, production Trading/financial state, unredacted logs, or environment-specific secrets.

Do not expose an unrestricted unauthenticated remote shell by default.

Do not silently weaken a failed check to finish a release.
