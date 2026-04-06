# Antipatterns Checklist

This file is accessible ONLY to Auditor Agent.

## Documentation Antipatterns

Check for each antipattern. If found — it's an issue.

| # | Antipattern | How to detect |
|---|-------------|---------------|
| 1 | "Configurable" without default | Grep: configur — is there a default nearby? |
| 2 | "Similar to X" or "Same as X" without verification | Grep: similar/like/same as — is there a specific ID or link? For identity claims ("same as"), verify the thing IS actually identical, not just similar. Common trap: "Same evidence protocol as spec-compiler" when fields differ. |
| 3 | Schedule without timezone | Grep: time/schedule/cron — is there a timezone? |
| 4 | Integration without error handling | Every external API call has error section? |
| 5 | P0 UI feature without layout description | P0 features with pages — is structure described? |
| 6 | Everything in one instruction file | Main instruction file < 80 lines? Details in separate files? |
| 7 | All features in one file | Separate files by phases or domains? |
| 8 | AC "works well/correctly" | Every AC testable by specific test? |
| 9 | Same data in 3+ places without source of truth | Source of truth defined? Auto-verification? |
| 10 | CI yaml not verified by execution tracing | All lines mentally executed? |
| 11 | Crypto keys = stubs | Keys valid format? Test values working? |
| 12 | Setup script without idempotency | Every operation with guard (if [ ! -f ... ])? |
| 13 | Transitive dependency for calls | A calls B — depends_on, not just reading |
| 14 | Summary table without auto-verification | Summary counts match details? |
| 15 | "N domains" without definition | What counts? Routers? Sections? URL prefixes? |
| 16 | CI and test config linked by implicit convention | Documented coupling between CI steps and test configuration? |
| 17 | Brace expansion in scripts | Explicit mkdir instead of {a,b,c}? |
| 18 | Regex [A-Z_]+ for names with digits | [A-Z][A-Z0-9_]* instead of [A-Z_]+? |
| 19 | "18 methods clean" with shallow checks | Self-audit: what was really checked? Depth assessment honest? |
| 20 | Writer-reported counts without independent verification | After Writer adds/removes items, Lead recounts independently? |
| 21 | Generated config files with secrets not in .gitignore | Setup-generated files with hardcoded passwords — in .gitignore? |
| 22 | depends_on pointing to later phase | Feature in Phase 0 depends on Phase 1 feature? Unimplementable! |
| 23 | Doc claims about code without ground-truth verification | Registry/manifest claims cross-checked against source files? Bidirectional check done? |
| 24 | Same concept, different names across documents | Grep for synonyms: agent/bot/worker, endpoint/route/path. Canonical term defined? |
| 25 | References to moved/deleted/renamed files | Every internal file path, link, section ref resolves to existing target? |
| 26 | Dates that contradict the timeline | "Updated" date before content additions? "Current" claims match actual state? |
| 27 | Scope declaration doesn't match content | Intro claims "covers X, Y, Z" — all sections present and non-empty? |
| 28 | "TODO" / "TBD" / empty sections in "complete" docs | Grep for TODO/TBD/FIXME/placeholder. Stub sections in ready documents? |
| 29 | OR/AND ambiguity in skip/guard conditions | Multi-criteria conditions using natural language "or"/"and" — rewrite with explicit quantifiers (NONE/ALL/ANY). "Skip if no X, Y, or Z" is ambiguous: does it mean skip if ANY is absent, or skip if ALL are absent? |
