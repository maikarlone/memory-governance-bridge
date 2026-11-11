# Governance Boundaries and Known Limits

Status: generic SOP and known limits. This note does not enable writes and does not change the read-only reference implementation.

Scope: engineering long-memory co-governance after the SOP is fixed. Day-to-day terminal iteration is outside this mode. Keep local iteration notes out of the repository.

## 1. Co-governance boundary

- Use this mode only in an engineering long-memory environment whose SOP is already fixed.
- Approve each write at the time of the write.
- Keep `update` off by default.
- Allow a later targeted correction only for the same fact.
- When different facts are merged by mistake, leave `update` off and do not force a write.
- Onboard a new environment one statement at a time.
- When a stored fact is missed because of the question wording, change the question only. Do not ingest it again.

## 2. Retest and execution constraints

- With no file changes, the runner may return `REWORK` / `no_changed_files`.
- Do not stop a run on a fixed short timeout.
- Count SQLite rows already stored in the library. Do not substitute a proxy such as `message_level`.

## 3. Known limits

- The kernel may merge different facts by mistake.
- A row that appears in retrieval diagnostics is not a hit.
- An access endpoint may skip recall and read a local file instead.
- Untracked files fail the execution preflight.
- Record `TECH_FAIL` as a technical interruption. It is not a failed goal.

## 4. Open-source exclusions

Repository documents exclude secrets, memory body text, snapshots, logs, real paths, usernames, library ids, and concrete business or project details. Leave local iteration notes and the original text of local instructions outside the repository. Published docs keep only this generic SOP and these known limits.

---

# 共治边界与已知限制

状态：通用 SOP 与已知限制。本文不开放写入，也不改变本参考实现的只读默认。

适用范围：SOP 已经固定的工程化长记忆共治环境。日常终端上的持续迭代不在此共治模式内。本地迭代说明留在仓库外。

## 1. 共治适用边界

- 只用于 SOP 固定之后的工程化长记忆环境。
- 写入需当场批准。
- `update` 默认关闭。
- 同一事实才允许以后做定向更正。
- 不同事实被误判合并时，保持 `update` 关闭，不做硬写。
- 新环境按一条一写纳入。
- 已在库但问法不命中时，只改问，不重注。

## 2. 复测与执行约束

- 无文件变更时，runner 可能返回 `REWORK` / `no_changed_files`。
- 不以固定短超时切断。
- 计数中的 SQLite 只使用库内记录数，不用 `message_level` 一类代理值代替。

## 3. 已知限制

- 内核可能把不同事实误判合并。
- 检索诊断里出现某条，不等于命中。
- 某个接入端可能跳过召回，改用本地文件。
- 未跟踪文件会导致执行预检失败。
- `TECH_FAIL` 只记作技术中断，不记作目标失败。

## 4. 开源排除

密钥、记忆正文、快照、日志、真实路径、用户名、库 id，以及具体业务与项目细节，不写入仓库文档。本地迭代材料及其说明原文留在仓库外。文档只保留上述通用 SOP 与已知限制。
