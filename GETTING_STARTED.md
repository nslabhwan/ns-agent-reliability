# OpenSynapse — Getting Started

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
| Real OpenAI account -> ChatGPT -> OpenSynapse E2E | NOT YET CLAIMED |
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

This section is for the current OpenAI tunnel path. The OpenSynapse tunnel **preparation path** is verified; a real authorized OpenAI account -> ChatGPT -> OpenSynapse E2E is still listed as pending until that exact path is observed.

OpenAI's current Secure MCP Tunnel documentation says you need:

- a tunnel ID from OpenAI Platform tunnel settings;
- a runtime API key for tunnel-client;
- a private MCP server reachable by tunnel-client over stdio or HTTP.

Official guide: https://developers.openai.com/api/docs/guides/secure-mcp-tunnels

### 1. Prepare the OpenSynapse tunnel profile

```bash
opensynapse connect openai \
  --tunnel-id tunnel_REPLACE_ME \
  --prepare-only
```

OpenSynapse stores an environment-variable reference for the API key, not the literal key value.

### 2. Load the runtime API key

```bash
read -rsp "OpenAI runtime API key: " CONTROL_PLANE_API_KEY
echo
export CONTROL_PLANE_API_KEY
```

Do not commit the key to Git, paste it into issues, or put it in the OpenSynapse config.

### 3. Run the official tunnel Doctor

```bash
opensynapse connect openai \
  --tunnel-id tunnel_REPLACE_ME \
  --no-run
```

### 4. Start the tunnel

```bash
opensynapse connect openai \
  --tunnel-id tunnel_REPLACE_ME
```

Keep that process running while the supported OpenAI client is discovering or calling the MCP tools.

### 5. ChatGPT plan / workspace note

OpenAI currently documents full MCP write/modify support for ChatGPT Business, Enterprise and Edu in beta. Pro can use custom MCPs in developer mode with read/fetch permissions, but full MCP write support is not currently documented for Pro.

Because OpenAI product availability changes, check the current official page before troubleshooting a missing ChatGPT UI:

https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt

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

If you try OpenSynapse, use the repository feedback issue form and include:

- Linux or Android/Termux;
- the last step that worked;
- the first step that failed;
- what real task you wanted the AI to do;
- no secrets, tokens, private logs, or credentials.

That feedback decides what gets simplified and expanded next.
