---
name: spec-compiler
description: "Universal documentation validation engine. Writer/Auditor separation, 18 methods in 5 groups, autonomous multi-pass loop with multi-model rotation. Works on any documentation set — specs, architecture, guides, configs. Run once, get polished docs."
---

# Spec Compiler

Universal documentation validation engine. Takes any set of documents, validates them through 18 methods, fixes issues autonomously, and stops when quality converges.

## How it works

Two agents — Writer (fixes) and Auditor (validates) — work in a loop. Auditor never sees Writer's process. Each validation group runs in fresh context. The loop continues until 2 consecutive clean rounds. Lead coordinates but never edits.

## Why Holdout

The holdout borrows ML's structure for a non-ML reason. Nothing here protects model parameters — an LLM Writer has none to overfit. What it protects is the validity of the measurement:

- The gate's "clean" verdict means "no issues found by probes the fixer could not target". Overfitting is optimization against a fixed metric, not a property of weights — an in-context LLM optimizes against published evaluation criteria the same way (Goodhart's law). If Writer sees the exact checks, detection greps, and trap catalog, a clean round only proves the published detectors pass.
- Knowing which checks run invites coverage gaming: effort flows to the probed paths and away from everything else.
- Probes are run by an agent whose only incentive is to find problems. Writer's incentive is to declare the fix done.

The split is **rules public, probes hidden**: writing conventions are given to Writer openly (see Writer conventions below) — hiding intent-level rules would only cause avoidable violations in fresh text. What stays Auditor-only is the probe set: which scenarios run, their detection procedures, and the accumulated trap catalog.

## Prerequisites

- Git repository initialized (for tracking changes)
- At least one document to validate

## Input

The compiler accepts **any documentation**. It auto-detects what's present and selects relevant methods.

Common document types (all optional):
- Specifications (PROJECT-SPEC, requirements, design docs)
- Feature definitions (JSON or Markdown)
- Architecture documents
- Agent/bot instructions (CLAUDE.md, agent profiles)
- Scripts (init.sh, CI/CD configs)
- API documentation
- Guides, runbooks, knowledge bases
- Configuration files with documentation

NOT included in validation loop:
- BUDGET.md — generated separately, stale numbers are non-blocking
- VALIDATION-REPORT.md — output of this skill, archived before each run

## 18 Validation Methods

Methods are organized in 5 groups. Each group runs in a fresh Auditor context. Lead auto-selects which methods apply based on documents present.

### Group 1 — Numbers & Cross-validation (methods 2, 3, 8, 14)

| # | Method | What it does |
|---|--------|-------------|
| 2 | Programmatic cross-validation | Every number verified against source of truth. Recount from primary data. |
| 3 | Consistency triangulation | Same value must be identical across ALL documents where mentioned. |
| 8 | Claim-by-claim verification | Every factual assertion checked — is it true and traceable? |
| 14 | Ground-truth graph | Build truth map from source files, cross-reference every doc claim against it. Check bidirectionality (if A references B, B must reference A). |

When to skip: Method 14 only applies when docs describe code structure (registries, API catalogs, dependency manifests).

### Group 2 — Consistency & Freshness (methods 12, 15, 16, 17)

| # | Method | What it does |
|---|--------|-------------|
| 12 | Contradiction detection | Find conflicting statements within and between documents. |
| 15 | Terminology consistency | Same concept must use same term everywhere. Detect synonyms used inconsistently ("agent"/"bot"/"worker", "endpoint"/"route"/"API"). |
| 16 | Temporal consistency | Dates, versions, timelines, sequences must not contradict each other or reality. |
| 17 | Staleness detection | Find references to files, paths, features, APIs that no longer exist. Dead links, old names, removed entities. |

When to skip: Methods 16-17 most valuable for mature projects with history. For fresh docs, focus on 12 and 15.

### Group 3 — Structure & Completeness (methods 7, 9, 11, 18)

