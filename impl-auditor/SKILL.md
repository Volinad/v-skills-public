---
name: Implementation Auditor
description: "Validates that code matches documentation — bridges the gap between passing tests and spec-compliant implementation. Use this skill when the user wants to audit code against specs, check if implementation follows the architecture, verify ADR compliance, find orphan code or unimplemented features, detect doc-vs-code drift, or verify that business invariants and state machines are enforced in code. Also use when the user says 'does the code match the docs', 'audit implementation', 'check code against spec', 'find drift', or 'verify ADR compliance'. Run AFTER spec-compiler (docs must be clean first) and AFTER tests pass."
---

# Implementation Auditor

## Purpose

Implementation Auditor validates that **code matches documentation**. It bridges the gap between "tests pass" and "implementation follows the spec." Spec-compiler ensures docs are internally consistent. Impl-auditor ensures code is consistent with those docs.

## Problem Statement

A well-validated documentation set (specs, architecture, features) describes the system that should exist. The actual codebase may diverge from this description in ways that unit tests do not catch:

- A feature passes all tests but implements a different behavior than what the spec describes
- Architectural Decision Records (ADRs) are violated in code (e.g., "all calls through router" but some bypass it)
- Database schema in code has fewer/more tables than architecture describes
- API endpoints in code don't match the documented contract (different paths, different response shapes)
- Environment variables used in code are undocumented, or documented ones are unused
- User flows described in the spec break at integration points even though each piece works individually
- Code exists that corresponds to no feature (orphan code), or features exist with no corresponding code
- Documented business invariants or state-machine constraints are not enforced in code

## Core Principle: Auditor Does Not Fix

Unlike spec-compiler and doc-compiler which fix issues automatically, impl-auditor **only reports discrepancies**. This is because when code and docs disagree, it's ambiguous which one is wrong:

- The code might be correct and the docs outdated
- The docs might be correct and the code incomplete
- Both might be partially right

The Owner decides what to fix and where. Impl-auditor provides the evidence.

## Prerequisites

- Git repository initialized (for tracking changes and reproducible snapshots)
- Documentation set present (at minimum: one spec, architecture doc, or feature definitions file)
- Codebase present (source files, package manifests)
- No running server required — impl-auditor works from static analysis only

## Input

Two categories of input, always used together:

**Documentation (source of truth for intent):**
- Project specification (PROJECT-SPEC or equivalent)
- Architecture document (schema, API contracts, ADRs)
- Feature definitions (JSON or Markdown with steps, tests, acceptance criteria)
- CLAUDE.md or equivalent development rules
- Any other document that describes what the code should do

**Codebase (source of truth for reality):**
- Source files (backend, frontend, scripts)
- Database models / migrations
- Route definitions
- Test files
- Configuration files (.env.example, docker-compose, CI configs)
- Package manifests (requirements.txt, package.json)

## What Implementation Auditor Is NOT

- **Not a linter.** It does not check code quality, style, or best practices.
- **Not a test runner.** It does not execute tests or check coverage.
- **Not a security scanner.** It does not look for vulnerabilities (unless the spec explicitly defines security requirements and the code violates them).
- **Not a code reviewer.** It does not suggest better implementations.

It answers one question: **"Does the code do what the docs say it should?"**

## Context Management

Reading full documentation sets plus entire codebases exceeds the context window of any single model instance for real projects. Impl-auditor manages context through subsetting and chunking:

### Subsetting Strategy

Each audit phase operates on a focused subset of inputs:
- **Phase 1 (Structural Mapping):** reads only documentation index files (table of contents, feature list, schema summary) and code entry points (route registration files, model registry, package manifests). Does NOT read full source files.
- **Phase 2 (Rule Compliance):** receives the Phase Bridge Package from Phase 1 plus targeted file excerpts relevant to each ADR/rule being checked. One rule = one focused read.
- **Phase 3 (Behavioral Verification):** receives Phase Bridge Package plus the specific feature definition and the code files that map to that feature. One feature at a time.
- **Phase 4 (Drift Scan):** reads file lists and counts (not file contents) for orphan detection; reads placeholder pattern scan results (not full files).

