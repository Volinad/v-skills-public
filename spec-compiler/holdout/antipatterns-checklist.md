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
| 26 | Dates that contradict the timeline | "Updated" date before content additions? "Current" claims match actual state? For snapshot/status docs that self-certify VCS/filesystem state: verify release/version dates against `git log`/tag timestamps, NOT the prose narrative — authors inherit wrong dates from the session narrative they were reading. Common trap: doc dates a release two days off from the release commit's actual timestamp. See L-047. |
| 27 | Scope declaration doesn't match content | Intro claims "covers X, Y, Z" — all sections present and non-empty? |
| 28 | "TODO" / "TBD" / empty sections in "complete" docs | Grep for TODO/TBD/FIXME/placeholder. Stub sections in ready documents? |
| 29 | OR/AND ambiguity in skip/guard conditions | Multi-criteria conditions using natural language "or"/"and" — rewrite with explicit quantifiers (NONE/ALL/ANY). "Skip if no X, Y, or Z" is ambiguous: does it mean skip if ANY is absent, or skip if ALL are absent? |
| 30 | Writer fix boundary contamination | After Writer edits, check: (a) do adjacent sections/tables that reference the same concept still agree? (b) did the fix update ALL locations where the concept appears, or only the primary one? (c) does any newly added text contain mathematical or logical claims -- verify them independently. Common trap: Writer adds a corrective note in one section but a summary table three sections away still describes the old behavior. |
| 31 | Claimed arithmetic equality without verification | Grep: "equals", "derived from", "computed as", "same as" near numbers. For each: independently verify the arithmetic. Common trap: "the gap parameter equals the maximum lookback window" but one is 20 days and the other is 30. Also: RAM estimates citing type sizes that don't match actual struct definitions (see L-029). |
| 32 | Attribution to a named source that diverges | Grep: "aligned with", "matches", "per `", "same boundary/window/value as", "from `<symbol>`". For each, OPEN the named source symbol and verify it exists AND the quoted value lives in THAT symbol (not a sibling). Code comments repeating the claim are NOT independent confirmation. Common trap: "aligned with `session_config` (window 08:00–20:00)" but `session_config`'s boundary is 06:00 and the 08:00 window belongs to a sibling function (`gateway.is_active_window`). See Scenario 19, L-043. |
| 33 | Reproduced union/enum type block omits a member used elsewhere | When a doc reproduces a discriminated union / enum / sum type, count its members against (a) the source type definition and (b) every place the doc's own matrix/prose/table references members. A member used downstream but missing from the block is a CRITICAL omission. Caught by M9 (interface contract) + M12 (contradiction) + M14 (ground-truth) converging. Common trap: a `Strategy` union block lists 5 arms but the decision matrix uses a 6th (`fallback`) that the source type has. See L-044. |
| 34 | Auditor finding quotes text absent from the audited document (ambient-context fabrication) | Under heavy ambient project context (a large surrounding narrative / cumulative CLAUDE.md that mentions related values), a consistency-lens auditor can flag or quote document text that does NOT exist in the file — reconstructed from memory, not read from disk. RULE: every finding must quote the EXACT line text WITH line number; before acting, grep the quoted string in the audited file. If it is not grep-found, the finding is a false positive — discard it. Also applies to evidence-table values in a clean countdown round (transcription slips: a path/name written from memory while the verified values matched the real one). This is why the gate requires 2 consecutive clean rounds with DIFFERENT models — one model's evidence table is not self-trustworthy. Distinct from #32 (false attribution to a real source — value exists, wrong symbol) and #30 (Writer fix contamination — different actor). Common trap: auditor flags a line-count claim about a file that appears nowhere in either doc; or claims a present-verbatim qualifier is "missing." See L-046. |
