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

**L-049** RESOLVED — External design review (2026-06) challenged the Writer/Auditor holdout as "cargo-cult ML": an LLM Writer has no parameters to overfit, so hiding rules from it only causes avoidable violations and extra rounds. The review was half right.
- Accepted: intent-level writing conventions must be PUBLIC to Writer — hiding "every schedule needs a timezone" has cost and no benefit; fix-boundary contamination (L-038) was partly caused by Writer not knowing basic conventions. Writer conventions digest added to SKILL.md.
- Rejected: publishing the probe set (scenario list, detection procedures, trap catalog). Overfitting is optimization against a fixed metric, not a property of weights — an in-context LLM optimizes against published evaluation criteria the same way (Goodhart). A "clean" gate verdict is evidence of general quality only if the fixer could not target the probes; publishing them also invites coverage gaming.
- Rejected: "fixed scenarios are memorizable" — scenarios are parameterized procedures (recount from source of truth, rebuild dependency graph) that regenerate ground truth against current docs each run, not fixed Q&A pairs. Secrecy prevents coverage gaming, not answer memorization.
- Codified as "rules public, probes hidden": SKILL.md "Why Holdout" section + "Writer conventions" digest; holdout Principle section updated to state the Goodhart rationale explicitly.

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
- Update: Generalized to L-040 — any claimed arithmetic equality, not just RAM. Promoted to Antipattern #31.

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
- Update: Third confirmation in L-037. Pattern now has 3 data points.

**L-037** NOTED — Sonnet found both critical issues in an ML classification spec via M13 (implementation dry run) that Opus missed across G1-G3 and G5. Criticals: (a) a lag contradiction — a feature documented as causal would introduce lookahead bias as implemented, (b) ambiguous label threshold — the boundary between "unlabeled" and the defined classes was undefined. Third confirmed case of Sonnet catching implementation-blocking issues Opus misses (after L-036 OR/AND bug, L-012 role discipline inverse).
- M13 + Sonnet is the highest-value combination for finding implementation-blocking issues in ML/quant specs.
- Add to holdout: No — operational insight, extending L-012/L-036 model rotation pattern.

**L-038** NOTED — Writer Round 1 fixes introduced 2 new medium issues. Pattern: (a) a clarifying note added to fix missing information contained an incorrect mathematical equivalence claim (two formulations stated as equivalent are NOT equivalent for the downstream calibration step), (b) a new section was added but a summary table covering the same topic was not updated, creating cross-reference inconsistency. This is a distinct failure mode: Writer fixes create new issues at the boundaries of the fix.
- After each Writer round, Auditor should specifically check the BOUNDARIES of each fix — adjacent sections, tables, and cross-references that touch the same concept but were not in the fix scope.
- Add to holdout: Yes — new Antipattern #30 (Writer fix boundary contamination).

**L-039** NOTED — For standalone ML/quant specs, method value ranking differs from general documentation. M13 (implementation dry run) found both criticals. M7 (completeness) found 3 mediums. Adversarial methods (M4 persona, M6 edge case) found zero blocking issues. M2/M3 (numbers, cross-validation) confirmed issues but did not discover them first. This suggests: for single-document specs with heavy algorithmic content, prioritize M13 > M7 > M12 > M8 over adversarial methods.
- Method selection should be document-type-aware. ML/quant specs benefit most from implementation dry runs and completeness audits, not adversarial personas.
- Add to holdout: No — operational insight for method selection.

**L-040** NOTED — Claimed arithmetic equalities in specs are a recurring trap. An ML spec claimed a gap parameter "equals the maximum normalization lookback" but the numbers were 20 vs 30 days. Previously (L-029): a RAM estimate assumed a smaller data type than the implementation actually used. Pattern: when a spec states "X equals Y" or "X is derived from Y" with specific numbers, verify the arithmetic independently. Prose claims of equality between computed values are often stale or wrong.
- Second occurrence of this pattern (L-029 + L-040). Promoting to Antipattern #31.
- Add to holdout: Yes — new Antipattern #31 (claimed arithmetic equality without verification).

