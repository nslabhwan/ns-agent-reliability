# Real ChatGPT → OpenSynapse E2E — 2026-09-20

Status: **PASS**

## Path observed

`ChatGPT custom plugin → OpenAI Secure MCP Tunnel → official tunnel-client v0.0.14 → OpenSynapse stdio MCP → configured workspace`

## Observable task

ChatGPT was asked to inspect the OpenSynapse workspace, create `OPENSYNAPSE_E2E.txt`, read it back, and verify SHA-256.

Observed host artifact:

- workspace: `/home/ec2-user/OpenSynapseWorkspace`
- file: `OPENSYNAPSE_E2E.txt`
- size: `97 bytes`
- mode: `600`
- owner: `ec2-user:ec2-user`
- SHA-256: `20ea4c8216f211d4043b191d20c40d9905dc0865847c30e3e206232226ed6cb1`

Content:

```text
OpenSynapse E2E verification
status=PASS_CANDIDATE
workspace=/home/ec2-user/OpenSynapseWorkspace
```

The host SHA-256 was recomputed independently after ChatGPT reported completion and matched exactly. The OpenSynapse launcher, official tunnel-client, and stdio MCP process were all still alive during the independent verification.

## What this proves

This proves a real authorized ChatGPT account can invoke OpenSynapse through the Tunnel and complete bounded write/readback work inside the configured workspace. It does **not** imply unrestricted shell or unrestricted filesystem access.