Three-tier read policy:
- **Tier 1:** entry points and inventories (default for all phases)
- **Tier 2:** targeted file reads guided by the Phase Bridge Package and risk flags
- **Tier 3:** full-subtree escalation only for disputed or high-impact findings

### Chunking Strategy

When a single file exceeds safe read size:
- Read line ranges, not full files (e.g., `file.py:1-100` then `file.py:101-200`)
- For route files: read decorator lines only first, then read handler bodies for flagged routes
- For model files: read class declarations and field names first, then read full models for flagged discrepancies
- For migration files: read migration metadata (table names, column names) not full SQL bodies

### Phase Bridge Package

Phase 1 produces a **Phase Bridge Package** that all subsequent phases receive instead of raw documentation. This is the primary mechanism for passing context across phase boundaries without re-reading everything.

The bridge package contains four components:

1. **Structural Mapping Summary** — a compact Markdown table (typically under 200 lines) mapping doc entities to code entities:

```markdown
| Entity Type | Doc Reference | Code Reference | Status | Notes |
|-------------|--------------|----------------|--------|-------|
| Feature F-001 | FEATURES.json | src/services/database.ts | match | |
| Feature F-010 | FEATURES.json | src/workers/processor.ts | partial | missing retry logic |
| Endpoint GET /api/v1/products | ARCHITECTURE.md:L200 | src/routes/products.ts:L15 | match | |
| Table: users | ARCHITECTURE.md:L350 | src/models/user.ts | drift | code has extra column |
| Env: REDIS_URL | .env.example | src/services/cache.ts:L8 | match | |
```

2. **Risk flags from Phase 1** — features with partial or no mapping, complex multi-file features that span many modules, and features that span both backend and frontend without a clear seam.

3. **Candidate file sets per feature/rule** — for each feature or rule, a short list of which code files to read in subsequent phases. This lets later phases go directly to the right files rather than re-deriving the mapping.

4. **Known ambiguities** — dynamic dispatch, plugin architectures, generated code boundaries, or other patterns where static mapping is uncertain. Later phases receive these flags so they can apply `confidence: low` appropriately instead of treating uncertain mappings as clean matches.

## 17 Audit Methods

Methods are organized in 4 groups. Each group runs in a fresh Auditor context. The Lead provides the Phase Bridge Package to each phase.

### Group 1 — Structural Mapping (methods IA-1 through IA-4)

These methods verify that documented entities exist in code.

| # | Method | What it does |
|---|--------|-------------|
| IA-1 | Feature-to-code mapping | For each **done** feature in FEATURES files: does corresponding code exist? "Corresponding code exists" means at minimum a dedicated module, file, or function — not merely a grep match in an unrelated file. Check that every step has implementation, every test has a test file, every deliverable is present. |
| IA-2 | API contract verification | Collect all endpoints from architecture/feature docs. Collect all routes from code (FastAPI routers, Express routes, etc.). Diff: documented but missing in code? In code but undocumented? For each matching endpoint: do request/response shapes match? "Shape matching" means: field names must match, types must be compatible, required/optional alignment must match. |
| IA-3 | Schema verification | Collect all tables/models from architecture docs. Collect all models from code (SQLAlchemy, Prisma, etc.) and migrations. Diff: documented but missing? In code but undocumented? For each matching table: do columns, types, and relationships match? |
| IA-4 | Dependency graph check | For **documented component boundaries and integration dependencies only**: if the architecture or an ADR states that module A must not depend on module B, verify the code enforces this. Check only boundaries explicitly stated in architecture docs or ADRs. Internal dependencies (utils, loggers, helpers) are out of scope. Allow non-import evidence: message bus subscriptions, config-driven orchestration, SQL reads, network calls — any mechanism by which one component consumes another's outputs counts as a dependency. |

