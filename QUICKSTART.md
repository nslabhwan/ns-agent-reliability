# OpenSynapse Linux Alpha — Quickstart

OpenSynapse turns a Linux machine you own into a bounded MCP work node for AI clients.

## 1. Install

Clone and inspect the repository, then run:

```bash
OPENSYNAPSE_ROOT=/srv/my-app bash install.sh
```

By default the node is read-only.

To allow writes only inside one explicit workspace:

```bash
OPENSYNAPSE_ROOT=/srv/my-app \
OPENSYNAPSE_WRITE_ROOT=/srv/my-app/ai-workspace \
bash install.sh
```

To also enable the small built-in host command set (`uptime`, `df`, `free` when present):

```bash
OPENSYNAPSE_ROOT=/srv/my-app \
OPENSYNAPSE_ENABLE_SAFE_COMMANDS=1 \
bash install.sh
```

No arbitrary shell is enabled by default.

## 2. Check the boundary

```bash
opensynapse doctor
opensynapse status
```

## 3A. Local MCP only

```bash
opensynapse serve --transport http
```

Default endpoint:

```text
http://127.0.0.1:8767/mcp
```

Do not expose that unauthenticated loopback endpoint directly to the public Internet.

## 3B. OpenAI Secure MCP Tunnel

OpenSynapse can prepare an OpenAI Secure MCP Tunnel profile using the official `openai/tunnel-client`.

You need:
- an authorized OpenAI tunnel ID such as `tunnel_...`;
- a runtime API key with the permissions required by your OpenAI tunnel setup.

OpenSynapse currently pins the verified official tunnel-client release `v0.0.14`. If `tunnel-client` is not already installed, OpenSynapse downloads the official Linux release, verifies it against the release `SHA256SUMS.txt`, and installs both `tunnel-client` and its bundled `cloudflared` companion.

Prepare the profile without contacting the control plane:

```bash
opensynapse connect openai \
  --tunnel-id tunnel_REPLACE_ME \
  --prepare-only
```

The generated profile stores:

```text
env:CONTROL_PLANE_API_KEY
```

not the API key value.

For a real connection, load the runtime key into your environment without putting the literal value in the OpenSynapse config:

```bash
read -rsp "OpenAI runtime API key: " CONTROL_PLANE_API_KEY
echo
export CONTROL_PLANE_API_KEY
```

Run the official Doctor without starting the long-lived daemon:

```bash
opensynapse connect openai \
  --tunnel-id tunnel_REPLACE_ME \
  --no-run
```

Then start the foreground tunnel:

```bash
opensynapse connect openai \
  --tunnel-id tunnel_REPLACE_ME
```

Keep the tunnel process running while the AI client is discovering or calling the MCP tools.

### Current truth boundary

Verified:
- official tunnel-client release download;
- SHA256 verification;
- `tunnel-client` and bundled `cloudflared` installation;
- profile generation;
- OpenSynapse stdio MCP command generation;
- secret environment reference;
- local test suite.

Not yet claimed:
- a real OpenAI account tunnel reaching ChatGPT;
- ChatGPT invoking a real OpenSynapse node through that tunnel.

That claim will be added only after a real authorized E2E passes.

## First-value test

A new user should be able to:
1. install;
2. run Doctor;
3. connect an MCP client;
4. read an allowed file;
5. make one explicitly allowed change;
6. verify the observable result.

If this path needs NS-specific knowledge or manual command relay, it is a product bug.

## Android / Termux

Fast path:

```bash
curl -fsSL https://raw.githubusercontent.com/nslabhwan/ns-agent-reliability/main/install.sh | bash
```

The default Android workspace is `~/OpenSynapseWorkspace` and is read/write enabled. Other phone paths are not automatically exposed. Android installs the dependency-free core and uses `opensynapse serve --transport stdio`; FastMCP HTTP is a Linux optional extra.

See [ANDROID_TERMUX.md](ANDROID_TERMUX.md).
