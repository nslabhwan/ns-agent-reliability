# Security Policy

## Reporting

Do not open a public issue containing credentials, private infrastructure identifiers, provider tokens, or unredacted logs. Use GitHub Private Vulnerability Reporting from this repository's Security tab for sensitive security reports.

## Security model

This project assumes the chat-facing control plane is not a trusted production shell. Deployments should preserve:

- absolute read-root allowlists;
- secret-path denial and redaction;
- isolated sandbox writes;
- bounded capability-oriented subprocess execution;
- no arbitrary `shell=True` execution from chat arguments;
- evidence-bound worker reports;
- separate operational Gate/approval for SSOT/runtime mutation;
- compare-and-swap or equivalent baseline protection for edits;
- explicit authority labels on observations/drafts/applies;
- unknown-safe handling of auth/quota/resource state.

## Public repository hygiene

Never commit:

- API keys, OAuth tokens, cookies or credentials;
- private keys/certificates;
- real provider credential stores;
- embedded credential remote URLs;
- private server usernames/addresses unless intentionally public;
- production environment files;
- raw private chat exports;
- sensitive logs.

## Threats considered

The architecture is explicitly designed to reduce risks from path traversal, prompt-induced arbitrary shell execution, secret-file reads, stale-state promotion, confused authority, worker self-verification, replayed context contamination, provider/session readiness confusion, and accidental production mutation from sandbox code.

## Non-guarantee

The current OpenSynapse public alpha has not completed an independent third-party security audit. Do not treat the alpha as a production control plane without adapting the policies to your environment, reviewing the configured read/write/command boundaries, and running the relevant negative/UAT suite.