### Group 2 — Rule Compliance (methods IA-5 through IA-8)

These methods verify that documented rules and constraints are followed in code.

| # | Method | What it does |
|---|--------|-------------|
| IA-5 | ADR compliance | For each Architectural Decision Record: search the codebase for violations. Example: ADR says "all database access through repository layer" — search for direct SQL queries outside repositories. |
| IA-6 | Security rule verification | Collect security requirements from docs (encryption, auth, access control). Verify each in code: are keys encrypted? Is auth middleware applied? Are immutable logs actually append-only? |
| IA-7 | Configuration completeness | Collect all env vars from .env.example and docs. Collect all env var reads from code (os.environ, process.env). Diff: documented but unused? Used but undocumented? Do defaults match? |
| IA-8 | Convention compliance | Collect **implementation-relevant** coding conventions from CLAUDE.md and docs: time semantics (UTC), layer boundaries, serialization rules, idempotency, transaction boundaries, async patterns. Cosmetic conventions (naming style, file organization) are out of scope unless they affect runtime behavior. Example: "all times in DB as UTC" — check model definitions for timezone-naive datetime fields. |

### Group 3 — Behavioral Verification (methods IA-9 through IA-12, IA-17)

These methods verify that documented behaviors are implemented correctly.

| # | Method | What it does |
|---|--------|-------------|
| IA-9 | User flow tracing | For each documented user flow or scenario: trace through the code path. Does the code handle each step? Are transitions between steps possible? Does data flow correctly between components? |
| IA-10 | Acceptance criteria check | For each **done** feature's acceptance criteria: can the criterion be verified from the code? Is the behavior actually implemented, not just tested? Example: "pagination returns max 50 items" — does the query have a LIMIT? |
| IA-11 | Error path verification | For each documented error handling requirement: does the code handle that error case? Are error responses in the correct format? Are failures logged/reported as specified? |
| IA-12 | Documented edge case verification | For **explicitly documented** edge cases only (concurrent access, empty states, boundary values, timezone handling): does the code handle them? Undocumented edge cases are out of scope — the auditor checks what the spec says, not what it should say. Static verification of concurrency and timing should be marked `confidence: low` unless the spec defines specific guard requirements. |
| IA-17 | Invariant / state-transition verification | For each documented business invariant, state machine constraint, or data contract: verify the code enforces it. Examples: "task cannot go from COMPLETED back to PENDING", "one active subscription per user", "role=admin/member must propagate consistently", "soft-deleted entities never appear in active queries", "invoice total must always equal sum of line items", "this field is immutable after creation." Check guard clauses, validation logic, and state transition code. |

### Group 4 — Drift Detection (methods IA-13 through IA-16)

These methods find things that exist in one place but not the other.

| # | Method | What it does |
|---|--------|-------------|
| IA-13 | Orphan code detection | Find code modules, endpoints, models, or components that are not referenced by any feature or document. This is undocumented functionality — either the docs need updating or the code shouldn't exist. **Exclusion:** generated code (Alembic migration stubs, auto-generated client code, scaffold boilerplate) is excluded from orphan detection. |
| IA-14 | Unimplemented features | Find features marked as "done" in FEATURES files but with missing or stub implementations. Detect placeholder code (TODO, NotImplementedError, pass, empty functions). |
| IA-15 | Test-spec alignment | For each test: does it verify what the acceptance criteria says? Do test names match the documented test names? Are there tests for things not in the spec, or spec items without tests? |
| IA-16 | Migration-schema drift | Compare the current database state (from running migrations) with the model definitions in code and the schema in docs. Three-way diff: docs vs models vs migrations. |

## Feature Status Filtering

Impl-auditor only audits features marked `done` (or equivalent status indicating complete implementation). Features with status `planned`, `in-progress`, `testing`, or equivalent are **out of scope**. Auditing incomplete features produces false positives and wastes audit time.