| # | Method | What it does |
|---|--------|-------------|
| 7 | Completeness audit | What SHOULD exist but doesn't? Missing sections, undocumented entities, gaps in coverage. |
| 9 | Interface contract testing | Where documents reference each other — do the contracts match? (endpoints in features vs architecture, imports vs exports) |
| 11 | Mutation testing | If you change X in source — would documentation catch it? Tests doc resilience. |
| 18 | Scope boundary check | Document claims to cover X — does it actually? No more, no less. Detect scope creep and coverage gaps. |

When to skip: Method 9 only applies when multiple documents reference each other. Method 11 only for docs tied to source code.

### Group 4 — Execution & Traceability (methods 1, 5, 10, 13)

| # | Method | What it does |
|---|--------|-------------|
| 1 | Manual re-read | Read every document fully. Foundation for all other methods. Often catches what systematic methods miss. |
| 5 | Execution path tracing | Mentally execute every script/config line by line. Track cwd, env vars, processes. |
| 10 | Copy-paste testing | Every command/snippet from docs — would it actually work if pasted into terminal? |
| 13 | Implementation dry run | Pretend you're building from these docs. Try to implement 2-3 key items. Find what's unclear, missing, or contradictory. |

When to skip: Methods 5, 10 only apply when docs contain executable content (scripts, commands, configs). Method 13 only for implementation-oriented docs.

### Group 5 — Adversarial (methods 4, 6)

| # | Method | What it does |
|---|--------|-------------|
| 4 | Persona simulation | Test from 3+ perspectives: implementing agent, new team member, automated system. What breaks for each? |
| 6 | Adversarial / security audit | Find reasons to reject. Security holes, credential leaks, missing error handling, unprotected operations. |

When to skip: Method 6 most valuable for docs with scripts, configs, or credentials. Both methods apply to nearly all document sets.

## Severity Definitions

Every issue must be classified using these definitions. Auditor cannot reclassify an issue to a higher severity than what the definition warrants.

| Severity | Definition | Example |
|----------|-----------|---------|
| critical | Factual error that would break implementation or cause incorrect behavior | Count says 12 endpoints, actually 15; wrong API path |
| medium | Cross-document inconsistency, missing required coverage, broken reference | Endpoint in features but not in architecture |
| minor | Style, formatting, wording preferences | Non-blocking, does not extend fix loop |
| observation | Improvement suggestion, nice-to-have | Non-blocking, recorded in learnings only |

Only **critical** and **medium** issues are blocking. Minor issues and observations never extend the loop.

## Model Assignments

Validated across many validation runs:

- **Lead: Opus.** Sonnet Leads violate role boundaries — they run verification themselves instead of spawning a new Auditor round.
- **Writer: Sonnet.** Edits are fast; Lead verifies counts independently anyway.
- **Auditor: alternate Opus/Sonnet between rounds.** The models have complementary blind spots — in three separate runs Sonnet caught implementation-blocking issues that multiple Opus auditors missed (an OR/AND ambiguity, a lookahead-bias contradiction, an undefined label threshold). Neither model is strictly superior; rotation is what catches the residue.
- **Background agents (including the Phase 7 collector): Opus only.** Sonnet background agents have silently disappeared mid-task (no output file) in three confirmed runs.

## Lead Agent Rules

You are the Lead. You coordinate. You follow these rules without exception.

### Role boundaries
- You DO NOT edit, fix, or modify any project files. NEVER.
- You DO NOT parse JSON from agent task output files. NEVER.
- You DO NOT offer to make "small fixes" yourself.
- Only Writer edits files. Only Auditor validates.

### Autonomous flow
- After each agent completes, IMMEDIATELY proceed to next step.
- Do NOT wait for user input between rounds. The loop is autonomous.
- Only stop for user input at Phase 1 (confirmation to start) and Phase 6 (final report).
- Between groups: fix critical issues, then continue. No pause needed.

### Agent health check
- If any agent has not responded in 5 minutes — restart with a different model.
- Specifically for Sonnet: if no response in 5 minutes, log "Sonnet timeout, retrying with Opus" and restart the round with Opus.
- If Lead has no active tasks and no pending responses for 5 minutes — STOP.
- NEVER endlessly poll task output files. Max 3 status checks, then ask user.

### Communication
- Report results in plain text with tables. No raw JSON.
- Always show: issues count by severity, files affected, gate status.

