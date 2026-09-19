# NS Unified Open Base — Current Product Direction

Status: ACTIVE
Effective: 2026-09-19
Authority: S explicit product / distribution direction
Publication lineage: reuse NS_GPT_CONNECTION_OPEN_SOURCE; do not create a competing public repository.

## Outcome

Turn the real NS server / phone / PC execution experience into one open-source base that an outside user can install through one onboarding flow and then use from supported ChatGPT surfaces, including ordinary Chat, Work, and Codex, without manually assembling MCP servers, tunnels, scripts, policy files, or per-product packages.

The immediate business objective is distribution and user acquisition:
- maximize qualified users and real usage before feature gating;
- obtain first external installs, repeat users, contributors, and future paid users;
- keep the useful core open source;
- monetize later around managed connectivity, fleet/team operation, enterprise controls, hosted services, premium automation, support, and evolved system capabilities.

## Product identity

One public umbrella product. Working public umbrella name: OpenSynapse.

Public user promise:

> Install once. Connect ChatGPT to the machines you own. Ask naturally. The work happens on the right device and is verified.

Do not lead with internal NS architecture names.

## Architecture rule

Unified UX does NOT mean coupled runtimes.

Keep each execution node independent:
- Server node
- Desktop / PC node
- Phone node

A single installer / onboarding layer detects the target and installs the matching independent runtime. No node may become a hidden runtime dependency of another node.

Shared public contracts:
- bounded read / execute / change
- typed MCP actions
- authentication / pairing
- verification receipts
- update / doctor / recovery
- plugin skill guidance

## Target user flow

1. User installs OpenSynapse once on a target device.
2. Installer detects OS / device type.
3. It installs the appropriate local companion runtime and runs Doctor.
4. It creates or joins the user's OpenSynapse device identity.
5. It establishes outbound authenticated connectivity to a stable HTTPS MCP endpoint.
6. It opens / guides the one-time ChatGPT plugin installation and authorization step.
7. New ChatGPT chats can call the same plugin from supported surfaces.
8. User can say natural requests such as:
   - "내 서버 로그 확인하고 원인 찾아줘"
   - "이 폴더 코드 수정하고 테스트해"
   - "폰에서 유튜브 영상 추출해"
   - "이 작업을 PC에서 계속해"
9. The plugin resolves the intended paired node and invokes only bounded capabilities.
10. Completion is reported only after observable verification.

The user must not have to understand MCP, Cloudflare Tunnel, Termux internals, service files, JSON policy, or NS internal naming to get first value.

## Distribution surfaces

One plugin package should target supported ChatGPT / Codex plugin surfaces:
- ordinary ChatGPT chats
- ChatGPT Work
- Codex in supported ChatGPT desktop surfaces
- Codex CLI plugin marketplace

Public plugin packaging should use the current OpenAI plugin format and stable remote HTTPS MCP endpoint requirements.

## Open-source scope now

Open aggressively:
- install / setup / update / doctor
- bounded local execution core
- server node
- device / phone node portable implementation
- workflow verification primitives
- reliability doctor / incident-derived guards
- plugin skills / manifests / guides
- self-hosted connectivity path
- examples and real demonstrations

Do not publish:
- credentials / tokens / cookies / private keys
- private NS URLs or account identifiers
- private conversations
- Trading strategy / financial SSOT
- private customer data
- raw private production logs
- environment-specific secrets

This is a security/privacy boundary, not product feature gating.

## Existing components to collapse under the umbrella

Reuse rather than rewrite where technically valid:
- NS_GPT_CONNECTION_OPEN_SOURCE — publication lineage / public monorepo candidate
- NS Direct Channel — server / bounded MCP execution core
- Universal Verified Workflow Core — verified workflow / completion semantics
- NS Agent Reliability Doctor — diagnostics / regression knowledge
- Phone Local NextGen — phone execution knowledge and proven capability, reimplemented portably with zero legacy runtime link
- Physical / Virtual Remote — optional later device-control modules after clean portable extraction

Existing separate product names become components, modules, or historical package names; they are not separate acquisition funnels.

## One-install implementation contract

The install UX may use platform-specific bootstrap commands/packages internally, but every platform must converge on the same command model:

- opensynapse install
- opensynapse connect
- opensynapse status
- opensynapse doctor
- opensynapse update
- opensynapse devices

Target packaging:
- Linux: install script / package
- macOS: package or install script
- Windows: PowerShell / package
- Android: APK or controlled Termux bootstrap during transition

The installer should automatically generate safe defaults and must not enable arbitrary shell execution by default.

## Connectivity model

Public plugin submission requires a stable externally reachable HTTPS MCP endpoint.

Therefore the public architecture has two compatible modes:
1. Managed relay / rendezvous: easiest zero-config onboarding and future commercial surface.
2. Self-hosted gateway: open-source path for users who do not want managed infrastructure.

Device nodes connect outbound. Users should not expose unauthenticated localhost services directly to the Internet.

## Immediate priority order

P0 — Consolidate product story and repo surface
- one umbrella name / README / demo / quickstart;
- current products become modules;
- no competing repository.

P1 — One installer + Doctor
- first target: clean Linux server install using current portable Direct Channel core;
- second target: Android Phone Local portable install;
- add desktop targets without weakening boundaries.

P2 — Stable plugin package
- skill + MCP registration package;
- ordinary Chat / Work / Codex usage guide;
- public submission-compatible HTTPS endpoint.

P3 — Pairing / node routing
- one user -> multiple independent nodes;
- explicit target selection when ambiguous;
- safe default routing and device status.

P4 — Real outsider E2E
- fresh user, fresh machine;
- install -> plugin -> natural chat request -> real mutation -> verification;
- no NS operator intervention.

P5 — Distribution
- GitHub README/demo;
- OpenAI public plugin directory;
- YouTube / Shorts;
- Reddit / Hacker News / GeekNews;
- X / LinkedIn;
- website landing page with install CTA.

## Marketing operating rule

Until real external usage exists, optimize for reach, installation, activation, and learning — not artificial scarcity.

Every strong internal NS task should be considered for a sanitized public demo:
real request -> execution -> failure if any -> recovery -> verified artifact.

One engineering event should produce multiple distribution assets.

## First success metrics

Do not use repository completeness as success.

Track:
- first 10 external installs
- first 3 users who complete a real task
- first repeat user
- first external issue / PR
- first 100 GitHub stars or equivalent qualified audience milestone
- first paid managed/support/evolved-system user

The first commercial objective remains a real external payment, but acquisition must be established before optimizing pricing.

## Non-goals

- Do not build another manager/router/queue/store just for productization.
- Do not merge server/phone/desktop runtime state.
- Do not require users to learn NS internal architecture.
- Do not keep separate marketing funnels for every internal module.
- Do not claim platform support before one real E2E proves it.

## Current decision

The previous public wedge "Agent Reliability Doctor" remains useful evidence and a module, but it is no longer sufficient as the public identity of the full NS capability.

The public direction is now a unified installable AI work infrastructure base.
