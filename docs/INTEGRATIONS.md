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

### Evidence mapping

- **`thread_id`, checkpoints, state history**
  - Doctor field: `resume`
  - Ask: Can the run resume from bounded persisted state without raw chat history?
- **pending writes / task records**
  - Doctor field: `redispatch`
  - Ask: Can already-completed work be executed again after recovery?
- **nodes/services that can write the same state**
  - Doctor field: `authorities`
  - Ask: Is there more than one mutation authority for one target?
- **state observed after a write**
  - Doctor field: `verification`
  - Ask: Is completion backed by observed result evidence?

Do not infer a failure merely because a framework supports replay. Record a failure only when your observed execution or configuration matches the Doctor field semantics.

## OpenAI Agents SDK

The Agents SDK has built-in tracing for agent runs, tool calls, handoffs, guardrails and custom events, and supports custom trace processors. That makes traces a useful evidence source without adding another observability database.

Official references:
- https://openai.github.io/openai-agents-python/ref/tracing/
- https://openai.github.io/openai-agents-python/ref/tracing/create/

### Evidence mapping

- **trace/span IDs and tool spans**
  - Doctor fields: `redispatch`, `mutation`
  - Ask: Did the same completed mutation get dispatched again?
- **function/MCP tool spans**
  - Doctor fields: `public_tools`, `tools`
  - Ask: What can the agent invoke, and which tools can mutate?
- **handoff/task boundaries**
  - Doctor field: `authorities`
  - Ask: Can two independent paths mutate the same canonical target?
- **custom result-verification span/event**
  - Doctor field: `verification`
  - Ask: Did the system observe the requested effect, not only an agent self-report?

Tracing may contain sensitive inputs/outputs. Redact or summarize before building the snapshot.

## CrewAI

CrewAI exposes Crews, Tasks, Tools and Flows; Flows are designed around event-driven state, persistence/resume, and CrewAI supports callbacks/hooks around execution. Use those existing records as evidence rather than adding an NS runtime.

Official references:
- https://docs.crewai.com/
- https://docs.crewai.com/learn/using-annotations

### Evidence mapping

- **Flow state / persisted execution**
  - Doctor field: `resume`
  - Ask: Is recovery based on durable bounded state?
- **task/process callbacks and run logs**
  - Doctor fields: `redispatch`, `verification`
  - Ask: Was terminal work repeated, and was the result observed?
- **tools assigned to agents**
  - Doctor fields: `public_tools`, `tools`
  - Ask: Is the public capability surface larger or more privileged than intended?
- **multiple Crews/Flows writing shared state**
  - Doctor field: `authorities`
  - Ask: Is canonical mutation authority ambiguous?

## MCP servers and clients

MCP servers expose tools with names, input schemas, optional output schemas and annotations. Clients discover them with `tools/list`, and servers can notify clients when the list changes.

Official reference: https://modelcontextprotocol.io/specification/2025-06-18/server/tools

### Evidence mapping

- **`tools/list` response**
  - Doctor field: `public_tools`
  - Ask: Has the externally visible surface grown beyond a manageable boundary?
- **tool name/schema snapshots across releases**
  - Doctor field: `schema`
  - Ask: Can a stale client override or resurrect an obsolete contract?
- **tool descriptions/annotations + implementation review**
  - Doctor field: `tools`
  - Ask: Is a nominal READ surface capable of mutation?
- **rollback tool list**
  - Doctor field: `rollback`
  - Ask: Did rollback restore deprecated tools?

Tool annotations are not proof by themselves. Verify actual authority at the implementation or execution boundary.

## Minimal workflow

1. Export or summarize existing evidence.
2. Redact sensitive material.
3. Copy `examples/doctor_snapshot_template.json`.
4. Populate only evidence-backed fields.
5. Run `ns-reliability snapshot.json --json`.
6. Treat missing fields as UNKNOWN, not healthy.
7. For HIGH/CRITICAL findings, verify the underlying evidence before remediation.
