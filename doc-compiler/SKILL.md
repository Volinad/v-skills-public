---
name: doc-compiler
description: "Document quality engine for non-technical writing — plans, ideas, proposals, reports, narratives. 14 validation methods, Writer/Auditor separation, interactive setup for edit permissions and autonomy level. Works on any human-facing document set. Use this skill when the user wants to review, polish, or validate non-technical documents, or asks to check a document for consistency, clarity, or completeness."
---

# Doc Compiler

Document quality engine for non-technical writing. Takes plans, ideas, proposals, reports, narratives — any document written for human readers — and validates them for consistency, clarity, completeness, and logical coherence.

## How it works

Same core architecture as Spec Compiler: Writer (fixes) and Auditor (validates) work in a loop with fresh context per round. The key difference is an interactive **Setup Phase** where the owner defines edit permissions and autonomy level before the loop begins. Doc Compiler respects the author's voice — it fixes problems without rewriting style.

## Prerequisites

- At least one document to validate
- Git repository recommended (for tracking changes) but not required

## Input

The compiler works with **any non-technical document**:
- Plans, roadmaps, project proposals
- Ideas, concepts, research notes
- Reports, summaries, post-mortems
- Narratives, guides, handbooks
- Meeting notes, decision logs
- Blog posts, articles, presentations
- Mixed document sets (some editable, some read-only)

## 14 Validation Methods

Methods are organized in 4 groups. Each group runs in a fresh Auditor context.

### Group 1 — Facts & Consistency (methods 1, 2, 3, 4)

| # | Method | What it does |
|---|--------|-------------|
| 1 | Deep read | Read every document fully, noting structure, claims, and overall impression. Foundation for everything else. |
| 2 | Consistency triangulation | Same fact, name, date, or number must be identical across ALL documents. |
| 3 | Claim verification | Every factual assertion checked — is it true, traceable, and supported? |
| 4 | Contradiction detection | Find conflicting statements within and between documents. |

### Group 2 — Structure & Completeness (methods 5, 6, 7, 8)

| # | Method | What it does |
|---|--------|-------------|
| 5 | Completeness audit | What SHOULD exist but doesn't? Missing sections, unexplained terms, promised content that never appears. |
| 6 | Scope boundary check | Document claims to cover X — does it actually? No more, no less. Detect scope creep and coverage gaps. |
| 7 | Terminology consistency | Same concept must use same term everywhere. Detect synonyms used inconsistently or undefined jargon. |
| 8 | Temporal consistency | Dates, timelines, sequences, version references must not contradict each other or reality. |

### Group 3 — Clarity & Flow (methods 9, 10, 11, 12)

These methods are unique to Doc Compiler — they evaluate the document as a piece of writing, not just as a container of facts.

| # | Method | What it does |
|---|--------|-------------|
| 9 | Clarity check | Identify sentences, paragraphs, or sections that are unclear, ambiguous, or require re-reading to understand. Flag jargon without context, overlong sentences, and passive constructions that obscure meaning. |
| 10 | Logical flow | Does the argument or narrative flow logically? Are transitions between sections smooth? Does each paragraph follow from the previous? Are conclusions supported by what came before? |
| 11 | Tone consistency | Is the tone (formal/informal, optimistic/cautious, technical/accessible) consistent throughout? Are there jarring shifts? Does the tone match the document's purpose? |
| 12 | Audience alignment | Is the document appropriate for its intended readers? Would they understand all terms? Is the level of detail right — not too shallow, not too deep? |

### Group 4 — Adversarial (methods 13, 14)

| # | Method | What it does |
|---|--------|-------------|
| 13 | Persona simulation | Test from 3+ reader perspectives: the decision-maker skimming for key points, someone unfamiliar with the subject, a skeptic looking for weak arguments. What breaks for each? |
| 14 | Staleness detection | Find references to people, projects, dates, links, or facts that may no longer be current. Dead links, outdated names, past-tense claims stated as present. |

## Severity Definitions

Every issue must be classified using these definitions. Auditor cannot reclassify to a higher severity than what the definition warrants.

| Severity | Definition | Example |
|----------|-----------|---------|
| critical | Factual error, logical contradiction, or misleading claim that would confuse or misinform the reader | Document says "Phase 2 starts in March" in one place and "April" in another |
| medium | Inconsistency, incomplete coverage, unclear passage that requires reader to guess | Term used without definition; section promised in intro but missing |
| minor | Style, formatting, wording that could be improved but doesn't mislead | Non-blocking, does not extend fix loop |
| observation | Improvement suggestion, subjective preference | Non-blocking, recorded in learnings only |

