# Implementation Auditor — Learnings

A learning here exists to change what a FUTURE audit does. This file holds only patterns that are **novel** (not already in the holdout procedures) and **actionable** (a concrete check). Read by the Auditor at the start of a run.

This file starts EMPTY in a fresh installation and accumulates per-installation (see Phase 5 in SKILL.md for the bar). Most runs of a mature skill add nothing — that is the healthy outcome. This skill promotes a pattern only after 3 occurrences across different projects, so an un-promoted entry may log a 2nd/3rd sighting as ONE terse line; once promoted, it moves to Archived and further sightings go in the run's IMPL-AUDIT-REPORT, not here. This file is a live watch list, not a run log.

## Statuses

| Status | Meaning |
|--------|---------|
| NOTED | Active insight, not yet promoted — kept until a 3rd cross-project occurrence promotes it |
| MATERIALIZED | Implemented as a holdout procedure / FP-guard — moved to Archived |
| RESOLVED | Implemented in SKILL.md / phase logic — moved to Archived |
| REJECTED | Considered and intentionally not implemented |

## What belongs here (the bar for a new entry)

Apply two tests before writing an entry — write it only if BOTH pass:
- **Novel** — absent from the holdout procedures, the known-false-positive guards, and existing entries.
- **Actionable** — it changes a future audit (a new check, severity-calibration rule, or project-type posture), statable in one sentence.

Keep each entry to its reusable core; counting a 2nd/3rd sighting toward the 3+ promotion bar is one terse line, never a paragraph. No confirmation ledger for an already-materialized procedure.

---

## Active insights (un-promoted — promote to holdout on recurrence)

*(none yet)*

---

## Archived

Entries whose substance now lives in the holdout file or SKILL.md collapse to one-line pointers here, for provenance.

*(none yet)*
