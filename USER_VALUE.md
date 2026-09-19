# OpenSynapse — User Value First

Status: ACTIVE PRODUCT REQUIREMENT
Effective: 2026-09-19
Source: S explicit direction — execution stage must be designed from the installer's / user's point of view.

## Product question

Every implementation decision must answer:

> What becomes easier, faster, safer, or newly possible for a normal user immediately after installing OpenSynapse?

Internal architecture, NS terminology, module boundaries, and historical implementation are secondary.

## Core user promise

> Install once. Keep using ChatGPT the way you already do. Now it can safely do real work on the computer, server, and phone you own — and verify that the work actually happened.

The user should not need to become an MCP, terminal, cloud, Termux, tunnel, or agent-infrastructure expert.

## Before / After

### Before OpenSynapse

A user commonly has to:
- copy commands from ChatGPT into Terminal;
- copy errors back into ChatGPT;
- upload / download files manually;
- switch between ChatGPT, SSH, IDE, phone, browser, and server dashboards;
- repeatedly explain machine state in new chats;
- configure separate MCP servers and permissions;
- manually check whether a claimed task really succeeded;
- babysit long-running work;
- reconnect or rebuild integrations after interruptions.

### After OpenSynapse

The same user can ask naturally:
- "이 서버 로그 보고 원인 찾아서 고쳐줘."
- "이 프로젝트 테스트 깨진 것 수정하고 검증해."
- "폰에서 영상 추출해서 자막과 프레임까지 정리해."
- "PC의 이 폴더 정리해."
- "어제 하던 작업 이어서 상태 확인해."
- "끝났으면 실제 결과까지 확인해."

OpenSynapse:
1. identifies an authorized paired device;
2. chooses the bounded capability required;
3. executes on that device;
4. handles recoverable failures without making the user relay commands;
5. verifies the observable result;
6. returns a concise result and evidence.

## Primary user benefits

### 1. No more copy-paste operator work

Highest-value benefit.

The user stops acting as a human relay between AI and Terminal / SSH / phone tools.

Success test:
A normal task can go from request to verified result without the user copying a command or log between systems.

### 2. One AI interface for multiple machines

The user does not need a different mental model for:
- Linux server
- desktop / laptop
- Android phone

They remain separate execution nodes internally, but the user sees one OpenSynapse connection and a device list.

Success test:
The same natural request style works across paired node types.

### 3. Real work, not only advice

OpenSynapse should move ChatGPT from:
"Here is what you can type"
to:
"I performed it, and here is the verified result."

User-visible actions include:
- read / organize files
- edit code or documents
- run tests / builds
- inspect logs and processes
- Git operations
- media extraction / conversion
- approved application / device operations
- server maintenance within configured boundaries

### 4. Verified completion

The user should not have to trust an AI's self-report.

Every meaningful action should end with a bounded observable check when possible.

User language:
- "수정했습니다" is not enough.
- "수정했고 테스트가 통과했으며 결과 파일이 존재하는 것을 확인했습니다" is the product behavior.

### 5. Long work without babysitting

Where supported, OpenSynapse should manage jobs that outlive one tool call or one chat turn and expose status / resume semantics.

The user should be able to leave and return without reconstructing the entire machine state manually.

### 6. Safe access without becoming a security engineer

Defaults:
- explicit roots
- bounded actions
- no arbitrary public unauthenticated shell
- secrets excluded / redacted
- write / destructive capabilities constrained
- device pairing / revocation visible

The user-facing benefit is simple:
"My AI can work on my machine without giving the whole Internet a shell."

### 7. Existing ChatGPT habits remain useful

The product should fit the user's existing ChatGPT / Work / Codex behavior instead of requiring a new AI chat application.

OpenAI's current plugin model allows reusable tools / connected capabilities to be installed and used across supported ChatGPT and Codex surfaces, subject to the user's plan, workspace and platform availability.

### 8. Fast first value

A user should not have to understand the architecture before seeing value.

Target first-run journey:
install -> pair -> open ChatGPT -> ask one real request -> see verified result.