In Phase 0, the Lead reads the feature status field from FEATURES files and excludes all non-done features from the audit scope. The exclusion count is reported in the consolidated report header.

## Severity Definitions

**Design decision:** Impl-auditor replaces spec-compiler's "medium" with "major" because implementation discrepancies carry higher consequence — a wrong API shape or violated ADR is more serious than a doc wording inconsistency. The "drift" severity captures undocumented code as a distinct finding class: not wrong, but accumulating silently.

| Severity | Definition | Example |
|----------|-----------|---------|
| critical | Entire feature/entity is missing or fundamentally wrong — the spec-defined concept does not exist in code at all | Spec says "users table has role field" but table has no role field; a "done" feature has no corresponding code |
| major | Feature/entity exists but behavior or shape differs significantly — exists but doesn't work as documented | API returns different response shape than documented; ADR is violated in multiple call sites |
| minor | Small discrepancy unlikely to affect functionality | Documented default value is 50, code default is 100 |
| drift | Not wrong, just undocumented (or documented but unimplemented) — note: drift accumulates | Extra endpoint exists in code but not in docs; 20 drifts may indicate a systemic documentation problem even though each is harmless alone |
| observation | Pattern noticed, Owner should evaluate | Several features access DB directly instead of through service layer |

**Blocking severities:** critical and major issues are blocking (prevent sign-off). Minor, drift, and observation findings are non-blocking.

**Drift escalation rule:** if total drift findings >= 15 (or Owner-defined threshold), the entire drift category auto-escalates to major in the executive summary. This forces Owner attention on systemic documentation rot rather than letting many small drifts slip through individually.

**Discriminator between critical and major:** Critical = the spec-defined entity does not meaningfully exist in code (missing table, missing feature, missing endpoint entirely). Major = the entity exists but its behavior, shape, or constraints differ significantly from the spec (wrong response shape, wrong field types, violated ADR, missing business logic).

## Workflow

### Phase 0: Setup

1. **Identify documentation set:** scan for known documentation patterns — files named `PROJECT-SPEC*.md`, `*ARCHITECTURE*.md`, `FEATURES-*.json`, `CLAUDE.md`, `*-SPEC*.md`, `*ADR*`, `README.md`. Also scan for any Markdown files in a `docs/` directory. Build a file list.

2. **Identify codebase scope:** read package manifests to determine tech stack (requirements.txt -> Python/FastAPI/SQLAlchemy; package.json -> Node/React/Next.js). Scan for framework markers: presence of `routers/` + `models/` + `alembic.ini` -> FastAPI+SQLAlchemy project; presence of `pages/` or `app/` + `next.config.*` -> Next.js frontend. Determine which top-level directories contain implementation code vs scripts vs tests vs config.

   **Greedy discovery pass:** beyond entry-point directories, grep for framework markers in ALL source files: `@app.get`/`@router.` (FastAPI), `export default function`/`getServerSideProps` (Next.js), `class.*Model.*Base` (SQLAlchemy), `Router()` (Express). This catches code outside expected directories and prevents blind spots in the Structural Map.

3. **Ask Owner:** "Are there areas I should focus on? Any known discrepancies to ignore? Any directories or files to exclude?" Owner-declared exclusions must be documented under an **Exclusions** section in the final `IMPL-AUDIT-REPORT.md`.

4. **Quick inventory from docs:** count features (total and by status), documented endpoints, documented tables, documented env vars.

5. **Quick inventory from code:** count route definitions (grep for decorators), model classes, migration files, test files, actual env var reads.

6. **Show comparison:** "Docs describe X endpoints (Y done features), code has Z routes. Docs describe N tables, code has M models." Flag large gaps immediately.

7. **Ask confirmation** to start deep audit.

### Phase 1: Structural Mapping

**Token tracking**: create `.token-log/impl-auditor-<YYYYMMDD-HHmmss>.jsonl`

