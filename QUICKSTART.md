# OpenSynapse Linux Alpha — Quickstart

OpenSynapse turns a Linux machine you own into a bounded MCP work node for AI clients.

## 1. Install

The safest current path is to clone / inspect the repository, then run:

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

## 3. Start the local MCP node

```bash
opensynapse serve --transport http
```

Default endpoint:

```text
http://127.0.0.1:8767/mcp
```

Do not expose that unauthenticated loopback endpoint directly to the public Internet.

## 4. ChatGPT connection status

Current Alpha proves the Linux node and bounded MCP execution layer.

The zero-config OpenSynapse HTTPS gateway / public ChatGPT plugin flow is the next integration milestone. Until that is published, advanced users may place the loopback MCP endpoint behind a reviewed authenticated HTTPS ingress supported by their AI client.

## First-value test

A new user should be able to:
1. install;
2. run Doctor;
3. connect an MCP client;
4. read an allowed file;
5. make one explicitly allowed change;
6. verify the observable result.

If this path needs NS-specific knowledge or manual command relay, it is a product bug.