Only **critical** and **medium** issues are blocking. Minor issues and observations never extend the loop.

## Workflow

### Phase 0: Setup

This phase is interactive — Lead asks the owner these questions before any validation begins. The answers define the rules for the entire run.

**Question 1: Document scope**
"Which documents should I validate?" Accept file paths, glob patterns, or "everything in this directory."

**Question 2: Edit permissions**
For each document (or group), ask:
- **Editable** — Writer can modify this document to fix issues
- **Read-only** — do not modify, but report any issues found in it

If there is only one document, ask: "Should I edit this document directly, or create a copy and work on the copy?"

For large sets (10+ documents), offer a default (e.g., "all editable") and ask the owner to specify exceptions rather than listing every file individually.

**Question 3: Autonomy level**
"How autonomous should I be?"
- **Full auto** — fix everything without asking. Only report at the end.
- **Ask on important** — fix straightforward issues autonomously (typos, number corrections matching source of truth, broken references, formatting). Ask before changes that alter meaning, restructure sections, or resolve ambiguities where multiple interpretations exist (e.g., choosing between two plausible dates, deleting a section, reordering arguments).
- **Approve everything** — propose every change and wait for approval before applying.

**Question 4: Language**
"Should I preserve the original language of the documents, or translate/rewrite in a specific language?" Default: preserve original language.

**Question 5: Context** (optional)
"Is there anything I should know about these documents — who they're for, what they'll be used for, any constraints?" This helps Auditor calibrate methods 11, 12, 13 (tone, audience, persona simulation).

After setup, show the owner:
- Document inventory with edit permissions
- Selected methods (based on document types)
- Autonomy level confirmed
- Ask confirmation to start

If git is available: `git add -A && git commit -m "doc-compiler: pre-validation snapshot"`

### Phase 1: Validation Groups

Launch Writer and Auditor as separate agents.

**Token tracking**: create `.token-log/doc-compiler-<YYYYMMDD-HHmmss>.jsonl`

For each group (1 through 4, skipping groups where no methods apply):

1. **Fresh Auditor context** — new Auditor instance for each group
2. Auditor runs assigned methods on all documents in scope
3. Auditor reports: issues with severity
4. If critical issues found in **editable** documents — Writer fixes them immediately before next group
5. Issues in **read-only** documents are recorded but not fixed
6. Non-critical issues accumulate for Phase 2

**Auditor input**: only final documents + holdout files + LEARNINGS + setup context (audience, purpose).
**Auditor separation**: Auditor DOES NOT receive Writer's changes or reasoning.

### Phase 2: Consolidated Review

After all groups complete:
1. Merge all remaining (unfixed) issues from all groups (deduplicate). Issues fixed during Phase 1 are recorded as resolved and excluded from this list.
2. Separate into: fixable (editable docs) and reportable (read-only docs)
3. Show consolidated table: method | issues | severity | files | editable?
4. Proceed to fix loop (unless autonomy = "approve everything", in which case show proposed changes first)

### Phase 3: Fix & Re-validate (autonomous loop)

This loop runs according to the autonomy level set in Phase 0:

1. If git available: `git add -A && git commit -m "doc-compiler: pre-writer-round-N"`
2. Writer fixes issues in **editable documents only** (critical first, then medium)
   - **Full auto**: fix without asking
   - **Ask on important**: fix straightforward issues, ask for ambiguous ones
   - **Approve everything**: propose each fix, wait for approval
3. **Lead sanity check**: do fixes introduce new inconsistencies? Quick cross-reference check.
4. If git available: `git add -A && git commit -m "doc-compiler: post-writer-round-N"`
5. **Model rotation**: alternate Auditor model each round (Opus → Sonnet → Opus)
6. **NEW Auditor** (fresh context) re-validates:
   - Changed files + files referencing changed files
   - Re-run the method group(s) that originally found the issues being fixed
   - **Lead provides minimal context**: list of changed files, one-line fix summary, previous round issue count only

**Auditor integrity rules** — given to every Auditor instance:
- Finding zero issues is a valid and valuable outcome. A clean document is the goal, not a failure of your review.
- Do NOT lower severity threshold to avoid returning empty-handed. If the only issues you find are style preferences — report zero issues.
- Inflating severity invalidates the round.
- Respect the author's voice. The goal is to fix problems, not to rewrite the document in your preferred style.
- For Group 3 methods (Clarity & Flow): only flag passages where meaning is genuinely unclear or structure actively hinders comprehension. Well-written informal text is not an issue.