Fresh Auditor context. Run methods IA-1 through IA-4. This produces the **Phase Bridge Package**: the Structural Mapping Summary table, risk flags, candidate file sets, and known ambiguities (see Context Management).

The Lead saves the Phase Bridge Package and provides it as context to all subsequent phases. This is the mechanism for passing Phase 1 findings to fresh Auditor contexts — each fresh context receives the bridge package as part of its prompt, not the raw documents.

This phase is the foundation — all subsequent phases reference this mapping.

### Phase 2a: Rule Compliance (Group 2)

Fresh Auditor context. Run methods IA-5 through IA-8 against the Phase Bridge Package from Phase 1.

Skip condition: skip this phase entirely if NONE of the following are documented: ADRs, security requirements, coding conventions. If any one of the three exists, run this phase — the applicable methods will self-select based on what is present.

This phase produces the **Rule Compliance Report**.

### Phase 2b: Behavioral Verification (Group 3)

Fresh Auditor context. Run methods IA-9 through IA-12 and IA-17 against the Phase Bridge Package from Phase 1.

For large projects, process features in batches (see Context Management — one feature at a time per read).

This phase produces the **Behavioral Gaps Report**.

### Phase 3: Drift Scan (Group 4)

Fresh Auditor context. Run methods IA-13 through IA-16.

This phase produces the **Drift Report**: what exists only in code or only in docs.

### Phase 4: Consolidated Report

Generate `IMPL-AUDIT-REPORT.md`:

- Date, project, scope
- **Exclusions** section: any files or areas excluded at Owner request (Phase 0 step 3), plus features excluded by status filter (count of non-done features skipped)
- Executive summary: X discrepancies found (N critical, N major, N minor, N drift, N observation)
- **Structural Mapping** (Phase 1): table of features/endpoints/tables/configs with match status
- **Rule violations** (Phase 2a): each ADR/security rule/convention with pass/fail and evidence
- **Behavioral gaps** (Phase 2b): user flows that break, missing error handling, unverified AC, violated invariants
- **Drift inventory** (Phase 3): orphan code, unimplemented features, test misalignment
- **Non-auditable items** (see Non-auditable Documentation section): items marked `auditability: insufficient`
- Recommendations: prioritized list of what to investigate first
- `git commit -m "impl-auditor: audit report — [X critical, Y major, Z minor, W drift]"`

### Phase 5: Learn

This phase captures methodology improvements. It runs as a **lightweight collector agent** with fresh context — Opus (Sonnet is unreliable as a background agent for synthesis tasks).

**A learning exists to change what a future audit does — that is the entire bar.** On a mature skill most runs produce zero new learnings, and that is the healthy, expected outcome, not a failure. Recording an instance of something the skill already does changes no future audit; it only grows a file every later run must read in full. Hold the collector to the same standard as the audit itself: finding nothing new is valid and valuable, and padding the file to "show work" is a defect, not diligence.

1. Collector reads `IMPL-AUDIT-REPORT.md`, current `LEARNINGS.md` (at `~/.claude/skills/impl-auditor/LEARNINGS.md` or the project-local copy), and the holdout file (`holdout/audit-procedures.md`) — to see what the skill already does, so it does not re-record it.
2. **Two-question test — apply to every candidate before writing it.** Write an L-entry only if BOTH hold:
   - **Novel** — absent from the holdout procedures, the known-false-positive guards, and existing entries. A fresh instance of an existing procedure/FP-guard is NOT novel.
   - **Actionable** — it changes a future audit: a new check, a severity-calibration rule, or a project-type posture. If you cannot state the novelty in one sentence, it is not worth keeping.
