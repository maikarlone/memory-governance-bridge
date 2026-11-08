# Security Policy

## Scope

This repository is a read-only reference implementation. It is not a production service and has no multi-tenant authentication, rate limiting, or SLA.

## Secrets

- Never commit tokens, API keys, `.env` files, cookies, or credentials.
- Provide client credentials through environment variables at runtime.
- Do not paste credentials into issues, pull requests, logs, or test fixtures.
- The example tokens in `examples/clients.example.json` are demo values only and must not be reused.

## Reporting

Report a suspected secret exposure or vulnerability privately to the maintainers. Do not open a public issue containing credentials or private data.

## Secure defaults

- `MEMORY_BRIDGE_ENABLED` defaults to unset/disabled.
- The adapter exposes no write route.
- The bridge makes no network request when disabled.
- Error responses must not include request headers or credentials.

## Out of scope

- Production deployment hardening.
- Multi-user authorization.
- Encryption at rest.
- Vendor memory-core vulnerabilities.