**L-041** NOTED — Single-document specs have a different issue profile than multi-document sets. Zero broken file references or missing dependencies (the most common issues in multi-doc validation). Instead: internal number mismatches, terminology used inconsistently within the same doc, and implementation gaps only visible through dry run. Implication: for single-doc validation, reduce weight on cross-reference methods (M3, M5) and increase weight on internal consistency (M12, M13, M7).
- Add to holdout: No — operational insight for method selection, complementary to L-039.

**L-042** NOTED — Informal/colloquial names for formal concepts create subtle inconsistencies. A spec used informal shorthand names in a summary table, conflicting with both the formal class taxonomy (which defined specific labels) and a separate boolean flag concept that shared one of the informal names. Sonnet R2 caught this; Opus R1 missed it.
- This is a specialization of Antipattern #24 (terminology drift). When a spec defines a formal taxonomy, any informal shorthand for those classes is a potential inconsistency source.
- Add to holdout: No — covered by existing Antipattern #24 and Scenario 15.

**L-043** MATERIALIZED — "Aligned with `<named source>`" attribution claims are often FALSE; verify by reading the named source DIRECTLY. A doc claimed alignment with a named function, quoting a specific boundary value — but that function's actual boundary differed; the quoted value belonged to a different, similarly-scoped function. The false claim was also mirrored in code comments. Found only by opening the cited source directly. → Materialized as Scenario 19 + Antipattern #32 (see Archived index).

**L-044** NOTED — A discriminated-union / enum type block reproduced in a doc can OMIT a member that the doc's own decision matrix and prose actively use. A doc reproduced a strategy union listing 5 arms but omitted the 6th (the source type has 6; the doc's matrix and prose referenced it). Caught by THREE methods CONVERGING: M9 (interface contract — count the arms), M12 (contradiction — matrix uses an arm the type block lacks), M14 (ground-truth graph — source has 6, doc has 5). This is different from Scenario 7 (status enum drift, which collects values doc-vs-doc) and Scenario 14 (endpoint/component counts): the trap is *internal* — the doc contradicts ITSELF (block vs. matrix/prose) and the source simultaneously.
- Check: when a doc reproduces a union/enum/sum type, count its members against (a) the source type definition and (b) every place the doc's own prose/matrix/table references members. A member used downstream but absent from the reproduced block is a CRITICAL omission.
- Three-method convergence on a CRITICAL, repeatable check → Antipattern #33. Add to holdout: extending Antipattern #33 is sufficient (no standalone scenario yet — re-promote to a full scenario on 2nd occurrence).

