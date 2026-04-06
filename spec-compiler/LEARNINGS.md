# Spec Compiler — Learnings

Patterns and insights collected from validation runs. Read by Auditor at start of each run.

Entries with MATERIALIZED status are archived after being implemented in holdout scenarios or antipatterns. Only active insights remain in this file.

## Statuses

| Status | Meaning |
|--------|---------|
| RESOLVED | Fixed by architectural decision, no holdout needed |
| NOTED | Recorded as operational insight, no code change needed |
| REJECTED | Considered and intentionally not implemented |
| MATERIALIZED | Implemented as holdout scenario or antipattern, moved to Archived section |

---

### Architectural Decisions

**L-002** RESOLVED — BUDGET numbers go stale immediately when features change. Including BUDGET in validation loop creates infinite recalculation cycles.
- Fix: BUDGET excluded from validation loop. Updated once after Gate PASS, not during validation.

**L-003** RESOLVED — Lead agent gets stuck parsing JSON from task output files. Spends hours in loop trying python3/jq extraction.
- Fix: Writer and Auditor produce plain text summaries. Lead role: "Never parses task output files."

**L-008** RESOLVED — Auditor read old VALIDATION-REPORT.md from previous session which said "GATE PASS". This biased Auditor's assessment.
- Fix: Phase 1 archives previous validation artifacts (rename to VALIDATION-REPORT-prev.md).

**L-019** RESOLVED — LEARNINGS accumulated actionable items but nobody checked if they were actually executed. Items recorded but not added to holdout until fresh-eyes audit caught it days later.
- Fix: LEARNINGS uses ticket-style statuses. After recording "Add to holdout: Yes", execute immediately — don't defer.
- v3 update: Learning Collector agent now auto-promotes repeated patterns to holdout scenarios.

**L-020** RESOLVED — Type A/B/C (change types) and Level A/B/C (change depth) used same letter designators for different concepts in different skills, causing confusion.
- Fix: Use distinct naming per skill. Avoid reusing letter designators across different taxonomies.

### Operational Insights

**L-009** NOTED — Lead on Sonnet violated role boundary — ran verification scripts himself instead of launching new Auditor round. Opus Lead was more disciplined about role separation.
- Recommendation: Lead should be Opus for better rule adherence.

**L-010** NOTED — Sonnet background agent disappeared during validation (output file never created). Required manual restart.
- Confirmed multiple times across projects. Pattern: Sonnet as background subagent can be unreliable.
- v3 update: 5-minute timeout with automatic retry on Opus added to Phase 4.

**L-012** NOTED — Optimal model configuration: Lead=Opus, Writer=Sonnet (fast edits), Auditor=alternate Opus/Sonnet.

**L-018** NOTED — Sonnet background agent disappeared again (third confirmed occurrence). Pattern consistent: Sonnet as background subagent is unreliable for critical tasks.
- Mitigation: don't rely on Sonnet for critical background tasks. Use Opus for background, Sonnet for foreground.

**L-022** NOTED — Context provider completeness gap in component registries. Context providers (React.createContext wrappers) consistently missed because they don't appear in component directories.
- When auditing component registries: always cross-check with index.ts exports, not just component directories.
- Check: context providers, config exports, composite hooks that wrap multiple components.

**L-023** NOTED — Sequential multi-round verification reduces false confidence. Each round with progressively more systematic methods finds new issues that previous rounds missed. "One clean pass" is not sufficient for structural documentation.
- Applied: 2 consecutive clean rounds gate in Phase 4.

**L-029** NOTED — RAM/memory estimates in specs are fragile when they assume a specific data type size. A spec assumed a smaller type but the implementation used a larger one, doubling the actual memory footprint. The wrong estimate propagated across multiple documents unchallenged until Method 2 (programmatic cross-validation) independently computed from the actual implementation.
- Always verify RAM estimates by computing from the actual data type definition, not trusting prose numbers.
- Add to holdout: Yes — Scenario: "RAM/memory estimates must be derived from dtype or struct size, not assumed."

**L-030** NOTED — Thread safety in specs that propose concurrent access to shared data structures. A spec claimed "no race condition" for shared data access across threads based on key partitioning. Multiple auditors independently flagged this: CPython GIL atomicity is an implementation detail, not a language guarantee. Free-threaded Python 3.13+ would break it.
- When specs propose threading: always require explicit synchronization (Lock, Queue, or separate data structures), never rely on GIL.