3. **Reconfirmations, and counting toward promotion.** This skill promotes a pattern only after 3 occurrences across different projects, so an UN-promoted entry may legitimately log a 2nd/3rd sighting — but as ONE terse line (date + context + "Nth occurrence"), never a fresh paragraph. Once a pattern is promoted to a holdout procedure it is done: further sightings go in the run's IMPL-AUDIT-REPORT, never back into LEARNINGS. Keep no confirmation ledger for an already-materialized procedure.
4. **Auto-promotion:** a genuinely new pattern seen 3+ times across different projects → materialize it as a holdout procedure or a Known-False-Positive guard. Two occurrences may be one project's quirk; three across contexts confirms a durable pattern. A specialization of an existing procedure → annotate that one, don't add a standalone entry. A learning that implies changing this skill's own instructions → flag it in the final summary as "SKILL.md update suggested: …"; the collector never edits SKILL.md (skill edits go through skill-creator).
5. **Archive what is already implemented.** Once an entry's substance lives anywhere a future audit reads it — a holdout procedure/FP-guard OR SKILL.md/phase logic — collapse it to a one-line pointer in the Archived index, regardless of the NOTED/MATERIALIZED label. Keep each surviving entry to its reusable core (the pattern + the check), naming at most the ONE closest entry it refines; run specifics (which change, which file, which input) belong in the IMPL-AUDIT-REPORT.
6. `git commit -m "impl-auditor: update learnings"`
7. **Token cost summary**: include estimated cost in the final summary line.
   Calculate: total_tokens × blended_rate (opus=$0.033/1K, sonnet=$0.0066/1K, haiku=$0.0006/1K).
   Example: "~168k tokens (~$5.54), ~2 minutes". The cost goes in every DONE status line too.
8. Print: `=== Impl Auditor: COMPLETE ===`

After this message: do NOT start new tasks. Audit is done.

## Holdout Mechanism

Impl-auditor maintains its own holdout files for audit quality assurance — analogous to spec-compiler's holdout files.

**Holdout file location:** `~/.claude/skills/impl-auditor/holdout/audit-procedures.md` (global) or `.claude/skills/impl-auditor/holdout/audit-procedures.md` (project-local).

**Holdout principle:** The Auditor agent reads holdout files and LEARNINGS before running methods.

**What audit-procedures.md contains:**
- Concrete execution procedures for each of the 17 methods (IA-1 through IA-17)
- Framework-specific lookup tables (where to find routes in FastAPI vs Express vs Django, etc.)
- Known false-positive patterns to exclude
- Thresholds for flagging drift vs. noise

The detailed execution procedures are developed incrementally as experience accumulates. The method descriptions in this skill are summary-level; the holdout file is the authoritative procedure reference.

## Error Handling

When a method encounters problems, the Auditor does not silently skip — it documents the failure explicitly in the evidence block.

**When a method can't parse code** (syntax errors, unexpected format, unsupported framework):
- Mark the method as `"depth": "blocked"` in the evidence block
- Record: what was attempted, what error occurred, what was not checked as a result
- Classify as an observation (not a discrepancy) — the blocker is the finding
- Continue with remaining methods; do not abort the phase

**When expected files can't be found** (no FEATURES files, no migration directory, etc.):
- Mark the corresponding method as `"depth": "not-applicable"` in the evidence block
- Exclude that method from the blocking-issue check
- Note in the consolidated report under "Methods not applicable"

**When a method produces inconclusive results** (e.g., dependency graph check finds no imports but the feature might use dynamic loading):
- Mark `"confidence": "low"` in the evidence block
- Flag as an observation for Owner review, not a discrepancy
- Do not promote to major/critical without corroborating evidence from another method

## Non-auditable Documentation

Sometimes the right finding is not "code drift" but "spec too underspecified to audit." When a documented requirement is too vague, ambiguous, or incomplete to support code-vs-doc adjudication, the Auditor marks it as `auditability: insufficient` in the evidence block.

Examples: "system handles errors gracefully" (no specific error types defined), "data is processed efficiently" (no performance criteria), "authentication is secure" (no specific mechanism).

These are reported in the consolidated report under "Non-auditable items" — they are not discrepancies but documentation improvement opportunities for the Owner.

## Method Selection Guide

Not every project needs all 17 methods. The Lead selects based on project characteristics:

