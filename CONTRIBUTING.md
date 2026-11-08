# Contributing

## Governance red lines

Pull requests that do any of the following are rejected:

- enable write access by default;
- add a write tool to an agent-facing MCP server;
- put tokens, API keys, or `.env` files in repository configuration;
- log credentials or full request headers;
- include real memory data, snapshots, logs, or private project facts;
- weaken the default-disabled bridge behavior.

## Read-only rule

The reference implementation is read-only. New write-path work must remain behind a controlled script, an explicit approval step, and a separate design review. It must not add a write route to the adapter or bridge.

## Pull request checklist

- [ ] `python -m unittest discover -s tests -v` passes.
- [ ] No secrets, tokens, `.env`, real data, logs, or snapshots.
- [ ] No private project names, internal paths, or production endpoints.
- [ ] New behavior has a test or a documented manual check.
- [ ] Documentation states whether the change is reference-only.
- [ ] `MEMORY_BRIDGE_ENABLED` remains opt-in.

## Commit style

Use short, imperative commit messages, for example:

```text
add no-direct-answer marker test
fix disabled bridge network guard
```

## License

By contributing, you agree that your contribution is licensed under Apache-2.0.
