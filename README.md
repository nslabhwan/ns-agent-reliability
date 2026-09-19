# OpenSynapse

**Let ChatGPT actually work on the computer, server, and phone you own.**

**Install once. Ask naturally. Let it work. Verify the result.**

OpenSynapse is an open-source AI work infrastructure built from a real long-running system. Its goal is simple: remove the human copy-paste loop between AI chat and your machines.

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
- **One interaction model across machines** — Linux server first; desktop and Android nodes follow the same public contract.
- **Verified completion** — "done" means an observable result was checked when possible.
- **Less human relay** — fewer command, log and file copy-paste loops.
- **Safe defaults** — explicit roots, bounded actions, no arbitrary public shell by default.
- **Open source / self-hostable core** — inspect what gets access to your machines.

## Current Alpha

### Available in this candidate

- Linux OpenSynapse node CLI:
  - `opensynapse install`
  - `opensynapse doctor`
  - `opensynapse status`
  - `opensynapse serve`
- portable bounded Direct Channel MCP core
- Reliability Doctor and incident-derived reliability regressions
- verified workflow / deployment reference components
- Apache-2.0 software licensing

### Next integration milestones

- stable authenticated HTTPS gateway
- one-time ChatGPT plugin connection flow
- portable Android Phone Local node
- multi-device pairing / routing
- desktop packaging
- resumable long-running jobs

We do not claim those milestones are public-ready before a real outsider E2E proves them.

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
opensynapse serve --transport http
```

See [QUICKSTART.md](QUICKSTART.md).

## Why this exists

ChatGPT and other AI clients are increasingly able to call tools, but users still have to assemble MCP servers, tunnels, permissions, scripts, terminals, device control and verification themselves.

OpenSynapse is focused on the **last mile between conversation and verified real-world work**.

The project came from repeatedly solving real failures in a private multi-agent / device system: stale ownership, tool-surface drift, retry loops, context loss, execution boundaries, failed deployments, mobile reconnection and AI claiming completion before the external state actually changed.

Those lessons are being extracted into a portable public system without publishing private credentials, endpoints, conversations, Trading logic or private production state.

## User promise

> Keep using the AI interface you already know.
> Your authorized machines become work nodes.
> OpenSynapse executes within explicit boundaries and checks the result.

## Architecture in one picture

```text
ChatGPT / compatible AI client
            |
     OpenSynapse connection
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

The older Reliability Doctor product page is preserved at [docs/RELIABILITY_DOCTOR.md](docs/RELIABILITY_DOCTOR.md).

## Security boundary

OpenSynapse does not intentionally publish or require:
- private keys, credentials, cookies or tokens;
- private NS endpoints or account identifiers;
- Trading strategy / financial SSOT;
- private conversations or customer data;
- raw private production logs.

Local node defaults remain narrow. Public unauthenticated shell access is not a product feature.

See [SECURITY.md](SECURITY.md).

## Current verification

The unified candidate currently carries the existing reliability regressions plus the imported bounded Direct Channel core and OpenSynapse CLI tests.

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
