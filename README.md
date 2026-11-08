# Memory Governance Bridge

## English overview

A minimal, **read-only reference implementation** of a governance layer between AI agents and a memory core. It is a sidecar, not a memory database.

It demonstrates:

- token-bound project/identity binding without trusting client-supplied identity;
- a default-disabled MCP stdio bridge;
- explicit empty-result semantics: `ok`, `no_match`, `service_down`, `low_relevance`, `no_direct_answer`;
- observe-mode answer matching that marks results instead of silently filtering them;
- a human-approved write path design (not enabled in this reference);
- a synthetic mock core and data set so the repository runs without private data.

**This is a reference implementation, not production-ready.**

### How it differs from a typical memory server

A typical memory server focuses on storage, embedding, and recall quality. This project focuses on the **governance boundary** around an existing memory core:

- read-only by default;
- no credentials in repository configuration;
- explicit semantic statuses instead of an empty list;
- per-client identity binding and rollback;
- audit-friendly write-path design rather than automatic memory writes.

## 中文概要

这是一个位于 Agent 与记忆内核之间的**只读治理侧车**参考实现，不是记忆数据库。

包含：

- token 绑定的项目/身份隔离，不接受客户端伪造身份；
- 默认关闭的 MCP stdio 桥；
- 明确的空结果语义：`ok`、`no_match`、`service_down`、`low_relevance`、`no_direct_answer`；
- 观察模式：只标记“未直接回答”，不静默过滤；
- 人工审批的写入路径设计（本参考实现不开放写入）；
- 合成 mock 内核和示例数据，clone 后不需要私有数据即可演示和测试。

**参考实现，非生产就绪。**

## Quick start

The adapter talks to a small subset of the upstream **TencentDB-Agent-Memory v3** interface (`POST /v3/atomic/search`). This repository is an independent reference implementation, not a vendored upstream.

### Bash

```bash
python -m unittest discover -s tests -v

export MEMORY_CLIENT_TOKEN="demo-desktop-token"

python mock/mock_core.py
```

In a second terminal:

```bash
export MEMORY_CLIENT_TOKEN="demo-desktop-token"

python adapter/adapter.py --upstream http://127.0.0.1:18080 \
  --data-dir examples/data \
  --clients examples/clients.example.json \
  --policy examples/policy.example.json \
  --port 18081
```

Query:

```bash
curl -s http://127.0.0.1:18081/v1/recall \
  -H "content-type: application/json" \
  -H "x-client-token: ${MEMORY_CLIENT_TOKEN}" \
  -d '{"query":"What is the sample project codename?","limit":3}'
```

Run the MCP bridge (disabled by default):

```bash
export MEMORY_BRIDGE_ENABLED=1
export MEMORY_CLIENT_TOKEN="demo-desktop-token"
export MEMORY_ADAPTER_URL=http://127.0.0.1:18081
python bridge/memory_bridge.py
```

### Windows CMD

```bat
python -m unittest discover -s tests -v

set "MEMORY_CLIENT_TOKEN=demo-desktop-token"
python mock\mock_core.py
```

In a second terminal:

```bat
set "MEMORY_CLIENT_TOKEN=demo-desktop-token"
python adapter\adapter.py --upstream http://127.0.0.1:18080 ^
  --data-dir examples\data ^
  --clients examples\clients.example.json ^
  --policy examples\policy.example.json ^
  --port 18081
```

Query:

```bat
curl -s http://127.0.0.1:18081/v1/recall ^
  -H "content-type: application/json" ^
  -H "x-client-token: %MEMORY_CLIENT_TOKEN%" ^
  -d "{\"query\":\"What is the sample project codename?\",\"limit\":3}"
```

Run the MCP bridge (disabled by default):

```bat
set "MEMORY_BRIDGE_ENABLED=1"
set "MEMORY_CLIENT_TOKEN=demo-desktop-token"
set "MEMORY_ADAPTER_URL=http://127.0.0.1:18081"
python bridge\memory_bridge.py
```

With `MEMORY_BRIDGE_ENABLED` unset, the bridge returns `disabled` and makes no network request.

> The example client file stores only SHA-256 hashes of demo tokens. The values above are demonstration credentials, not production secrets.

## Layout

```text
adapter/      read-only identity-binding adapter
bridge/       MCP stdio bridge
docs/         architecture and write-path design
examples/     synthetic clients, policy, L0/L1 data
mock/         tiny mock memory core
rules/        generic agent recall rules
scripts/      wrapper and lifecycle templates
tests/        offline tests
```

## Security

- No tokens, keys, `.env`, real memory data, logs, or snapshots in this repository.
- Client credentials are read from environment variables at runtime.
- Do not enable write paths by default. See `CONTRIBUTING.md` and `SECURITY.md`.

## License

Apache-2.0.