| Project characteristics | Always apply | Likely apply | Consider skipping |
|------------------------|-------------|-------------|------------------|
| Small project (<=10 features, <=20 endpoints) | IA-1, IA-2, IA-3, IA-14 | IA-7, IA-10, IA-15 | IA-4, IA-5, IA-6, IA-8, IA-9, IA-11, IA-12, IA-13, IA-16, IA-17 |
| Large project (>20 features, >50 endpoints) | IA-1 through IA-17 (all) | — | None |
| No ADRs or security/convention docs | IA-1, IA-2, IA-3, IA-14 | IA-7, IA-10, IA-13, IA-15 | IA-5, IA-6, IA-8 |
| Strong architectural docs (ADRs present) | IA-1, IA-2, IA-3, IA-5, IA-6 | IA-4, IA-7, IA-8, IA-14, IA-16 | IA-9, IA-11, IA-12 |
| API-heavy project | IA-2, IA-7, IA-10 | IA-1, IA-3, IA-9, IA-13, IA-14 | IA-4, IA-12 |
| Database-heavy project | IA-3, IA-16 | IA-1, IA-2, IA-6, IA-14 | IA-9, IA-11, IA-12 |
| Project with state machines or documented invariants | IA-1, IA-17 | IA-9, IA-10, IA-12 | — |
| Pre-release audit | All methods (IA-1 through IA-17) | — | None |
| Post-sprint spot check | IA-1, IA-14, IA-15 | IA-2, IA-3, IA-7 | IA-4 through IA-13, IA-16, IA-17 |

When in doubt, include the method. False positives (method finds nothing) are cheap. False negatives (skip method, miss issue) are expensive.

## Evidence Protocol

Based on spec-compiler's protocol, extended with dual-source fields. For each method, Auditor produces:

```json
{
  "method_id": "IA-2",
  "method_name": "API contract verification",
  "depth": "deep",
  "what_checked": ["GET /api/v1/products — params, response shape", "POST /api/v1/users — request body, validation"],
  "what_not_checked": ["WebSocket endpoints — not in scope for this method"],
  "docs_source": ["docs/ARCHITECTURE.md:lines 200-250"],
  "code_source": ["src/routes/products.ts:1-80", "src/routes/users.ts:1-120"],
  "discrepancies_found": [],
  "confidence": "high",
  "clean": true
}
```

The dual-source fields (`docs_source` / `code_source`) replace the single `files_examined` field from spec-compiler because impl-auditor always has two distinct source types. Plus a human-readable summary. Lead never parses raw JSON — Auditor provides text summaries.

## Lead Agent Rules

You are the Lead. You coordinate. You follow these rules without exception.

### Role boundaries
- You DO NOT edit, fix, or modify any project files. NEVER.
- You DO NOT parse JSON from agent task output files. NEVER.
- You DO NOT offer to make "small fixes" yourself.
- Only the Owner decides what to fix and where (code vs. docs). See Core Principle: Auditor Does Not Fix.

### Autonomous flow
- After each phase completes, IMMEDIATELY proceed to the next phase.
- Do NOT wait for Owner input between phases. The audit is autonomous.
- Only stop for Owner input at Phase 0 (setup confirmation) and Phase 4 (final report delivery).
- Deliver the Phase Bridge Package from Phase 1 as explicit context to each subsequent fresh Auditor.

### Agent health check
- If any agent has not responded in 5 minutes — restart with a different model.
- Specifically for Sonnet: if no response in 5 minutes, log "Sonnet timeout, retrying with Opus" and restart the phase with Opus.
- If Lead has no active tasks and no pending responses for 5 minutes — STOP.
- NEVER endlessly poll task output files. Max 3 status checks, then ask Owner.

### Communication
- Report results in plain text with tables. No raw JSON.
- Always show: discrepancy count by severity, phases completed, files affected.

