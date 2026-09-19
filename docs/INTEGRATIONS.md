# From your agent stack to a Doctor snapshot

The Doctor does **not** require a new agent runtime, tracing vendor, database, or SDK. It consumes a small normalized JSON snapshot assembled from evidence your stack already exposes.

This guide describes evidence mapping, not a claim that the Doctor automatically understands every framework-specific trace format.

## Normalized evidence model

Start from `examples/doctor_snapshot_template.json`. Populate only fields you can support with evidence. Missing fields remain **UNKNOWN** and do not fire findings.

Useful evidence sources include:

- runtime/checkpoint state;
- tool/MCP schemas and tool lists;
- retry and task lineage records;
- trace/span/tool-call events;
- deployment and rollback receipts;
- observed result evidence after mutations.

Never paste credentials, private keys, cookies, customer PII, or unrelated production data into a Doctor snapshot.

## LangGraph

LangGraph persists graph state as checkpoints organized by threads and can retain pending writes for fault-tolerant resume. Those artifacts are useful for checking resume, redispatch, ownership and result-evidence assumptions.

Official reference: https://docs.langchain.com/oss/python/langgraph/persistence

- `resume`: use `thread_id`, checkpoints and state history. Check whether resume works from bounded persisted state.
- `redispatch`: use pending writes and task records. Check whether completed work can run again after recovery.
- `authorities`: inspect nodes/services that can write the same state. Check for competing mutation authority.
- `verification`: use state observed after a write. Check whether completion has result evidence.

Do not infer a failure merely because a framework supports replay. Record a failure only when your observed execution or configuration matches the Doctor field semantics.

## OpenAI Agents SDK

The Agents SDK has built-in tracing for agent runs, tool calls, handoffs, guardrails and custom events, and supports custom trace processors. That makes traces a useful evidence source without adding another observability database.

Official references:
- https://openai.github.io/openai-agents-python/ref/tracing/
- https://openai.github.io/openai-agents-python/ref/tracing/create/

- `redispatch` / `mutation`: inspect trace IDs and tool spans for repeated completed mutations.
- `public_tools` / `tools`: inspect function and MCP spans to identify callable and mutating tools.
- `authorities`: inspect handoff/task boundaries for competing mutation paths.
- `verification`: use custom verification spans/events to confirm the requested effect was observed.

Tracing may contain sensitive inputs/outputs. Redact or summarize before building the snapshot.

## CrewAI

CrewAI exposes Crews, Tasks, Tools and Flows; Flows are designed around event-driven state, persistence/resume, and CrewAI supports callbacks/hooks around execution. Use those existing records as evidence rather than adding an NS runtime.

Official references:
- https://docs.crewai.com/
- https://docs.crewai.com/learn/using-annotations

- `resume`: use Flow state and persisted execution to test bounded durable recovery.
- `redispatch` / `verification`: use callbacks and run logs to detect repeated terminal work and missing result evidence.
- `public_tools` / `tools`: inspect tools assigned to agents for excessive capability.
- `authorities`: inspect multiple Crews/Flows writing shared state for ambiguous mutation authority.

## MCP servers and clients

MCP servers expose tools with names, input schemas, optional output schemas and annotations. Clients discover them with `tools/list`, and servers can notify clients when the list changes.

Official reference: https://modelcontextprotocol.io/specification/2025-06-18/server/tools

- `public_tools`: compare `tools/list` responses and watch for uncontrolled surface growth.
- `schema`: compare tool/schema snapshots across releases for stale-client authority.
- `tools`: compare descriptions/annotations with implementation authority, especially READ surfaces.
- `rollback`: compare rollback tool lists and reject restoration of deprecated tools.

Tool annotations are not proof by themselves. Verify actual authority at the implementation or execution boundary.

## Minimal workflow

1. Export or summarize existing evidence.
2. Redact sensitive material.
3. Copy `examples/doctor_snapshot_template.json`.
4. Populate only evidence-backed fields.
5. Run `ns-reliability snapshot.json --json`.
6. Treat missing fields as UNKNOWN, not healthy.
7. For HIGH/CRITICAL findings, verify the underlying evidence before remediation.
