# Holdout Validation Scenarios

This file is accessible ONLY to Auditor Agent. Writer Agent MUST NOT see it.

## Principle

Holdout scenarios are analogous to holdout sets in ML. The Writer doesn't know what specific checks Auditor will run, so it cannot optimize for them.

---

## Scenario 1: Number & Fact Integrity

For every number, date, name, or factual claim in the document:
1. Find all places where this fact is mentioned
2. Do all occurrences match?
3. Can the fact be verified from context or common knowledge?

**Typical traps:**
- "Team of 5 people" in one section, "our 6-person team" in another
- Revenue figure differs between executive summary and details
- Person's title changes between mentions

## Scenario 2: Promise vs Delivery

Check every forward reference and promise in the document:
1. "As described below..." — is it actually described below?
2. "See Section X..." — does Section X exist and cover what's promised?
3. Table of contents entries — do all listed sections exist?

**Typical traps:**
- Introduction promises "three key findings" but body has four (or two)
- "We will discuss X later" but X never appears
- Appendix referenced but missing

## Scenario 3: Logical Argument Integrity

For documents that make arguments or proposals:
1. Does each conclusion follow from its premises?
2. Are there logical gaps where the reader must infer a missing step?
3. Are counter-arguments acknowledged or silently ignored?

**Typical traps:**
- "Because A is true, we should do C" — but the connection between A and C is unexplained
- Data presented selectively to support a predetermined conclusion
- "Obviously" or "clearly" used to skip over non-obvious reasoning

## Scenario 4: Audience Mismatch

1. Who is the intended reader? (stated or implied)
2. Would that reader understand all terms used?
3. Is the level of detail appropriate?

**Typical traps:**
- Executive summary full of technical acronyms
- Document for external stakeholders using internal jargon
- Overly simplified for an expert audience (insulting)
- Mixing audiences (some sections for executives, others for engineers)

## Scenario 5: Temporal Drift

For all dates, timelines, and time-relative claims:
1. "Current" / "now" / "today" — still accurate?
2. Deadlines in the past with status still "planned" or "upcoming"
3. "Recently" without a date — when?

**Typical traps:**
- "Q1 2025 launch" but it's Q1 2026 and no update
- "Our latest research shows..." but the research is 2 years old
- Meeting notes say "next week we'll..." but no follow-up recorded

## Scenario 6: Terminology Drift

Across all documents in scope:
1. Build a glossary of key terms from context
2. Are the same concepts called different things in different places?
3. Are abbreviations introduced before use?

**Typical traps:**
- "Project Alpha" / "the Alpha initiative" / "our main project" — same thing?
- Abbreviation used without ever being defined
- Same abbreviation means different things in different documents

## Scenario 7: Scope Creep & Missing Pieces

For documents with declared purpose or scope:
1. Does it cover everything it claims?
2. Does it contain material outside its scope?
3. Are there sections with only headers and no content?

**Typical traps:**
- "This plan covers marketing, sales, and operations" but operations section is empty
- A project proposal that spends 3 pages on background and 1 paragraph on the actual proposal
- TODO/TBD markers in what's presented as a finished document

## Scenario 8: Tone Shifts

Read the document as a continuous piece:
1. Does the tone shift unexpectedly between sections?
2. Are there sections that feel like they were written by a different person?
3. Is the formality level consistent?

**Typical traps:**
- Formal executive summary followed by casual bullet points
- Copy-pasted sections from other documents with different voice
- Mix of "we" and "I" and "the team"

## Scenario 9: Dead References

For every reference to external resources:
1. Links — do they work?
2. People — are they still in the roles mentioned?
3. Projects — do they still exist under that name?
4. Documents — are they still current?

**Typical traps:**
- Link to a Google Doc that's been deleted or moved
- "Contact John in Marketing" but John moved to Sales
- Reference to a project that was renamed or cancelled

## Scenario 10: Implicit Assumptions

Look for claims that assume the reader knows something unstated:
1. Are there jumps in logic that require background knowledge?
2. Are there unstated dependencies between sections?
3. Would a reader outside the immediate context understand this?

**Typical traps:**
- "Given the Q3 results, we need to pivot" — Q3 results never stated
- Plan assumes a specific budget without stating it
- Decision rationale references a conversation not documented