**L-031** NOTED — Event ordering specs must account for insertion order when priorities are equal. A spec documented a specific ordering, but both event types had equal priority. The actual code inserted them in reverse order, so the tie-breaking mechanism reversed the documented order. Caught by Method 13 (implementation dry run) and Method 4 (persona: code reviewer).
- When specs document ordering of equal-priority items: explicitly state the tie-breaking mechanism and verify against code insertion order.

**L-032** NOTED — "Same as X" identity claims are a distinct antipattern from "similar to X". Draft spec said "Same as spec-compiler" for evidence protocol and "same learning-collector pattern as spec-compiler" for Phase 5. Both were false — the actual structures diverged. "Similar to" is vague; "same as" is a falsifiable claim that is often wrong. Caught by claim-by-claim verification (M8).
- Antipattern #2 extended to cover identity claims ("Same as X") in addition to similarity claims.
- Add to holdout: No — extending existing Antipattern #2 is sufficient.

**L-033** NOTED — Logical operators (OR/AND/NONE) in natural language skip conditions are ambiguous and error-prone. Phase 2a skip condition said "if no ADRs, security requirements, OR coding conventions" — intent was "if NONE of these exist" (AND logic), but OR means "if any one is missing, skip". Sonnet (Round 1 re-validation) caught this; all 5 initial Opus auditors missed it.
- Skip conditions with multiple criteria must use explicit logic: "if NONE of [A, B, C] exist" or "if ALL of [A, B, C] are absent". Never rely on OR/AND in prose.
- Add to holdout: Yes — new Antipattern #29.

**L-034** NOTED — Skill specifications are a distinct document type requiring specific method selection. Of 18 methods, only 9 applied (no code, no cross-doc numbers, no scripts, no executable paths). Completeness audit (M7) was the highest-value method — using an existing skill spec (spec-compiler SKILL.md) as structural template caught 8 medium issues in one pass.
- For skill spec validation: prioritize M7 (completeness audit against reference spec), M8 (claim-by-claim), M4 (persona simulation), M12 (contradiction detection).
- Add to holdout: No — operational insight, not a recurring trap.

**L-035** NOTED — Parallel initial audit with 5 groups confirms issue validity through independent convergence. Issues found by 3+ groups independently (e.g., "no Lead Agent Rules" found by G3, G4, G5) have high confidence. Issues found by only 1 group (e.g., "evidence protocol divergence" found only by G1) require closer scrutiny but may still be valid — G1's unique find was confirmed as real.
- Parallel audit is effective for small single-document validations. Convergence count is a useful confidence signal but not a filter — unique findings can be valid.
- Add to holdout: No — operational insight.

**L-036** NOTED — Sonnet found the OR/AND skip condition bug that all 5 Opus auditors missed. This is the second confirmed case of model rotation catching issues (first: L-012 noted Opus is better for role discipline, now Sonnet is better for logical precision in natural language). Model rotation is not just theoretical — it produces measurable catches.
- Reinforces L-012: alternate Opus/Sonnet for Auditor rounds. Neither model is strictly superior — they have complementary blind spots.
- Add to holdout: No — reinforces existing operational insight.

---

## Archived

Entries below have been materialized into holdout scenarios or antipatterns and are kept for historical reference only.

L-001 (Writer miscounts) → Holdout Scenario 1, Antipattern #20. L-004 (depends_on scan) → Holdout Scenario 12. L-005 (generated config secrets) → Holdout Scenario 2. L-006 (conditional guards) → Holdout Scenario 4. L-007 (circular/cross-phase deps) → Holdout Scenario 13, Antipattern #22. L-011 (sequential validation) → Phase 2 group structure. L-013 (clean workspace) → Phase 1 step 5. L-014 (count verification) → Phase 4 step 3. L-015 (change level classification) → Removed from spec-compiler (out of scope). L-016 (UX findings) → Out of scope. L-017 (references edge type) → Architecture docs. L-021 (ground-truth graph) → Method 14, Holdout Scenario 14. L-024-L-028 (v2 upgrade) → Spec Compiler v2 structure.