### Document Language Rules
- Technical documentation (specs, features, architecture, API docs, configs) — write and fix in English without asking.
- Non-technical documents (concepts, plans, descriptions, narratives, READMEs) — preserve original language. When in doubt, ask the owner before translating.
- Never translate document content unless explicitly asked.
- Auditor reports and Writer summaries are always in English.

### Timestamp logging
Print at START and DONE of every major step:
```
=== Spec Compiler: [Step Name] START [YYYY-MM-DD HH:MM:SS] ===
=== Spec Compiler: [Step Name] DONE [YYYY-MM-DD HH:MM:SS] — [duration] — ~[N]k tokens (~$X.XX) — [summary] ===
```

### Token tracking

At workflow start, create `.token-log/spec-compiler-<timestamp>.jsonl`.

After each step completes (when you have `total_tokens` and `duration_ms` from
the step or task notification), append a JSONL entry:
`{"agent": "<step-name>", "model": "<model>", "total_tokens": N, "duration_ms": N, "timestamp": "<ISO>", "phase": "<phase>"}`

At workflow end (before `=== Spec Compiler: COMPLETE ===`), read the log and print
a token usage summary table with per-phase breakdown and estimated cost.
Blended rates (per 1K tokens): opus=$0.033, sonnet=$0.0066, haiku=$0.0006.

## Writer Agent Rules

Writer is the only agent that edits project files. These rules apply to every Writer instance.

- Writer ONLY edits files to fix issues reported by Auditor. No unsolicited improvements.
- Before fixing an issue, Writer locates the Auditor's quoted text in the target file. If the quote cannot be found (grep returns nothing), Writer does not guess — it reports the issue back as a suspected false positive (Antipattern #34).
- Writer DOES NOT validate or assess quality — that is Auditor's job.
- Writer DOES NOT read or modify holdout files (validation-scenarios.md, antipatterns-checklist.md). Holdout principle (see Why Holdout).
- Writer reports all changes as plain text summaries: what file, what changed, why.
- After adding or removing items that affect counts, Writer recounts and reports the new total. Lead verifies independently.
- Writer preserves document language according to Document Language Rules above.

### Writer conventions

These are rules of good documentation, not secrets — Writer is expected to know and apply them in every edit. Apply them to the text you touch; hunting for violations elsewhere is Auditor's job.

- Every "configurable" states its default; every schedule states its timezone.
- Acceptance criteria are testable — never "works correctly" / "works as expected".
- When editing a concept, update EVERY site that mentions it: summary tables, adjacent sections, cross-references. Fixes that skip this introduce new issues at the fix boundary.
- Do not introduce arithmetic or equivalence claims ("X equals Y", "derived from Z") without verifying the numbers from source.
- Multi-criteria conditions use explicit quantifiers ("if NONE of [A, B, C] exist"), never prose "or"/"and".
- When documenting ordering of equal-priority items, state the tie-breaker.
- No TODO/TBD stubs in documents declared complete.

What stays hidden from Writer is not these rules — it is the probe set Auditor runs against the result (see Why Holdout).

## Workflow

### Phase 1: Scan & Plan

1. Find all documents in scope (specified by user, or auto-detect from project root)
2. Classify each document by type (spec, architecture, guide, script, config, agent profile, other)
3. Count: files, sections, cross-references
4. **Select methods**: based on document types present, determine which of 18 methods apply
5. **Archive previous artifacts**: rename existing `VALIDATION-REPORT.md` to `VALIDATION-REPORT-prev.md`
6. Show user: document inventory, selected methods, estimated groups
7. **Token tracking**: create `.token-log/spec-compiler-<YYYYMMDD-HHmmss>.jsonl`
8. Ask confirmation to start
9. `git add -A && git commit -m "spec-compiler: pre-validation snapshot"`

### Phase 2: Validation Groups

Launch Writer and Auditor as separate agents.

For each group (1 through 5, skipping groups where no methods apply):

