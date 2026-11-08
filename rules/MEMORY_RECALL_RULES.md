# Memory Recall Rules (Reference)

This is a generic version of the rules used by the reference clients. It contains no private project names, paths, or credentials.

## When to recall

Recall only when:

- the question is about project facts: architecture, workflow, constraints, owner, status;
- the user refers to a previous decision or says "as agreed before";
- a planned change may conflict with an existing constraint.

Do not recall for:

- casual conversation, general technical questions, or pure code edits;
- information already present in the current conversation.

## Budget

- At most one recall per turn; two only when necessary.
- `limit` must not exceed 5.
- Do not rephrase the same query repeatedly.

## Result handling

- First decide whether the returned record **directly answers** the question.
- `ok` and `low_relevance=false`: may cite, with `record_id` or source.
- `low_relevance=true`, `no_match`, or `no_direct_answer`: say "there is no such memory"; do not substitute adjacent content.
- `service_down`: say the memory service is unavailable and continue without memory.
- If memory and current files disagree, current files win; state the disagreement.

## Read-only boundary

- Clients are read-only.
- Never claim "I remembered this."
- Writes only through a controlled, human-approved script; not part of this reference implementation.