### Timestamp logging
Print at START and DONE of every major step:
```
=== Impl Auditor: [Phase Name] START [YYYY-MM-DD HH:MM:SS] ===
=== Impl Auditor: [Phase Name] DONE [YYYY-MM-DD HH:MM:SS] — [duration] — ~[N]k tokens (~$X.XX) — [summary] ===
```

### Token tracking

At workflow start, create `.token-log/impl-auditor-<timestamp>.jsonl`.

After each phase completes (when you have `total_tokens` and `duration_ms` from
the phase or task notification), append a JSONL entry:
`{"agent": "<phase-name>", "model": "<model>", "total_tokens": N, "duration_ms": N, "timestamp": "<ISO>", "phase": "<phase>"}`

At workflow end, read the log and print a token usage summary table with
per-phase breakdown and estimated cost.
Blended rates (per 1K tokens): opus=$0.033, sonnet=$0.0066, haiku=$0.0006.

## Auditor Agent Rules

These rules apply to every Auditor instance in impl-auditor.

### Integrity rules
- Finding zero discrepancies is a valid and valuable outcome. A codebase that matches its docs is the goal, not a failure of your review.
- Do NOT lower your severity threshold to avoid returning empty-handed. If the only issues you find are trivial style mismatches — that means the implementation is clean. Report zero discrepancies.
- Inflating severity (classifying a minor label mismatch as "critical") invalidates the phase and wastes Owner time. Use the severity definitions strictly.

### Self-audit rule
After completing all assigned methods, Auditor honestly assesses:
- For each method: was the check deep or shallow?
- If >50% shallow — the phase is NOT clean, needs re-run with narrower scope
- "Clean pass" with shallow checks = false confidence

### Zero-issues validity
A phase with zero findings is explicitly valid. Do not add "borderline" or "possible" issues to avoid an empty report.

### Severity inflation guard
The critical/major boundary is strict:
- Critical = entity does not exist or is fundamentally absent
- Major = entity exists but behavior/shape is wrong
- When in doubt between critical and major — use major
- When in doubt between major and minor — use minor
- Escalate only with concrete evidence, not suspicion

## Pipeline Diagram

```
spec-compiler --> Clean docs
                       |
                       v
              Implementation (code)
                       |
                       v
              Tests pass (pytest, playwright)
                       |
                       v
             impl-auditor --> Discrepancy report
                       |
                       v
              Owner decides what to fix
                       |
                  +----+----+
                  v         v
             Fix code    Fix docs
                  |         |
                  v         v
            Re-run tests  Re-run spec-compiler
                  |         |
                  +----+----+
                       v
              Re-run impl-auditor
```

## Key Design Decisions

### Why no auto-fix?
When docs say "12 endpoints" and code has 9, the right fix could be adding 3 endpoints, updating docs to 9, or some combination. Only an Owner with project context can decide.

### Why separate from spec-compiler?
Spec-compiler validates docs against docs. Impl-auditor validates code against docs. Different inputs, different methods, different skills. Combining them would create a massive skill with confused responsibilities.

### Why structural mapping first?
If we don't know which features map to which code, behavioral checks are meaningless. The structural mapping is the Rosetta Stone — it tells us what to compare against what.

### Why "major" instead of "medium"?
Implementation discrepancies carry higher consequence than doc inconsistencies. "Major" better communicates the stakes. Blocking behavior is the same: critical and major are both blocking.

### Why "drift" as a severity?
Drift is distinct from "wrong." Each drift item alone is often harmless, but 20 drifts indicate a systemic documentation maintenance problem. Aggregating them as a named category makes the systemic pattern visible.

### Framework awareness
The auditor needs to understand the project's tech stack to find the right things:
- FastAPI: check `@router` decorators in `routers/` directory
- SQLAlchemy: check `class Model(Base)` in `models/` directory
- React/Next.js: check `pages/` or `app/` directory for routes
- Alembic: check `versions/` for migrations

Phase 0 detects the framework from package manifests and adjusts method execution accordingly.
