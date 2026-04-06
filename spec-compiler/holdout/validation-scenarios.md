# Holdout Validation Scenarios

This file is accessible ONLY to Auditor Agent. Writer Agent MUST NOT see it.

## Principle

Holdout scenarios are analogous to holdout sets in ML. The development agent (Writer) doesn't know what specific checks Auditor will run, so it cannot optimize for them.

---

## Scenario 1: Number Integrity

For every number in documentation (feature count, tables, endpoints, tests, env vars):
1. Find all places where this number is mentioned
2. Recount from source of truth (JSON files, source code, configs)
3. Do all occurrences match?

**Typical traps:**
- Summary says "23 features" but counting JSON entries yields 24
- Architecture section "Inventory: 7 tables" — actually 6
- "12 modules" — 12 of what? Sections? Routers? Files?

After Writer adds/removes items — recount independently (don't trust Writer's numbers).

## Scenario 2: Password/Secret Consistency

Collect all mentions of passwords, keys, credentials:
- .env / .env.example
- docker-compose.yml
- init.sh / setup scripts
- CI yaml
- Test fixtures / conftest
- CLAUDE.md or equivalent

All values identical? Crypto keys valid format (not stubs)?

Also check generated config files (alembic.ini, settings.py, etc.) with hardcoded secrets — are they in .gitignore?

## Scenario 3: Shell Script Execution

For every script (init.sh, CI yaml, Makefiles):
1. Mentally execute line by line
2. Track: cwd, env vars, running processes
3. `cd dir1 && ... && cd dir2` — dir2 is relative to dir1, not root!
4. Brace expansion `{a,b,c}` in heredoc = literal string
5. Conditional guards that assume file exists (e.g., .gitignore guard only runs if file already present — breaks on fresh repos)

## Scenario 4: Vague Acceptance Criteria

For every feature check AC for:
- "works correctly" — WHAT specifically?
- "configurable" — default value specified?
- "similar to X" — X = specific reference?
- "standard" — standard for whom?

## Scenario 5: Dependency Completeness

For every feature:
1. Search steps for references to other features (F-xxx or equivalent IDs)
2. Search for usage of tables/endpoints from other features
3. All found references present in depends_on?

## Scenario 6: API Contract Mismatch

1. Collect all endpoints from features/requirements
2. Collect all endpoints from architecture/design docs
3. Diff: present in one but missing in the other?

## Scenario 7: Status Enum Drift

For every entity with status/state:
1. Collect all possible values from feature definitions
2. Collect from architecture docs
3. Do they match? Is there a state machine with transitions?

## Scenario 8: CI Pipeline Reality Check

1. Will CI yaml run? Do all images exist?
2. Do env vars in CI match test config defaults?
3. Do test commands match actual file structure?

## Scenario 9: Domain-Specific Edge Cases

Identify the project's domain and check for domain-critical edge cases:

**Finance/Trading:** Atomicity of multi-step operations, race conditions, time-window constraints, partial operation handling, immutability requirements (append-only logs), currency precision and rounding.

**Medical/Health:** Data retention policies, consent tracking, audit trail completeness, anonymization requirements, regulatory compliance references.

**Legal/Compliance:** Version control of documents, approval workflows, access control requirements, retention periods, jurisdiction-specific rules.

**E-commerce:** Inventory consistency, payment failure handling, refund flows, tax calculation edge cases, concurrent purchase conflicts.

If domain is not obvious — skip this scenario.

## Scenario 10: Orphan Writes

For every table/file that a feature CREATES:
- Who READS this data?
- Is there a consumer? Or is it an orphan write?

## Scenario 11: Summary Count Verification

For every summary table (overview lines like "Domain: N tables"):
- Recount N from detailed sections
- Does summary match details?

## Scenario 12: depends_on Cross-Reference Scan

For every feature:
1. Search steps and description for references to other features
2. Search for usage of tables/endpoints/data from other features
3. All found references present in `depends_on`?
4. No circular dependencies? (A depends on B depends on A)

## Scenario 13: Cycle and Cross-Phase Dependency Detection

After any modification to dependency declarations:
1. Build dependency graph from all features
2. Check for cycles (A depends on B depends on C depends on A)
3. Check for cross-phase violations: feature in Phase 0 depends on feature in Phase 1 — unimplementable!
4. Every dependency target must exist and be in the same or earlier phase

## Scenario 14: Ground-truth Graph Integrity

When documentation describes code structure (component registry, API catalog, dependency manifest):

1. Collect ground truth from source files in a single pass (grep imports, scan exports, read configs)
2. Build a ground-truth map keyed by entity name
3. Cross-reference EVERY claim in the document against the map
4. Check bidirectionality: if A.field contains B, verify B.reverseField contains A
5. Check completeness: are there source entities missing from the document?

**Typical traps:**
- Registry lists component X as used by [A, B] but source shows A, B, C use it
- Document says "5 endpoints" but scanning route files reveals 7
- Import graph in docs missing recently added modules

## Scenario 15: Terminology Drift

Across all documents in scope:

1. Build a glossary of key concepts from context
2. Search for synonyms and near-synonyms used for the same concept
3. For each inconsistency: is there a defined canonical term?

**Typical traps:**
- "agent" / "bot" / "worker" / "assistant" used interchangeably
- "endpoint" / "route" / "API" / "path" mixed without consistency
- "module" / "skill" / "plugin" / "extension" drift across documents
- Abbreviations used inconsistently (sometimes "DB", sometimes "database")

## Scenario 16: Dead Reference Detection

For every internal reference in documentation (file paths, links, feature IDs, section refs):

1. Does the target exist?
2. Has it been renamed or moved?
3. Is the content at the target still relevant to the reference context?

**Typical traps:**
- "See docs/GUIDE.md" but file was archived/deleted
- File path referenced but file renamed
- Link to `#section-name` but heading was reworded
- Feature ID referenced in text but removed from features list

## Scenario 17: Temporal Consistency

For all dates, versions, timelines, and sequences across documents:

1. Are dates internally consistent? (created before modified, v1 before v2)
2. Do version numbers follow a coherent progression?
3. Do "current" / "latest" / "now" references match actual state?
4. Are deprecated items marked as such?

**Typical traps:**
- "Updated: 2025-01-15" but references features added in February
- "v2.0" in one doc, "v1.3" in another for the same release
- "Currently using X" but architecture says "migrating to X"
- Roadmap dates in the past with status still "planned"

## Scenario 18: Scope Creep & Coverage Gaps

For each document that declares its scope (intro, purpose statement, table of contents):

1. Does the document actually cover everything it claims?
2. Does it contain material outside its declared scope?
3. Are there sections that promise detail but deliver only stubs?

**Typical traps:**
- "This document covers X, Y, and Z" but Z section is empty
- Architecture doc includes deployment instructions that belong in ops guide
- "See below for API reference" but API section has only "TODO"
- Document title says "Complete Guide" but covers only 3 of 7 subsystems
