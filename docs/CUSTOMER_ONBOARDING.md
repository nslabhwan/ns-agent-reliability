# OpenSynapse customer onboarding

The verified public path is designed so the customer performs only the account-owned steps that OpenSynapse cannot safely impersonate.

## Customer does once

1. Create an OpenAI Tunnel and include the target ChatGPT workspace.
2. Create a Restricted runtime API key with **Tunnels Read + Use**.
3. Add one ChatGPT custom MCP plugin: **Tunnel**, same Tunnel, **No authentication**.

## OpenSynapse does the machine work

Run:

```bash
curl -fsSL https://raw.githubusercontent.com/nslabhwan/ns-agent-reliability/main/onboard-openai.sh | bash
```

The guided flow installs/reuses OpenSynapse, stores the runtime key locally with mode 600, prepares the official Tunnel profile, runs Doctor, enables recovery when supported, records only non-secret onboarding state, and prints the final ChatGPT plugin fields and E2E prompt.

Check/resume:

```bash
curl -fsSL https://raw.githubusercontent.com/nslabhwan/ns-agent-reliability/main/onboard-openai.sh | bash -s -- --status
```

## Secret boundary

The raw runtime key is not accepted as a command-line argument, not written to onboarding state, and not pasted into ChatGPT. The official `tunnel-client` receives a local `file:` reference.

## Verified reference

The real ChatGPT → Secure MCP Tunnel → OpenSynapse write/readback E2E evidence is in `REAL_CHATGPT_E2E_20260920.md`.
