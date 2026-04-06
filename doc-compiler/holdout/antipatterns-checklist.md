# Antipatterns Checklist

This file is accessible ONLY to Auditor Agent.

## Document Antipatterns

Check for each antipattern. If found — it's an issue.

| # | Antipattern | How to detect |
|---|-------------|---------------|
| 1 | "Obviously" / "clearly" hiding weak logic | Grep: obviously/clearly/of course — is the claim actually self-evident? |
| 2 | Undefined abbreviations | First use of every abbreviation — is it expanded? |
| 3 | Same fact, different numbers | Every number mentioned 2+ times — do all occurrences match? |
| 4 | Forward reference to nowhere | Every "see below" / "as described in" — does the target exist? |
| 5 | Empty sections in "complete" documents | Grep: TODO/TBD/FIXME/placeholder. Headers with no content below them? |
| 6 | Scope declaration doesn't match content | Introduction claims to cover X, Y, Z — all present and substantive? |
| 7 | Timeline with past dates and future status | Any deadline in the past still marked "planned" or "upcoming"? |
| 8 | Mixed audiences without signposting | Technical and non-technical sections mixed without indicating who each is for? |
| 9 | Conclusion not supported by body | Does the conclusion follow from what was presented? Or does it introduce new claims? |
| 10 | Copy-paste tone shift | Sections that feel like they were written by different people — style, formality, voice? |
| 11 | Pronoun inconsistency | Mix of "we" / "I" / "the team" / "one" without pattern? |
| 12 | Orphan context | Reference to "the meeting" / "the discussion" / "as agreed" without saying which one? |
| 13 | Missing "so what" | Data or findings presented without interpretation or next steps? |
| 14 | Buried lead | Key insight or recommendation hidden deep in the document instead of prominent? |
| 15 | List length inconsistency | "Three priorities" in summary but four in the details (or vice versa)? |
| 16 | Hedging without reason | Excessive "might" / "could" / "potentially" — is there genuine uncertainty or just weak writing? |
| 17 | Circular reasoning | A because B, B because A? Conclusion restates premise as proof? |
| 18 | Undefined "this" / "that" | Vague references — "this approach" / "that issue" — what specifically? |
| 19 | Missing attribution | Claims presented as fact without source — "studies show" / "research indicates" — which studies? |
| 20 | Stale "current" claims | "Currently" / "at present" / "now" — is it actually current? When was this written? |
