# Write Path Design (Reference)

This document describes a design only. The reference implementation does not expose write access.

## Who may write

- Agent clients: read-only; may submit drafts only.
- Controlled script: the only ingestion executor.
- Approval queue: accepts, rejects, and freezes a batch.
- Human owner: final approval, rollback, and block.

## Idempotency

- Candidate key: `project_id + content_hash + source_identity`.
- Same `content_hash` with a different source: do not create another L1 record; append the source to the existing audit entry and flag "possible duplicate".
- Re-running a batch returns `already_ingested` with no new records.

## Conflicts

- Current code/files win over stale memory.
- Never silently overwrite; mark the old record `superseded` with `superseded_by`.
- Unresolved conflicts go to `needs_review`.

## Approval flow

```text
draft -> preflight (duplicate/conflict) -> human approval
      -> freeze batch + snapshot -> controlled ingest
      -> extraction consistency check -> approve or rollback
```

## Extraction consistency

- One fact per extraction batch.
- Verify the number of L1 records equals the approved statements.
- Verify each L1 record is semantically consistent with its statement.
- If one item is inconsistent, roll back that item; if the batch is incomplete, roll back the batch.

## Audit and rollback

- Append-only audit: batch id, candidate id, counts, idempotency key, record id, source ids, result.
- Take a snapshot before ingestion.
- Rollback stops services, restores the snapshot, restarts, and rechecks counts and provenance.
- Superseded markers live in an adapter-side overlay table; the core is not mutated.

## Production gate

Not production-ready until read-only enforcement, idempotency, conflict handling, approval, audit, rollback, isolation, quality regression, and extraction consistency all pass.