7. **Loop condition**: continue until **2 consecutive clean Auditor rounds**
   - "Clean" = no critical or medium issues in editable documents
   - Issues in read-only documents are tracked but don't block the gate
   - Safety limit: max 15 rounds (non-technical docs converge faster than specs)

**Sonnet health check**: if Sonnet Auditor has not responded within 5 minutes, log "Sonnet timeout, retrying with Opus" and restart the round with Opus.

### Phase 4: Gate Decision

Gate PASS requires:
- 2 consecutive clean Auditor rounds (different models preferred)
- All applicable methods covered with evidence
- No critical or medium issues remaining in editable documents
- Read-only document issues listed in report

Gate FAIL: report remaining issues, rounds completed, convergence trend. Ask owner how to proceed.

### Phase 5: Report

Generate `DOC-REVIEW-REPORT.md` alongside the validated documents:
- Date, time, duration
- Documents validated (with edit permissions noted)
- Setup parameters (autonomy level, language, context)
- Methods applied
- Issues found and fixed (all rounds)
- Issues in read-only documents (unfixed, listed for owner)
- Model rotation log
- Gate status
- If git available: `git add -A && git commit -m "doc-compiler: validation complete — GATE [PASS/FAIL]"`

Show owner the final summary.

### Phase 6: Learn

Runs as a **lightweight learning-collector agent** (background, Opus, fresh context).

1. Collector reads: `DOC-REVIEW-REPORT.md` and current `LEARNINGS.md`, plus holdout files
2. Collector identifies new patterns, recurring issues, and method effectiveness
3. Collector writes new L-entries to `LEARNINGS.md`
4. **Auto-promotion**: patterns appearing 2+ times → new holdout scenario or antipattern
5. **Auto-archive**: MATERIALIZED entries → move to Archived section
6. If git available: `git add -A && git commit -m "doc-compiler: update learnings"`
7. **Token cost summary**: include estimated cost in the final summary line.
   Calculate: total_tokens × blended_rate (opus=$0.033/1K, sonnet=$0.0066/1K, haiku=$0.0006/1K).
   Example: "~168k tokens (~$5.54), ~2 minutes". The cost goes in every DONE status line too.
8. Print: `=== Doc Compiler: COMPLETE ===`

## Writer Agent Rules

- Writer ONLY edits documents marked as **editable** in Phase 0 setup. NEVER touch read-only documents.
- Writer respects the **autonomy level**: full auto, ask on important, or approve everything.
- Writer preserves the author's voice and style. Fix problems, don't rewrite.
- Writer preserves document language unless explicitly asked to translate.
- Writer reports all changes as plain text summaries: what changed and why.
- Writer DOES NOT read holdout files. Holdout principle.

## Lead Agent Rules

- Lead coordinates. Lead DOES NOT edit files or parse JSON from task output.
- Lead enforces edit permissions — never allows Writer to modify read-only documents.
- Lead enforces autonomy level — escalates to owner when required.
- Report results in plain text with tables. No raw JSON.
- Always show: issues count by severity, files affected, edit status.

### Timestamp logging
```
=== Doc Compiler: [Step Name] START [YYYY-MM-DD HH:MM:SS] ===
=== Doc Compiler: [Step Name] DONE [YYYY-MM-DD HH:MM:SS] — [duration] — ~[N]k tokens (~$X.XX) — [summary] ===
```

### Token tracking

At workflow start, create `.token-log/doc-compiler-<timestamp>.jsonl`.

After each step completes (when you have `total_tokens` and `duration_ms` from
the step or task notification), append a JSONL entry:
`{"agent": "<step-name>", "model": "<model>", "total_tokens": N, "duration_ms": N, "timestamp": "<ISO>", "phase": "<phase>"}`

At workflow end, read the log and print a token usage summary table with
per-phase breakdown and estimated cost.
Blended rates (per 1K tokens): opus=$0.033, sonnet=$0.0066, haiku=$0.0006.

## Evidence Protocol

For EACH method run, Auditor produces:

```json
{
  "method_id": 10,
  "method_name": "Logical flow",
  "depth": "deep",
  "what_checked": ["argument structure", "section transitions", "conclusion support"],
  "what_not_checked": [],
  "files_examined": ["proposal.md:1-150"],
  "issues_found": [],
  "confidence": "high",
  "clean": true
}
```

Plus a human-readable summary.

## Self-audit Rule

After completing all assigned methods, Auditor honestly assesses:
- For each method: was it deep or shallow?
- If >50% shallow — round is NOT clean, needs re-run
- For Group 3 methods: "I read the document as a reader, not as a scanner" — confirming genuine reading comprehension, not keyword matching
