# OpenSynapse — Getting Started

## 3-minute first-value proof

If you want to verify that OpenSynapse is doing real bounded machine work before configuring an AI connection:

```bash
curl -fsSL https://raw.githubusercontent.com/nslabhwan/ns-agent-reliability/main/try.sh | bash
```

This creates `~/OpenSynapseWorkspace`, installs the node with that single writable boundary, runs Doctor, writes `OPENSYNAPSE_DEMO.txt` through the bounded runtime, and reads it back to verify the observable result.


Use this page if you want to try the current public alpha without reading the whole repository first.

OpenSynapse turns a machine you own into a bounded MCP work node. The current public alpha supports Linux and Android/Termux.

## 0. What is verified today?

| Path | Current status |
| --- | --- |
| Linux install + bounded node | VERIFIED |
| Linux local HTTP MCP write/readback/command E2E | VERIFIED |
| Android/Termux fresh public install | VERIFIED on a real device |
| Android stdlib MCP, 7 tools, real write/readback | VERIFIED on a real device |
| OpenAI Secure MCP Tunnel profile preparation | VERIFIED |
| Real OpenAI account -> ChatGPT -> OpenSynapse write/readback E2E | VERIFIED 2026-09-20 |
| Android -> ChatGPT remote E2E | NOT YET CLAIMED |
| Windows / macOS package | NOT YET AVAILABLE |

Choose the path below that matches what you have.

---

## A. Android / Termux

### What you need

- an Android phone;
- Termux;
- Internet access.

The installer can install Python and Git through Termux when they are missing.

### 1. Install

Run this inside Termux:

```bash
curl -fsSL https://raw.githubusercontent.com/nslabhwan/ns-agent-reliability/main/install.sh | bash
```

The default workspace is:

```text
~/OpenSynapseWorkspace
```

That workspace is readable and writable by OpenSynapse. Other phone paths are not automatically exposed.

### 2. Check the node

```bash
opensynapse doctor
opensynapse status
```

If your shell cannot find the command yet, use:

```bash
$HOME/.local/bin/opensynapse doctor
$HOME/.local/bin/opensynapse status
```

A healthy Android node should report:

```text
node_type: android-termux
authority: SELF_HOSTED_ANDROID
```

### 3. Run the local MCP server

Android uses the dependency-free stdlib MCP transport:

```bash
opensynapse serve --transport stdio
```

Use this with a local MCP client that can launch a stdio server. Stop it with Ctrl+C when you are finished.

### Android truth boundary

The public Android path has been verified from a fresh GitHub clone on a real Android/Termux device through install, identity check, MCP tool discovery, file write, and file readback.

The current public Android alpha does **not** yet claim a real ChatGPT account -> Secure MCP Tunnel -> Android OpenSynapse E2E. Do not interpret the local Android verification as that remote connection proof.

More Android details: [ANDROID_TERMUX.md](ANDROID_TERMUX.md)

---

## B. Linux / server

### What you need

- Linux;
- Python 3.11+;
- Git;
- a directory you want OpenSynapse to access.

### 1. Clone

```bash
git clone https://github.com/nslabhwan/ns-agent-reliability.git
cd ns-agent-reliability
```

### 2. Choose a workspace

Example:

```bash
mkdir -p "$HOME/opensynapse-workspace"
```

Install with read/write access limited to that workspace:

```bash
OPENSYNAPSE_ROOT="$HOME/opensynapse-workspace" \
OPENSYNAPSE_WRITE_ROOT="$HOME/opensynapse-workspace" \
bash install.sh
```

If you want read-only access, omit OPENSYNAPSE_WRITE_ROOT.

### 3. Check the boundary

```bash
opensynapse doctor
opensynapse status
```

Read the printed roots before connecting any AI client. Those roots are the machine access boundary.

### 4. Run MCP locally

Stdio:

```bash
opensynapse serve --transport stdio
```

Linux also supports the optional local HTTP transport:

```bash
opensynapse serve --transport http
```

Default local endpoint:

```text
http://127.0.0.1:8767/mcp
```

Do not expose that unauthenticated loopback endpoint directly to the public Internet.

---

## C. Connect a private node through OpenAI Secure MCP Tunnel

This section is the verified OpenAI tunnel path. On 2026-09-20 a real ChatGPT plugin attached through OpenAI Secure MCP Tunnel, created a file in the configured OpenSynapse workspace, read it back, and matched an independently recomputed host SHA-256.

OpenAI's current Secure MCP Tunnel documentation says you need:

- a tunnel ID from OpenAI Platform tunnel settings;
- a runtime API key for tunnel-client;
- a private MCP server reachable by tunnel-client over stdio or HTTP.