1. **Fresh Auditor context** — new Auditor instance for each group
2. Auditor runs assigned methods on all documents in scope
3. Auditor reports: issues with severity (critical / medium / minor / observation)
4. If critical issues found — Writer fixes them immediately before next group
5. Non-critical issues accumulate for Phase 3

For small document sets (a single doc or a few files), groups may run as parallel independent Auditor instances instead of sequentially — convergence of several groups on the same issue is a strong validity signal, while an issue found by only one group warrants scrutiny but can still be real. For large sets, keep groups sequential: context fills up and later methods get shallow treatment.

**Auditor input**: only final documents + holdout files + LEARNINGS:
   - `.claude/skills/spec-compiler/holdout/validation-scenarios.md` (or global `~/.claude/skills/spec-compiler/holdout/`)
   - `.claude/skills/spec-compiler/holdout/antipatterns-checklist.md`
   - `.claude/skills/spec-compiler/LEARNINGS.md`
**Auditor separation**: Auditor DOES NOT receive Writer's changes or reasoning. Holdout principle.

### Phase 3: Consolidated Review

After all groups complete:
1. Merge all issues from all groups (deduplicate)
2. Show consolidated table: method | issues | severity | files
3. Proceed to fix loop (no user confirmation needed)

### Phase 4: Fix & Re-validate (autonomous loop)

This loop runs without user intervention:

1. `git add -A && git commit -m "spec-compiler: pre-writer-round-N"`
2. Writer fixes all remaining issues (critical first, then medium)
3. **Lead sanity check** — programmatic verification before Auditor:
   - Count verification (do numbers in summaries match details?)
   - Cross-reference integrity (do all internal references resolve?)
   - If sanity check fails — Writer fixes immediately, skip Auditor