**L-045** NOTED — A doc that self-labels as "the contract" but documents only the OUTPUT leaf type, omitting the INPUT and POLICY type blocks, is an incomplete contract. A doc called itself "the contract" yet documented only the output type, omitting the input and policy types; it also named a config knob absent from the source type and stated no policy defaults ("configurable without default" — Antipattern #1). A contract is the full input→policy→output surface; documenting one leaf and claiming completeness is a scope/coverage failure tied to the doc's OWN self-description.
- Check: when a doc claims to be "the contract" / "the API" / "the schema", enumerate the full type surface from source (inputs, policy/config, outputs) and confirm each block is present with stated defaults. A named knob must exist in the source type; every policy field needs a default.
- First occurrence; specialization of Scenario 18 (scope creep & coverage gaps) + Antipattern #27 (scope declaration vs. content), with the self-description trigger being "the contract". Add to holdout: No — covered by Scenario 18 / Antipattern #27 + #1; revisit for a dedicated scenario if it recurs.

**L-046** MATERIALIZED — Auditor fabricates/misquotes document text under heavy ambient context: a consistency-lens auditor flagged or quoted strings that do NOT exist in the audited file, reconstructed from the host project's large ambient narrative (a large cumulative agent-instructions file that mentions those values) instead of read from disk. One run: Sonnet's first-round consistency group produced 3 false positives of this shape (a line-count claim absent from both docs; a present-verbatim qualifier claimed "missing"; an attribution qualifier not present); the same run's clean round had evidence-table transcription slips (a path written from memory while verified values matched the real one). Distinct from L-043/#32 (value real, wrong source) and L-038/#30 (Writer-side contamination). Cross-model redundancy (independent Opus rounds) preserved verdict integrity — direct support for the 2-clean-different-models gate (L-023). → Materialized as Antipattern #34 (mitigation: quote exact line+number; grep-verify the quoted string exists before acting). See Archived index.

**L-047** NOTED — State-snapshot / status documents inherit dates from the session narrative the author was reading, and the narrative date can be wrong. A snapshot doc (self-certifying git/filesystem verification) dated a release at 3 sites two days earlier than the release commit's actual timestamp. The author copied the narrative's date into a doc that claims to verify against VCS. Ground truth for a date in a self-certifying snapshot is the VCS history (commit timestamp / tag), NOT prose narrative — even the doc's own cumulative narrative.
- Check: for every date/version-release claim in a snapshot or status doc, verify against `git log`/tag timestamps, not against the narrative. Treat narrative-sourced dates as suspect and mark them explicitly (e.g. "(per narrative)"); precise release dates especially must be git-sourced.
- Specialization of Scenario 17 (temporal consistency) with a new ground-truth source (VCS). Add to holdout: No — annotated Scenario 17 + Antipattern #26 to add the VCS-as-ground-truth dimension; revisit for a dedicated scenario if narrative-date inheritance recurs.

**L-048** NOTED — Bilingual / paired documents covering the SAME state with asymmetric precision: the more precise variant carries the higher factual risk and deserves the harder audit; the vaguer variant rarely carries precise-fact errors and can serve as the accurate-wording reference. First bilingual-pair run for this skill: the precise snapshot carried a wrong exact release date while the plain-language overview stated it vaguely ("early May") and was therefore correct; the vague variant's wording was also already accurate at another disputed site and served as the reference for the fix. Vagueness is a shield against precise-fact error, not a defect to "fix" by forcing precision into the vague variant.
- Check: when a document set is a paired/bilingual representation of one state, identify the higher-precision variant and weight its claim-by-claim/ground-truth audit harder; cross-check the precise variant's exact facts against both ground truth AND the vaguer sibling; do NOT down-rank the precise doc's risk because the pair "mostly agrees." Use the vaguer variant as a wording reference where the precise one is wrong, not the other way around.
- First occurrence; distinct document-set class (paired/bilingual). Add to holdout: Yes — new Scenario 20 (paired/bilingual document precision asymmetry).

---

## Archived

Entries below have been materialized into holdout scenarios or antipatterns and are kept for historical reference only.

L-001 (Writer miscounts) → Holdout Scenario 1, Antipattern #20. L-004 (depends_on scan) → Holdout Scenario 12. L-005 (generated config secrets) → Holdout Scenario 2. L-006 (conditional guards) → Holdout Scenario 4. L-007 (circular/cross-phase deps) → Holdout Scenario 13, Antipattern #22. L-011 (sequential validation) → Phase 2 group structure. L-013 (clean workspace) → Phase 1 step 5. L-014 (count verification) → Phase 4 step 3. L-015 (change level classification) → Removed from spec-compiler (out of scope). L-016 (UX findings) → Out of scope. L-017 (references edge type) → Architecture docs. L-021 (ground-truth graph) → Method 14, Holdout Scenario 14. L-024-L-028 (v2 upgrade) → Spec Compiler v2 structure. L-043 (source attribution diverges) → Holdout Scenario 19, Antipattern #32. L-046 (auditor fabricates doc text under ambient context) → Antipattern #34.
