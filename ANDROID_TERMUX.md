# OpenSynapse Android / Termux Alpha

OpenSynapse can use an Android phone itself as an independent work node through Termux.

This is not "phone as a remote control for a PC." The OpenSynapse runtime executes on the phone.

## Fast install

From Termux:

```bash
curl -fsSL https://raw.githubusercontent.com/nslabhwan/ns-agent-reliability/main/install.sh | bash
```

The installer:
- detects Termux;
- installs Python/Git with `pkg` only if missing;
- creates an isolated Python environment;
- installs the dependency-free OpenSynapse core (no FastMCP/Rust required);
- creates `~/OpenSynapseWorkspace`;
- grants OpenSynapse read/write only inside that workspace by default.

Then:

```bash
opensynapse doctor
opensynapse status
opensynapse serve --transport stdio
```

The stdio MCP server exposes the same bounded `dc_*` tool contract as Linux.

If `~/.local/bin` is not yet on your PATH:

```bash
$HOME/.local/bin/opensynapse doctor
```

## What the first Android Alpha proves

The first portable Android node is intentionally small. It uses Python stdlib for MCP stdio so Android does not need the Linux FastMCP/watchfiles dependency chain:

- status / Doctor;
- bounded directory and file reads;
- bounded file writes;
- safe command execution when explicitly enabled;
- the same result-verification semantics as the Linux node.

The private NS Phone Local system has broader capabilities, including media and device workflows. Those are being reimplemented into the public node without creating a runtime dependency on the private system.

## Safety default

On Android/Termux, the default writable area is:

```text
~/OpenSynapseWorkspace
```

OpenSynapse does not automatically expose the rest of Termux home or Android shared storage.

To choose a different explicit workspace:

```bash
OPENSYNAPSE_ROOT=$HOME/my-ai-work \
OPENSYNAPSE_WRITE_ROOT=$HOME/my-ai-work \
bash install.sh
```

## Current truth boundary

The portable code path shares the OpenSynapse core with Linux while keeping each device runtime independent.

Do not treat:
- the private NS Phone Local connector,
- private NS Android helper,
- legacy runtime,
- server control plane

as dependencies of this public Android node.

The first publication gate is a fresh install and real read/write verification on an actual Android/Termux device.
