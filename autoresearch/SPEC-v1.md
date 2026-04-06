---
document: Autoresearch Skill Specification
version: 1
status: draft
created: 2025-01-15
updated: 2025-01-15
author: community
---

# Autoresearch Skill — SPEC v1

Universal AI-driven research engine. Adapted from [Andrej Karpathy's autoresearch](https://github.com/karpathy/autoresearch) pattern: hypothesis, experiment, analysis, repeat. Optimizes anything with a measurable metric — ML hyperparameters, code performance, prompts, trading strategy parameters, configurations.

---

## 1. Purpose

Replace manual parameter tuning and ad-hoc optimization with an autonomous research loop. The AI Researcher formulates hypotheses based on accumulated evidence, runs experiments, records results with reasoning chains, detects plateaus, and produces a structured report.

### 1.1 Trigger Conditions

The skill activates when a user or agent needs to:
- Optimize parameters of a trading strategy or ML model
- Improve code performance (load time, latency, throughput)
- Tune prompts or system instructions for AI agents
- Find optimal configuration for any module with a measurable metric
- Run overnight autonomous optimization sessions

### 1.2 Non-Goals

- Real-time monitoring or alerting (separate concern)
- Deploying winning configurations to production (manual step)
- Multi-objective optimization with competing metrics (future work)
- Parallel experiment execution (single-threaded by design)

---

## 2. Prerequisites

- **Python 3.10+** installed (for analyzer and report generator scripts)
- **Git repository** initialized in project root (required for code mode; recommended for parameter mode to track reports)
- **Eval command** that exits with code 0 on success and outputs the metric to stdout in the defined format (see section 2.4)
- **For parameter mode:** a parameter space definition (JSON file or inline, see section 2.3)
- **For code mode:** a `program.md` file defining goals and constraints

---

## 3. Two Modes

### 3.1 Parameter Mode

For optimizing numerical parameters without changing code.

**Input:** Eval command + parameter space definition + baseline metric.
**Researcher action:** Generates a JSON dict of parameters for each experiment.
**Experiment:** Skill writes params to a temp JSON file, substitutes its path into eval command, runs command, parses metric from stdout.
**Git:** No git operations on project code. Journal and reports tracked in `.autoresearch/` only.

**Use cases:** ML hyperparameters (learning rate, tree depth, dropout), trading strategy params (threshold, take-profit, stop-loss), configuration values (cache size, timeout, batch size).

**Invocation:**
```
/autoresearch --mode parameter \
  --eval-command "python run_eval.py --params {params_file}" \
  --param-space params_space.json \
  --metric accuracy --direction maximize \
  --baseline 0.82 --max-experiments 50
```

### 3.2 Code Mode (Karpathy-style)

For optimizing code, prompts, or any file content.

**Three-file architecture:**
1. `program.md` — Goal, constraints, rules. Human writes, Researcher cannot modify. Defines what "better" means, what the Researcher can and cannot do, and domain knowledge.
2. **Target file(s)** — The file(s) the Researcher modifies. Can be code (.py, .tsx, .css), prompts (.md), configs (.json, .yaml), or any text file. Multiple files specified as comma-separated list.
3. **Eval command** — Benchmark/test script that outputs the metric. Researcher cannot modify. Prevents cheating.

**Researcher action:** Reads target file(s), formulates a code change hypothesis (one conceptual change per experiment), modifies the file(s) using Edit tool.
**Experiment:** Run eval command, parse metric from stdout.
**Git:** `git commit` on improvement, `git checkout -- <target_files>` on regression or no improvement. History = trail of improvements.

**Use cases:** Website load time optimization, algorithm performance, prompt engineering, CSS/bundle optimization.

**Invocation:**
```
/autoresearch --mode code \
  --program .autoresearch/program.md \
  --target "src/components/Gallery.tsx,src/styles/main.css" \
  --eval-command "npm run benchmark" \
  --metric load_time_ms --direction minimize \
  --baseline 50 --max-experiments 30
```

### 3.3 Parameter Space Definition

For parameter mode, a JSON file defines what the Researcher can tune:

```json
{
  "parameters": {
    "learning_rate": {"type": "float", "min": 0.0001, "max": 0.1, "default": 0.001},
    "batch_size": {"type": "int", "min": 8, "max": 256, "default": 32},
    "dropout": {"type": "float", "min": 0.0, "max": 0.5, "default": 0.1},
    "num_layers": {"type": "int", "min": 1, "max": 8, "default": 3},
    "optimizer": {"type": "enum", "values": ["adam", "sgd", "adamw"], "default": "adam"}
  },
  "constraints": [
    "learning_rate should be tested at log scale first, then refined"
  ]
}
```

If no `--param-space` is provided, the Researcher asks the user to define parameter ranges during interactive setup.

### 3.4 Eval Command Protocol

The eval command MUST output the metric in one of these formats to stdout:

**Format 1 — Single metric (simplest):**
```
METRIC: 2.34
```

**Format 2 — Named metrics (recommended, supports secondary metrics):**
```
METRIC accuracy: 0.934
METRIC f1_score: 0.891
METRIC latency_ms: 42
METRIC loss: 0.187
```

**Format 3 — JSON (for complex outputs):**
```
AUTORESEARCH_RESULT: {"accuracy": 0.934, "f1_score": 0.891, "latency_ms": 42}
```

The primary metric (specified by `--metric`) is used for optimization decisions. All other metrics are recorded in the journal as `all_metrics` for analysis.

**Exit codes:** 0 = success (parse metric), non-zero = failure (record error in journal, skip experiment).

**For parameter mode:** the skill writes the params dict to a temp file at `.autoresearch/sessions/<session-id>/current_params.json` and substitutes `{params_file}` in the eval command with the absolute path to this file. The eval command reads params from this file.

---

## 4. Project Initialization

On first run in any project, the skill creates:

```
<project>/.autoresearch/
  config.json                 # Project defaults
  sessions/                   # One subfolder per research session
```

**config.json schema:**
```json
{
  "project_name": "my-project",
  "default_mode": "parameter",
  "default_eval_command": null,
  "default_metric": null,
  "default_direction": "maximize",
  "default_max_experiments": 50,
  "default_plateau_window": 10
}
```

Each research session creates:
```
.autoresearch/sessions/<session-id>/
  journal.jsonl               # Experiment journal (append-only)
  checkpoint.json             # Resume state
  current_params.json         # Current params (parameter mode, overwritten each experiment)
  program.md                  # Copy of program.md (code mode only)
  report.md                   # Final AUTORESEARCH-REPORT
```

**Session ID format:** `YYYY-MM-DD-HHMM-<mode>-<short-description>` (e.g., `2025-06-15-1400-param-learning-rate-sweep`).

---

## 5. Core Loop

```
Phase 1: Setup
    |
Phase 2: Initialize session
    |
Phase 3: Research loop ─────────────────────┐
    |                                        |
    Researcher.hypothesize()                 |
        → params (parameter mode)            |
        → file changes (code mode)           |
    |                                        |
    ExperimentRunner.run()                   |
        → execute eval command               |
        → parse metric from stdout           |
    |                                        |
    Journal.append(entry)                    |
        → hypothesis + result + analysis     |
    |                                        |
    Analyzer.update()                        |
        → sensitivity, plateau, trends       |
    |                                        |
    Researcher.reflect()                     |
        → update mental model                |
        → decide: continue / stop            |
    |                                        |
    if improvement (code mode):              |
        git commit                           |
    elif regression (code mode):             |
        git checkout -- <target_files>       |
    |                                        |
    if plateau or budget exhausted:          |
        → Phase 4                            |
    else:                                    |
        ────────────────────────────────────┘
    |
Phase 4: Report generation
    |
Phase 5: Learn (update LEARNINGS.md)
```

---

## 6. Journal Format

Each experiment produces one JSONL entry:

```json
{
  "experiment_id": "EXP-0001",
  "session_id": "2025-06-15-1400-param-learning-rate-sweep",
  "timestamp": "2025-06-15T14:15:00Z",
  "hypothesis": "Reducing learning rate from 0.001 to 0.0005 should improve convergence stability, because EXP-0000 showed loss oscillation at higher rates",
  "params": {"learning_rate": 0.0005, "batch_size": 32, "dropout": 0.1},
  "changes_summary": null,
  "git_commit_hash": null,
  "metric_name": "accuracy",
  "metric_value": 0.934,
  "metric_direction": "maximize",
  "baseline_value": 0.82,
  "all_metrics": {"accuracy": 0.934, "f1_score": 0.891, "val_loss": 0.187, "latency_ms": 42},
  "is_improvement": true,
  "is_valid": true,
  "analysis": "Confirmed: lr=0.0005 is a sweet spot. Accuracy improved 14% over baseline with stable convergence.",
  "next_direction": "Explore dropout range [0.15, 0.3] with learning_rate fixed at 0.0005",
  "tags": ["tier1", "lr_sweep", "promising"],
  "timing": {"experiment_sec": 612.5, "researcher_sec": 3.2},
  "error": null
}
```

**Field notes:**
- `params`: always present in parameter mode, null in code mode
- `changes_summary`: always present in code mode (describes what was changed), null in parameter mode
- `git_commit_hash`: set to commit hash when code mode experiment is committed, null otherwise
- `is_valid`: determined by domain-specific validity gates (e.g., min samples >100 for ML evaluation)
- `error`: non-null when eval command fails; in that case, `metric_value` is null

**Journal is append-only.** Failed experiments are recorded too — they inform future hypotheses.

---

## 7. Analyzer

Python script (`scripts/analyzer.py` in the skill directory) performs quantitative analysis without LLM calls.

### 7.1 Parameter Sensitivity

For each parameter, compute mean and std of the primary metric across all values tested. Output as table: parameter, value, mean_metric, std_metric, count.

### 7.2 Plateau Detection

Check if the best metric has improved in the last N experiments (default N = value from config `default_plateau_window`). Returns: `{is_plateau: bool, best_metric: float, experiments_since_improvement: int}`.

### 7.3 Pareto Frontier

Given two metrics (e.g., accuracy vs latency_ms), identify configurations on the Pareto front — those where no other config is better on both metrics simultaneously.

### 7.4 Diminishing Returns

Compute the rate of improvement over sliding windows of size 5. If the improvement rate drops below 1% for 3 consecutive windows, flag diminishing returns.

### 7.5 Invocation

The skill invokes the script using its absolute path:
```bash
python ~/.claude/skills/autoresearch/scripts/analyzer.py <journal_path> [--window 10] [--pareto metric1,metric2]
```

Output: JSON to stdout. The skill reads and interprets the results.

**Error handling:** If the script fails (non-zero exit), the skill logs the error and continues the research loop without analyzer input for that iteration.

---

## 8. Smart Stopping

The research loop stops when ANY of these conditions is met:

| Condition | Default | Configurable |
|-----------|---------|-------------|
| Budget exhausted | 50 experiments | `--max-experiments N` |
| Time budget exhausted | 8 hours | `--max-hours H` |
| Plateau detected | 10 experiments without improvement | `--plateau-window N` |
| Researcher recommends stop | After analysis shows diminishing returns | Always enabled |
| User interrupts | Ctrl+C | Always enabled |
| Consecutive eval failures | 3 failures in a row | Not configurable |

On any stop: checkpoint is saved, report is generated, LEARNINGS updated.

---

## 9. Checkpoint & Resume

**checkpoint.json schema:**
```json
{
  "session_id": "2025-06-15-1400-param-learning-rate-sweep",
  "mode": "parameter",
  "status": "running",
  "completed_experiments": 23,
  "max_experiments": 50,
  "best_experiment_id": "EXP-0015",
  "best_metric_value": 0.961,
  "started_at": "2025-06-15T14:00:00Z",
  "last_checkpoint_at": "2025-06-15T17:30:00Z",
  "eval_command": "python run_eval.py --params {params_file}",
  "metric_name": "accuracy",
  "metric_direction": "maximize",
  "baseline_value": 0.82,
  "param_space_path": "params_space.json",
  "target_files": null,
  "program_md_path": null,
  "git_stash_ref": null
}
```

**Checkpoint frequency:** After every experiment (journal append is atomic; checkpoint updates after successful append).

**Resume:** `/autoresearch --resume [session-id]`. Loads checkpoint + full journal, continues from last experiment. If no session-id provided, resumes the most recent session with `status: "running"`.

---

## 10. Report Generation

Script `scripts/report_generator.py` (in skill directory) produces `AUTORESEARCH-REPORT-YYYY-MM-DD-HHMM.md`.

### 10.1 Report Structure

```markdown
---
type: autoresearch-report
session: <session-id>
mode: parameter | code
metric: <metric_name>
direction: maximize | minimize
baseline: <value>
best: <value>
improvement: <percentage>%
experiments: <total>
valid: <count>
runtime: <hours>h <minutes>m
created: YYYY-MM-DD HH:MM UTC
---

# Autoresearch Report: <session description>

## Summary
- Experiments: N total, M valid, K improvements over baseline
- Best result: <metric>=<value> (+X% over baseline)
- Runtime: Xh Ym
- Stopping reason: plateau / budget / researcher recommendation / eval failures

## Top-5 Configurations
| Rank | Experiment | <metric> | Secondary Metrics | Key Params/Changes | Notes |
|------|-----------|----------|-------------------|-------------------|-------|

## Parameter Sensitivity (parameter mode only)
<table per parameter with mean/std of metric>

## Change Log (code mode only)
<committed changes with experiment IDs and metric deltas>

## Researcher Insights
<Key hypotheses that worked, key hypotheses that failed, patterns discovered>

## Recommendations
<What to try next, what to avoid, suggested follow-up sessions>

## Experiment Log (abbreviated)
<First 5 and last 5 experiments with hypotheses>
```

### 10.2 Report Destination

Written to `--report-to` path if provided, otherwise to `.autoresearch/sessions/<session-id>/report.md`.

### 10.3 Invocation

```bash
python ~/.claude/skills/autoresearch/scripts/report_generator.py <journal_path> [--output path] [--top-n 5]
```

**Error handling:** If report generation fails, the skill writes a minimal summary (best experiment + count) directly instead of crashing.

---

## 11. Researcher Design

The Researcher is Claude (the agent running the skill), reasoning about what to try next within the research loop.

### 11.1 Model Selection

- **Default:** Use the model powering the current Claude Code session (inherited)
- **For long sessions (>20 experiments):** The skill does not spawn separate Researcher agents. Claude itself is the Researcher — it formulates hypotheses, runs experiments, and analyzes results in a single continuous session. This avoids context loss between experiments.

### 11.2 System Context (included in every hypothesis step)

- Mode (parameter or code)
- Parameter space definition (parameter mode) or program.md content (code mode)
- Primary metric name, direction, baseline
- Antipatterns from holdout (see section 16)

### 11.3 Session Context (grows with experiments)

- Full journal for sessions with fewer than 50 experiments
- For sessions with 50+ experiments: summary of top-5 results + last-10 experiments + analyzer sensitivity table
- Analyzer output (plateau status, sensitivity, Pareto if applicable)

### 11.4 Output Format

**Parameter mode:** The Researcher outputs:
1. `hypothesis` — natural language explanation of why these params
2. `params` — JSON dict matching the parameter space schema
3. `tags` — categorization (e.g., "threshold_sweep", "exploit", "explore")

**Code mode:** The Researcher:
1. States `hypothesis` — what change and why
2. States `changes_plan` — what files will be modified and how (one-sentence per file)
3. Makes the actual edits using Edit tool (one conceptual change per experiment)

### 11.5 Key Instructions for Researcher

- Always explain WHY you chose these specific values (not "random exploration")
- Reference prior experiments by ID when explaining reasoning
- Distinguish explore (new region) vs exploit (refine known good region)
- After 3 experiments in same region without improvement, switch to exploration
- Never repeat exact same parameters — check journal before proposing
- For parameter mode: respect parameter ranges from param-space definition
- For code mode: make one conceptual change per experiment (atomic, testable)
- For code mode: if a change breaks compilation/tests (eval returns non-zero), revert and try a different approach

---

## 12. Git Integration

### 12.1 Code Mode

**Before starting session:** `git stash` any uncommitted changes if working tree is dirty. Save stash ref to checkpoint. Warn user that uncommitted changes were stashed.

**Each experiment:**
1. Researcher modifies target file(s) using Edit tool
2. Run eval command
3. If metric improves over current best: `git add <target_files> && git commit -m "autoresearch(EXP-NNNN): <hypothesis_short>"`
4. If metric regresses or stays same: `git checkout -- <target_files>`

**After session completes:** If git stash was used, run `git stash pop` to restore user's uncommitted changes. If stash pop conflicts, warn user and leave stash intact.

**Result:** Git history = chain of improvements. Regressions are reverted. Clean history.

### 12.2 Parameter Mode

No git operations on project code. Journal and reports live in `.autoresearch/` and are not auto-committed.

### 12.3 Skill Self-Update

When LEARNINGS.md is updated, commit to skills repo:
```bash
cd ~/.claude/skills && git add autoresearch/ && git commit -m "autoresearch: update learnings (L-NNN)" && git push
```

---

## 13. Workflow Phases

### Phase 1: Setup

**Interactive mode** (`/autoresearch` without args):
1. Check if `.autoresearch/` exists; create if not (see section 4)
2. Ask: "What do you want to optimize?" — detect mode from answer
3. If parameter mode:
   - Ask for eval command (or use default from config.json)
   - Ask for parameter space definition (file path or define interactively)
   - Ask for metric name, direction (maximize/minimize), baseline value
4. If code mode:
   - Ask for target file(s)
   - Ask for eval command
   - Ask for metric name, direction, baseline
   - Create or review program.md together with user
5. Ask for budget (max experiments and/or max hours)
6. **Validate before starting:** run eval command once with default/baseline params to confirm it works and metric is parseable. If validation fails, show error and ask user to fix eval command.
7. Confirm all settings and start

**Programmatic mode** (with args): Validate all required args are present, run baseline eval validation, then start. Missing required args cause an error with clear message.

**Required args (parameter mode):** `--mode`, `--eval-command`, `--metric`, `--direction`, `--baseline`
**Required args (code mode):** `--mode`, `--eval-command`, `--target`, `--metric`, `--direction`, `--baseline`
**Optional args (both):** `--max-experiments` (default: 50), `--max-hours` (default: 8), `--plateau-window` (default: 10), `--report-to`, `--param-space` (parameter mode), `--program` (code mode)

### Phase 2: Initialize Session

1. Generate session ID from current timestamp + mode + user-provided description
2. Create session directory under `.autoresearch/sessions/`
3. Load prior sessions' journals from same project (read-only context for Researcher)
4. Load LEARNINGS.md and holdout files from skill directory
5. Run baseline eval to establish starting metric value (already validated in Phase 1)
6. Save initial checkpoint with status "running"
7. For code mode: `git stash` uncommitted changes if dirty, save stash ref to checkpoint

### Phase 3: Research Loop

For each experiment (up to max_experiments or stopping condition):

1. **Hypothesize:** Researcher reviews journal + analyzer output, formulates hypothesis, selects params (parameter mode) or plans code changes (code mode)
2. **Execute:**
   - Parameter mode: write params to `current_params.json`, substitute `{params_file}` in eval command, run command
   - Code mode: apply planned edits to target files, run eval command
3. **Parse:** Extract metric from stdout per eval command protocol (section 2.4). If parsing fails, record error and count as eval failure.
4. **Record:** Create journal entry with hypothesis + result + analysis. Append to journal.jsonl.
5. **Checkpoint:** Update checkpoint.json (completed count, best experiment if new best).
6. **Analyze:** Run `scripts/analyzer.py` on journal — get plateau status, sensitivity data.
7. **Git** (code mode only): commit if improvement, revert if regression/same.
8. **Decide:** Check stopping conditions (section 8). If any triggered, proceed to Phase 4. Otherwise, continue loop.

**Error handling:**
- Eval command returns non-zero: record error in journal (`error` field), increment consecutive failure counter. If 3 consecutive failures, pause and ask user.
- Eval command times out (>30 minutes for a single experiment): kill process, record timeout error. Count as failure.
- Metric parsing fails: record parsing error. Count as failure.
- Analyzer script fails: log warning, continue without analyzer data for this iteration.
- Code mode: if eval fails after file modification, always revert files before next experiment.

### Phase 4: Report Generation

1. Run `scripts/report_generator.py` on journal.jsonl
2. Write report to destination (--report-to or session directory)
3. Update checkpoint status to "completed"
4. Print summary to user: best result, improvement %, total experiments, runtime, stopping reason

### Phase 5: Learn

1. Review the session: what patterns emerged? What worked? What was surprising?
2. If a new operational insight is found: append to LEARNINGS.md with next L-NNN number
3. If a pattern appeared in 2+ sessions: promote to holdout file (research-procedures.md or antipatterns.md)
4. Commit LEARNINGS.md update to skills git repo (section 12.3)
5. For code mode: `git stash pop` to restore user's uncommitted changes (if stash was used)
6. Print: `=== Autoresearch: SESSION COMPLETE ===`

---

## 14. Lead Agent Rules

When the skill runs autonomously (overnight, long sessions), these rules govern behavior:

### Role boundaries
- The Researcher formulates hypotheses and modifies target files (code mode only). It does NOT modify the eval command, program.md, or the skill itself during a session.
- The skill orchestration (setup, checkpoint, git operations, report generation) is handled by the skill instructions, not by the Researcher's judgment.

### Autonomous flow
- After each experiment, IMMEDIATELY proceed to the next. No pauses for user input during the research loop.
- Only stop for user input at: Phase 1 setup, Phase 3 error handling (3 consecutive failures), and Phase 4 report delivery.

### Health checks
- If an eval command has not completed in 30 minutes, kill the process and record a timeout.
- If the research loop has made no progress (0 valid experiments) after 10 experiments, pause and ask user if eval command is correct.

### Communication
- Print a one-line status after every experiment: `[EXP-NNNN] metric=X.XX (best=Y.YY) | hypothesis: <short> | <improved/no change/regression>`
- Print a summary every 10 experiments: experiments completed, best so far, plateau status.
- On completion: print full summary with improvement stats.

### Timestamp logging
Print at START and DONE of major phases:
```
=== Autoresearch: [Phase Name] START [YYYY-MM-DD HH:MM:SS] ===
=== Autoresearch: [Phase Name] DONE [YYYY-MM-DD HH:MM:SS] — [duration] — [summary] ===
```

---

## 15. Severity Definitions

For classifying experiment results and operational events:

| Severity | Definition | Example |
|----------|-----------|---------|
| improvement | Metric improved over current best | Accuracy went from 0.91 to 0.95 |
| valid | Metric did not improve but experiment passed validity gates | Accuracy=0.88, samples=500 — valid but not best |
| invalid | Experiment failed validity gates | Accuracy=0.99 (suspiciously high), samples=3 (too few) |
| error | Eval command failed or metric could not be parsed | Non-zero exit code, timeout, parse failure |

**Validity gates** are domain-specific and defined in the parameter space or program.md. Common examples:
- Minimum sample size (e.g., eval_samples > 100)
- Metric range sanity check (e.g., accuracy < 1.0 — perfect scores indicate data leakage)
- Secondary metric floor (e.g., f1_score > 0.50)

---

## 16. Holdout Files

### 16.1 research-procedures.md

Concrete procedures the Researcher follows:

- **Hypothesis formulation:** Must reference prior evidence. "I think X because EXP-Y showed Z."
- **Explore vs exploit decision tree:**
  - First 5 experiments: broad exploration (cover different regions of parameter space)
  - After finding a promising region: 3-5 experiments to refine
  - After 3 refinements without improvement: switch back to exploration
  - When analyzer flags diminishing returns: explore a completely new dimension
- **Parameter interaction awareness:** Some params interact (e.g., learning rate + batch size in ML training). Test individual params first, then test interactions of the top values.
- **Validation rigor:** Primary metric alone is insufficient. Always check secondary metrics (sample size, robustness, consistency across sub-periods).
- **Cross-session learning:** When starting a new session, read prior session journals and summarize key findings before first hypothesis.

### 16.2 antipatterns.md

Common optimization traps to avoid:

- **AP-01: Metric gaming.** Optimizing the primary metric by degrading important secondary metrics. Example: high accuracy by evaluating on only 5 samples (no statistical significance), or fast load time by removing critical functionality.
- **AP-02: Overfitting to eval period.** Results on one time period may not generalize. Note the eval period in the report. If possible, suggest cross-validation across multiple periods.
- **AP-03: Ignoring robustness.** A configuration that works perfectly under nominal conditions but fails with slightly different inputs is fragile. Always note sensitivity.
- **AP-04: Single-lever optimization.** If only one parameter changes across all experiments, the search is not exploring the full space. After the initial sweep of one parameter, deliberately vary others.
- **AP-05: Repeating failed hypotheses.** Check journal before proposing — do not retry parameters that already failed unless combined with a different change.
- **AP-06: Premature stopping.** Don't stop after the first improvement. The plateau window (default 10 experiments) exists for a reason — early improvements are often not the best.
- **AP-07: Code mode — large changes.** One conceptual change per experiment. Large refactors make it impossible to attribute improvement to a specific change.
- **AP-08: Wrong metric direction.** Double-check at session start: minimize latency, maximize accuracy. Getting direction wrong wastes the entire session. The skill validates this in Phase 1.

---

## 17. LEARNINGS.md

Follows the pattern from spec-compiler/impl-auditor skills.

**Location:** `~/.claude/skills/autoresearch/LEARNINGS.md`

**Entry format:**
```markdown
### L-NNN: Short title
**Status:** ACTIVE | RESOLVED | NOTED | MATERIALIZED
**Source:** session-id or general observation
**Finding:** What was discovered
**Impact:** How this affects future research sessions
**Action:** What to do about it (add to holdout, change default, etc.)
```

**Statuses:**
| Status | Meaning |
|--------|---------|
| ACTIVE | Under investigation, not yet resolved |
| RESOLVED | Fixed by skill update or holdout change |
| NOTED | Recorded as operational insight, no change needed |
| MATERIALIZED | Implemented in holdout, archived |

**Auto-promotion rule:** When a pattern appears in 2+ sessions, create or update a holdout procedure. Mark the learning as MATERIALIZED and move to Archived section.

---

## 18. Agent Interaction

### 18.1 Who Can Invoke

- **User directly:** `/autoresearch` or `/autoresearch --mode ...`
- **Any coordinator agent:** Via Agent tool with full args

### 18.2 Invocation from Agent

```
Agent tool prompt: "Run /autoresearch --mode parameter
  --eval-command 'python run_eval.py --params {params_file}'
  --param-space config/param_space.json
  --metric accuracy --direction maximize --baseline 0.82
  --max-experiments 50 --max-hours 8
  --report-to reports/optimization/"
```

### 18.3 When to Suggest Running

Agents should suggest autoresearch when:
- A module has a benchmark but performance is below target
- The user asks to "optimize", "tune", "improve" something measurable
- A model has a working pipeline but suboptimal metrics

Agents should ask the user about timing before launching:
- "Autoresearch for 50 experiments will take ~8 hours. Run now or schedule for tonight?"
- Suggest off-peak hours for long sessions

### 18.4 Return Value

When autoresearch completes, it outputs:
- One-line summary: best metric value, improvement %, experiment count
- Path to the full report file
- The best parameter configuration (parameter mode) or the git log of committed improvements (code mode)

---

## 19. File Inventory

### 19.1 Global Skill Files (in ~/.claude/skills/autoresearch/)

| File | Purpose |
|------|---------|
| SKILL.md | Main skill instructions |
| SPEC-v1.md | This specification |
| LEARNINGS.md | Self-improvement journal |
| holdout/research-procedures.md | Researcher procedures and decision trees |
| holdout/antipatterns.md | Optimization traps to avoid |
| scripts/analyzer.py | Quantitative analysis (sensitivity, plateau, Pareto) |
| scripts/report_generator.py | Markdown report generation |

### 19.2 Project-Local Files (created on first run)

| File | Purpose |
|------|---------|
| .autoresearch/config.json | Project defaults |
| .autoresearch/sessions/*/journal.jsonl | Experiment journal (append-only) |
| .autoresearch/sessions/*/checkpoint.json | Resume state |
| .autoresearch/sessions/*/current_params.json | Current experiment params (parameter mode) |
| .autoresearch/sessions/*/program.md | Goal & constraints (code mode) |
| .autoresearch/sessions/*/report.md | Session report |