Official guide: https://developers.openai.com/api/docs/guides/secure-mcp-tunnels

### 1. Create the two OpenAI account-side objects

In OpenAI Platform, create one Tunnel and one restricted runtime API key with **Tunnels Read + Use**. Keep the raw API key local; do not paste it into ChatGPT.

### 2. Run one guided onboarding command

```bash
curl -fsSL https://raw.githubusercontent.com/nslabhwan/ns-agent-reliability/main/onboard-openai.sh | bash
```

The guide prints the official Platform pages, asks for the Tunnel ID, then delegates the local work to the verified connection path. It:

- reuses or installs OpenSynapse;
- prompts for the runtime key only on the local TTY;
- stores it in a mode-600 local file;
- does not store the raw key in onboarding state;
- passes only a `file:` reference to the official tunnel-client;
- runs the official Tunnel Doctor;
- prefers a Linux `systemd --user` service for restart recovery;
- falls back to a managed background process when the user service manager is unavailable;
- prints the exact ChatGPT plugin fields and final E2E verification prompt.

Check recovery state with:

```bash
opensynapse autostart status
```

`READY_AFTER_LOGIN` means crash recovery is active and the service returns after the user logs in. For an unattended Linux server, the status output also prints the one-time `loginctl enable-linger` command when linger is disabled.

### 3. Add the ChatGPT plugin once

In ChatGPT plugin settings create a custom MCP plugin, choose **Tunnel**, select the same Tunnel, and use **No authentication** for the tunneled stdio OpenSynapse target. Account/workspace UI availability can change, so use the options actually exposed by your ChatGPT workspace.

### 4. Prove real work

Ask ChatGPT to inspect the OpenSynapse workspace, create a file, read it back, and verify SHA-256. The exact verified 2026-09-20 run is recorded in `docs/REAL_CHATGPT_E2E_20260920.md`.

---

## D. What can the current node expose?

The common public MCP surface has seven bounded tools:

- dc_status
- dc_read_text
- dc_list_directory
- dc_tail_log
- dc_process_status
- dc_write_text
- dc_run_bounded

Execution is not an unrestricted public shell. Commands must be explicitly configured and are executed without shell expansion.

---

## E. First useful test

After your MCP client is connected, keep the first task deliberately small.

Example sequence:

1. Ask it to list the allowed workspace.
2. Ask it to read one test file.
3. Ask it to create `hello-from-opensynapse.txt` inside the allowed write root.
4. Ask it to read the file back.
5. Confirm the result exists on the machine.

That is the OpenSynapse completion model:

```text
request -> execute -> observable result -> verify once
```

---

## F. Common problems

### `opensynapse: command not found`

Try:

```bash
$HOME/.local/bin/opensynapse status
```

Then add `$HOME/.local/bin` to your shell PATH if needed.

### `root does not exist`

Create the directory first, then reinstall with that directory as OPENSYNAPSE_ROOT.

### The AI can read but cannot write

Writing is intentionally separate. Reinstall or configure an explicit write root. On Android the default `~/OpenSynapseWorkspace` is already writable.

### Tunnel says CONTROL_PLANE_API_KEY is missing

Export the runtime key in the shell that starts the tunnel. OpenSynapse intentionally does not store the literal secret.

### ChatGPT does not show the expected MCP capability

Check current ChatGPT plan/workspace support and Developer Mode permissions. The OpenAI tunnel permission and ChatGPT workspace permission are separate.

### Android installed successfully but I want ChatGPT to control it remotely

The Android local node is verified. The real ChatGPT-to-Android tunnel E2E is not yet a published claim. Track the repository for that milestone rather than assuming it has already passed.

---

## G. Security checklist

Before real work:

- verify the read roots;
- verify the write roots;
- do not expose the loopback HTTP endpoint directly to the Internet;
- do not publish runtime API keys;
- start with a disposable/test workspace;
- expand access only after you understand the boundary.

See [SECURITY.md](SECURITY.md).

---

## H. Proof and feedback

Current Android real-device evidence is recorded in:

`release/REMOTE_ANDROID_PUBLICATION_RECEIPT_20260919_OPENSYNAPSE_A3.json`

Repository:

https://github.com/nslabhwan/ns-agent-reliability

If you try OpenSynapse, use the [OpenSynapse Alpha feedback form](https://github.com/nslabhwan/ns-agent-reliability/issues/new?template=opensynapse-feedback.yml). It also asks where you heard about the project so we can distinguish real acquisition sources. Include:

- Linux or Android/Termux;
- the last step that worked;
- the first step that failed;
- what real task you wanted the AI to do;
- no secrets, tokens, private logs, or credentials.

That feedback decides what gets simplified and expanded next.
