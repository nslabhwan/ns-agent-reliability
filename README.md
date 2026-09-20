# OpenSynapse

> **Built by NS — AI execution infrastructure for real systems.**
>
> NS connects AI to servers, phones, cloud infrastructure, and code so work can move from request → execution → verification → recovery. OpenSynapse is the open-source work-node layer extracted from that real operating system.
>
> **NS:** https://getnslab.com/?utm_source=github&utm_medium=repo&utm_campaign=ns_identity_20260920
> **Community / support:** https://discord.gg/YBKQpC6aem

**Let ChatGPT actually work on the computer, server, and phone you own.**

**Install once. Ask naturally. Let it work. Verify the result.**

**New here? Start with [GETTING_STARTED.md](GETTING_STARTED.md).** It separates the verified Linux/Android paths from the still-pending ChatGPT account E2E so you can follow the current alpha without guessing.

### 3-minute first-value proof

On Linux or Termux, create one dedicated workspace, install OpenSynapse, inspect the boundary, and prove a real bounded write -> readback in one command:

```bash
curl -fsSL https://raw.githubusercontent.com/nslabhwan/ns-agent-reliability/main/try.sh | bash
```

The proof leaves `~/OpenSynapseWorkspace/OPENSYNAPSE_DEMO.txt` behind so the result is observable outside the CLI. This local proof does **not** claim the still-pending real-account ChatGPT tunnel E2E.

OpenSynapse is open-source AI work infrastructure built from a real long-running system. Its goal is simple: remove the human copy-paste loop between AI chat and your machines.

Instead of:

```text
AI gives command
-> you copy it to Terminal / SSH
-> you copy the error back
-> repeat
```

the target experience is:

```text
you ask
-> OpenSynapse acts on an authorized device
-> recoverable failures are handled
-> the real result is checked
-> you get the verified outcome
```

## What you get

- **Real work, not only advice** — bounded file reads, writes, commands, tests, logs and device workflows.
- **One interaction model across machines** — Linux and Android/Termux use the same public contract while remaining independent nodes.
- **Verified completion** — "done" means an observable result was checked when possible.
- **Less human relay** — fewer command, log and file copy-paste loops.
- **Safe defaults** — explicit roots, bounded actions, no arbitrary public shell by default.
- **Open source / self-hostable core** — inspect what gets access to your machines.

## Current Alpha

### Available now

- OpenSynapse node CLI:
  - `opensynapse install`
  - `opensynapse doctor`
  - `opensynapse status`
  - `opensynapse demo`
  - `opensynapse serve`
  - `opensynapse connect openai`
- portable bounded Direct Channel MCP core
- OpenAI Secure MCP Tunnel **prepare path**
  - pinned official `openai/tunnel-client v0.0.14`
  - official SHA256 verification before install
  - companion `cloudflared` extracted from the same official release bundle
  - API key stored as `env:CONTROL_PLANE_API_KEY` reference, not written by OpenSynapse
- Reliability Doctor and incident-derived reliability regressions
- verified workflow / deployment reference components
- Apache-2.0 software licensing

### Important connection boundary

The OpenAI tunnel **prepare path is verified**. A real OpenAI account tunnel → ChatGPT → OpenSynapse node E2E is **not yet claimed** until it is tested with a real authorized tunnel ID and runtime API key.

### Android / Termux verified alpha

The same OpenSynapse bounded core now runs on Termux **without FastMCP, Rust, or watchfiles**. Android uses a dependency-free stdlib MCP stdio server, while Linux can install the optional `[http]` extra for FastMCP HTTP transport.

The Android installer creates one writable workspace at `~/OpenSynapseWorkspace`. See [ANDROID_TERMUX.md](ANDROID_TERMUX.md). A fresh public install and real stdio MCP write/readback have now passed on an actual Android/Termux device.

### Next integration milestones

- real-account OpenAI Secure MCP Tunnel E2E
- one-time ChatGPT connector/plugin onboarding
- portable Android media/device modules
- multi-device pairing / routing
- desktop packaging
- resumable long-running jobs

## Linux quickstart

Python 3.11+ is required.

Clone / inspect, then:

```bash
OPENSYNAPSE_ROOT=/srv/my-app bash install.sh
```

By default the configured root is read-only.

Allow one explicit write workspace:

```bash
OPENSYNAPSE_ROOT=/srv/my-app \
OPENSYNAPSE_WRITE_ROOT=/srv/my-app/ai-workspace \
bash install.sh
```

Then:

```bash
opensynapse doctor
```

For the OpenAI Secure MCP Tunnel path, see [QUICKSTART.md](QUICKSTART.md).

## Why this exists

ChatGPT and other AI clients are increasingly able to call tools, but users still have to assemble MCP servers, tunnels, permissions, scripts, terminals, device control and verification themselves.

OpenSynapse focuses on the **last mile between conversation and verified real-world work**.

The project came from repeatedly solving real failures in a private multi-agent / device system: stale ownership, tool-surface drift, retry loops, context loss, execution boundaries, failed deployments, mobile reconnection and AI claiming completion before the external state actually changed.

Those lessons are being extracted into a portable public system without publishing private credentials, endpoints, conversations, Trading logic or private production state.

## User promise

> Keep using the AI interface you already know.
> Your authorized machines become work nodes.
> OpenSynapse executes within explicit boundaries and checks the result.

## Architecture

```text
ChatGPT / compatible AI client
            |
  supported authenticated connection
            |
   +--------+---------+
   |        |         |
 server    PC       phone
  node     node       node
   |        |         |
independent bounded runtimes
```

Unified UX does **not** mean coupled runtimes. Server, desktop and phone nodes remain independently operable.

## Modules already inside the lineage

- **Direct Channel** — bounded MCP execution
- **Reliability Doctor** — detects control / verification failure classes
- **Verified Workflow** — completion and evidence semantics
- **Phone Local knowledge** — real Android execution experience being ported without legacy runtime dependency

The older Reliability Doctor page is preserved at [docs/RELIABILITY_DOCTOR.md](docs/RELIABILITY_DOCTOR.md).

## Security boundary

OpenSynapse does not intentionally publish or require:
- private keys, credentials, cookies or tokens;
- private NS endpoints or account identifiers;
- Trading strategy / financial SSOT;
- private conversations or customer data;
- raw private production logs.

Local node defaults remain narrow. Public unauthenticated shell access is not a product feature.

For the OpenAI tunnel helper, OpenSynapse writes only the environment-variable reference `CONTROL_PLANE_API_KEY`, not the secret value.

See [SECURITY.md](SECURITY.md).

## Current verification

Current local/public-candidate verification includes:

- Linux one-install bootstrap
- bounded HTTP MCP write → readback → command E2E with `shell=false`
- OpenAI official tunnel-client prepare-path integration
- stdlib MCP tool-contract and write/readback tests
- full regression suite: **51/51 PASS**

Development rule:

```text
request -> execute -> observable result -> verify once
```

## Product direction

Read:
- [UNIFIED_BASE.md](UNIFIED_BASE.md)
- [USER_VALUE.md](USER_VALUE.md)

The immediate goal is not feature scarcity. It is to get real external installs, real completed tasks, repeat users, contributors and the first paid managed / support / evolved-system users.

## License

Software, tests, schemas and executable examples: **Apache-2.0**.

See `LICENSE`, `NOTICE`, `LICENSE_POLICY.md`, `THIRD_PARTY_NOTICES.md` and `TRADEMARKS.md`.