No tutorial should be longer than the first successful task.

## Initial user segments

### A. AI-assisted developers / vibe coders

Pain:
ChatGPT can explain code, but the human still shuttles commands, files, test output, deployments and errors.

Immediate OpenSynapse value:
direct project inspection, edits, tests, Git, server diagnostics and verification.

This is the first Linux / desktop launch audience.

### B. Small operators / solo builders

Pain:
They manage a website, server, automations and content without a dedicated operations team.

Immediate value:
one conversational interface for server status, files, deployment checks, logs, content / media jobs and routine automation.

### C. Power users who work from their phone

Pain:
Real technical work from mobile is awkward because terminals, SSH, files, browsers and AI chat are fragmented.

Immediate value:
ChatGPT on mobile can trigger authorized work on the phone itself or on paired machines.

Phone Local is a major public differentiator and demo surface.

### D. Teams / businesses — later paid expansion

Pain:
multiple machines, permissions, auditability, shared automation, managed connectivity and support.

Paid-value candidates:
- managed gateway
- team / fleet management
- RBAC / SSO
- audit retention
- centralized policy
- SLA / support
- managed update / recovery
- enterprise deployment

Do not make these enterprise features prerequisites for individual adoption.

## Product priority by user value

P0 — Human relay elimination
- install
- pair
- bounded read / execute / change
- result verification

P1 — One-device first success
- clean Linux server first
- task completed from ChatGPT without manual command relay

P2 — Multi-device identity
- server + PC + phone listed as paired nodes
- explicit device targeting
- safe routing

P3 — Phone Local portable capability
- actual local phone work
- media / file / app / device workflows where safely portable

P4 — Resume / jobs / continuity
- long-running jobs
- reconnect / resume
- concise current-state handoff

P5 — Advanced remote / virtual screen
- only after basic user value works cleanly

## What is NOT a primary user benefit

Do not lead marketing or onboarding with:
- Goal DAG
- fencing token
- control plane
- event ledger
- Gate
- provider routing
- DNA
- policy schema
- internal NS version history

Those can power reliability internally or appear in technical documentation.

Users buy:
- less manual work
- more things AI can actually do
- less context switching
- safer access
- verified results
- continuity

## First-run acceptance test

An outsider who has never seen NS must be able to:

1. install OpenSynapse from one public entry point;
2. pair one Linux machine;
3. install / connect the OpenSynapse ChatGPT plugin;
4. open a normal supported ChatGPT surface;
5. ask: "이 컴퓨터의 작업 폴더 상태를 확인해줘";
6. receive a real bounded result;
7. ask for one harmless file change or test execution;
8. have the action executed and read back / verified;
9. understand how to revoke the connection.

No NS operator should need to intervene.

## Website / README message hierarchy

1. Outcome:
   "Let ChatGPT actually work on your computer, server and phone."

2. Friction removed:
   "No command copy-paste. No manual log relay. No separate AI app."

3. Trust:
   "Bounded access. Your devices stay under your control. Results are verified."

4. Proof:
   real 30–90 second demos.

5. Install CTA:
   "Install OpenSynapse"

Architecture comes after the first CTA.

## Marketing evidence loop

Every real NS operation that is safe to sanitize should become evidence of a user benefit.

Format:
user request -> real device action -> obstacle / recovery if relevant -> verified result

Examples:
- ChatGPT fixes a server problem without SSH copy-paste.
- ChatGPT extracts video / audio / captions / frames on a phone.
- ChatGPT edits code, runs tests, and verifies the build.
- ChatGPT resumes a previously interrupted task.

Do not make demos look like synthetic product commercials when a real workflow is stronger.

## Decision filter

Before adding a feature, ask:

1. Does this remove a manual user step?
2. Does this make a new real-world task possible?
3. Does this reduce setup / reconnection friction?
4. Does this increase safety or confidence without adding user ceremony?
5. Does this help acquisition, activation, retention, or future paid expansion?

If the answer is no to all five, it is not a launch priority.