4. `git add -A && git commit -m "spec-compiler: post-writer-round-N"`
5. **Model rotation**: alternate Auditor model each round (Opus → Sonnet → Opus)
6. **NEW Auditor** (fresh context, fresh agent instance) re-validates:
   - Changed files + files referencing changed files
   - Re-run the method group(s) that originally found the issues being fixed. If unsure: number changes → Group 1, cross-doc inconsistencies → Group 2, structural gaps → Group 3, unclear instructions → Group 4
   - **Fix boundaries**: adjacent sections, tables, and cross-references that touch the same concept as each fix but were outside its scope. Writer fixes tend to introduce new issues exactly at these boundaries — a note added in one section while a table three sections away still describes the old behavior, or new text carrying an unverified mathematical claim (Antipattern #30).
   - Auditor input is the same as Phase 2: final documents + holdout files + LEARNINGS.md.
   - **Lead provides minimal context**: list of changed files, one-line fix summary, previous round issue count (number only). Do NOT pass full issue details from prior rounds.
7. Record: round number, issues found, issues fixed, model used

**Auditor integrity rules** — these instructions are given to every Auditor instance:
- Finding zero issues is a valid and valuable outcome. A clean document is the goal, not a failure of your review.
- Do NOT lower your severity threshold to avoid returning empty-handed. If the only issues you can find are word choices or style preferences — that means the document is clean. Report zero issues.
- Inflating severity (classifying style preferences as "medium") invalidates the round and wastes everyone's time. Use the severity definitions strictly.
- Self-assess honestly: for each method, was your check deep or shallow? If >50% shallow — the round is NOT clean.
- Every finding must quote the exact line text WITH its line number from the audited file. Before reporting, grep the quoted string in the file to confirm it exists. Under heavy ambient context (a large surrounding narrative that mentions related values) auditors have reported quotes that exist nowhere in the document — reconstructed from memory instead of read from disk (Antipattern #34). A finding whose quote cannot be grep-found is a false positive — discard it.

8. **Loop condition**: continue until **2 consecutive clean Auditor rounds on different models**
   - "Clean" = no critical or medium issues
   - The two clean rounds must come from different models — one model's evidence table is not self-trustworthy (Antipattern #34)
   - Minor issues and observations are non-blocking
   - All 18 applicable methods must have been covered across the full compilation
   - Safety limit: max 25 rounds. If not converging after 25 — stop, show convergence curve, ask user whether to continue or accept current state.

### Phase 5: Gate Decision

Gate PASS requires:
- 2 consecutive clean Auditor rounds on different models (required, not preferred — cross-model redundancy has repeatedly preserved verdict integrity where a single model misjudged)
- All applicable methods covered with evidence
- No critical or medium issues remaining
- Convergence confirmed (issues per round decreased)

Gate FAIL: report remaining issues, rounds completed, convergence trend. Ask user how to proceed.

### Phase 6: Report

Generate `VALIDATION-REPORT.md` in project root (or docs/ if it exists):
- Date, time, duration
- Documents validated (inventory)
- Methods applied (with rationale for skipped methods)
- Evidence summary per method
- Issues found and fixed (all rounds, with round number)
- Model rotation log (which model found what)
- Gate status + confidence level
- `git add -A && git commit -m "spec-compiler: validation complete — GATE [PASS/FAIL]"`

Show user the final summary. List non-blocking observations if any.

### Phase 7: Learn

This phase captures methodology improvements. It runs as a **lightweight collector agent** with fresh context — not as an extension of the exhausted main session.

**A learning exists to change what a future run does — that is the entire bar.** On a mature skill most runs produce zero new learnings, and that is the healthy, expected outcome, not a failure. Recording an instance of something the skill already handles changes no future behavior; it only grows a file every later run must read in full. The collector is held to the same integrity rule as the Auditor (Phase 4): finding nothing new is valid and valuable, and padding the file to "show work" is the same failure as an Auditor inflating severity to avoid an empty report.

1. Lead spawns a **learning-collector agent** (background, fresh context, Opus — Sonnet background agents have vanished mid-task).
2. Collector reads `VALIDATION-REPORT.md`, current `LEARNINGS.md`, and the holdout files — to see what the skill already does, so it does not re-record it.
3. **Two-question test — apply to every candidate before writing it.** Write an L-entry only if BOTH hold:
   - **Novel** — absent from SKILL.md, the holdout files, and existing entries. A fresh instance of an existing scenario/antipattern/gate is NOT novel.
   - **Actionable** — it changes a future run: a new check, a method weighting, or a document-class posture. If you cannot state the novelty in one sentence, it is not worth keeping.
4. **A reconfirmation is not a learning.** When a run re-demonstrates a pattern already in the gate/holdout/SKILL — model rotation catching a residual, a fix-boundary miss, M13-by-execution paying off — that goes in THIS run's VALIDATION-REPORT, never as a new entry and never as a dated tail on the existing one. Keep no "Nth confirmation" counters and no confirmation ledger: the gate is already materialized, so its evidence does not accumulate here.
5. **Each kept entry is its reusable core** — the pattern plus the check it implies, in a few sentences, naming at most the ONE closest entry it refines. The audience is a future Auditor who needs the check; the run's specifics (which round, which model, which file) belong in the VALIDATION-REPORT, not here.
6. **Promote or annotate.** A genuinely new pattern seen 2+ times across entries → materialize it as a holdout scenario/antipattern. A specialization of an existing one → annotate that one, don't add a standalone entry. A learning that implies changing this skill's own instructions (method selection, model assignments, phases, gate rules) → flag it in the final summary as "SKILL.md update suggested: …"; the collector never edits SKILL.md (skill edits go through skill-creator).
7. **Archive what is already implemented.** Once an entry's substance lives anywhere a future run reads it — a holdout scenario/antipattern OR SKILL.md / phase logic / the gate — collapse it to a one-line pointer in the Archived index. The test is "is it implemented where a run will encounter it?", not the NOTED/MATERIALIZED label — this is what stops load-bearing-but-already-baked entries (like the model-rotation gate) from growing confirmation tails.
8. `git add -A && git commit -m "spec-compiler: update learnings"`
9. **Token cost summary**: include estimated cost in the final summary line.
   Calculate: total_tokens × blended_rate (opus=$0.033/1K, sonnet=$0.0066/1K, haiku=$0.0006/1K).
   Example: "~168k tokens (~$5.54), ~2 minutes". The cost goes in every DONE status line too.
10. Print: `=== Spec Compiler: COMPLETE ===`

After this message: do NOT start new tasks. Compilation is done.

## Method Selection Guide

Not all 18 methods apply to every document set. Lead selects based on content:

| Document type | Always apply | Likely apply | Rarely apply |
|---------------|-------------|-------------|-------------|
| Spec / requirements | 1, 7, 8, 12, 15, 18 | 4, 6, 9, 13, 16, 17 | 2, 3, 5, 10, 11, 14 |
| Feature definitions (JSON) | 1, 2, 3, 7, 8, 9, 12 | 11, 13, 14, 16, 17, 18 | 4, 5, 6, 10, 15 |
| Architecture | 1, 7, 8, 9, 12, 15, 18 | 3, 4, 6, 11, 13, 14, 16, 17 | 2, 5, 10 |
| Agent instructions | 1, 7, 12, 15, 17, 18 | 4, 6, 8, 9 | 2, 3, 5, 10, 11, 13, 14, 16 |
| Scripts / CI configs | 1, 3, 5, 6, 10 | 2, 4, 7, 8, 12, 13, 17 | 9, 11, 14, 15, 16, 18 |
| API documentation | 1, 2, 3, 7, 9, 14 | 6, 8, 10, 12, 13, 17, 18 | 4, 5, 11, 15, 16 |
| Guides / knowledge bases | 1, 7, 8, 15, 16, 17 | 4, 12, 13, 18 | 2, 3, 5, 6, 9, 10, 11, 14 |
| Skill specification (SKILL.md) | 1, 4, 7, 8, 12 | 15, 17, 18 | 2, 3, 5, 6, 9, 10, 11, 13, 14, 16 |
| ML/quant algorithm spec | 1, 7, 8, 12, 13 | 2, 15, 16, 18 | 3, 4, 5, 6, 9, 10, 11, 14, 17 |
| Mixed / full project | ALL | — | — |

Type-specific notes from validation runs:
- **Skill specifications**: completeness audit (7) against a mature reference skill spec is the highest-value method — structural comparison caught 8 issues in one pass.
- **ML/quant specs**: implementation dry run (13) finds the implementation-blocking criticals; adversarial methods find near zero. Schedule at least one Sonnet round running method 13 — that combination caught criticals all Opus rounds missed.
- **Single-document sets**: broken cross-references and missing dependencies largely disappear; internal number mismatches, in-document terminology drift, and dry-run-visible gaps dominate. Shift weight from cross-reference methods (3, 5, 9) to internal consistency (7, 12, 13).
- **Paired/bilingual sets**: the higher-precision variant carries the factual risk — weight its claim-by-claim (8) and ground-truth (14) audit harder; use the vaguer sibling as a wording reference, never force precision into it (Scenario 20).

When in doubt, include the method. False positives (method finds nothing) are cheap. False negatives (skip method, miss issue) are expensive.

## Evidence Protocol

For EACH method run, Auditor produces structured evidence:

```json
{
  "method_id": 14,
  "method_name": "Ground-truth graph",
  "depth": "deep",
  "what_checked": ["registry.json vs actual exports", "bidirectional references"],
  "what_not_checked": ["internal component dependencies"],
  "files_examined": ["src/registry.json:1-200", "src/index.ts:1-50"],
  "issues_found": [],
  "confidence": "high",
  "clean": true
}
```

Plus a human-readable summary. Lead never parses raw JSON — Auditor provides text summaries.

## Self-audit Rule

After completing all assigned methods, Auditor honestly assesses:
- For each method: was it deep or shallow?
- If >50% shallow — round is NOT clean, needs re-run
- "Clean pass" with shallow checks = false confidence

## Skill Files

- `LEARNINGS.md` — starts empty in a fresh installation; the Phase 7 collector appends an insight only when a run surfaces something genuinely new, and every Auditor instance reads it. Holds un-promoted, still-actionable insights plus a one-line Archived index of patterns already baked into SKILL/holdout. It is NOT a run log — reconfirmations and per-run narratives live in each run's VALIDATION-REPORT.
- `holdout/validation-scenarios.md`, `holdout/antipatterns-checklist.md` — Auditor-only checks. Writer must never read them (holdout principle).
