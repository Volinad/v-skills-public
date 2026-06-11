# Spec Compiler — Learnings

Patterns and insights collected from validation runs. Read by Auditor at start of each run.

This file starts empty and accumulates per installation: the Phase 7 learning-collector appends entries from your validation runs. Entries with MATERIALIZED status are archived after being implemented in holdout scenarios or antipatterns. Only active insights remain in this file.

## Statuses

| Status | Meaning |
|--------|---------|
| RESOLVED | Fixed by architectural decision, no holdout needed |
| NOTED | Recorded as operational insight, no code change needed |
| REJECTED | Considered and intentionally not implemented |
| MATERIALIZED | Implemented as holdout scenario or antipattern, moved to Archived section |

## Entry format

`**L-NNN** STATUS — one-paragraph insight: what happened, why it matters, what to check next time.`

Optional bullets: the concrete check to run; "Add to holdout: Yes/No — rationale".

---

### Architectural Decisions

(none yet)

### Operational Insights

(none yet)

---

## Archived

Entries materialized into holdout scenarios or antipatterns move here as one-line pointers, kept for historical reference.

(none yet)
