# Autoresearch — Antipatterns

Common optimization traps to avoid. Read at the start of every session.

## AP-01: Metric Gaming

Optimizing the primary metric by degrading important secondary metrics.

**Examples:**
- High accuracy by evaluating on only 5 samples (no statistical significance)
- Fast page load by removing critical functionality
- Low error rate by rejecting all edge cases

**Prevention:** Always check secondary metrics. If validity gates are defined in the parameter space, enforce them. If not, use common sense: results with extreme primary metrics and poor secondary metrics are suspicious.

## AP-02: Overfitting to Eval Period

Results on one specific time period, dataset, or test case may not generalize.

**Prevention:** Note the eval period/dataset in the journal and report. If possible, suggest cross-validation across multiple periods. Flag in the report if all experiments were evaluated on the same narrow dataset.

## AP-03: Ignoring Robustness

A configuration that works perfectly under nominal conditions but fails with slightly different inputs is fragile.

**Prevention:** Check metric sensitivity to small parameter perturbations. If a 1% change in a parameter causes a 50% metric change, the configuration is on a knife edge. Note robustness in the report.

## AP-04: Single-Lever Optimization

If only one parameter changes across all experiments, the search is not exploring the full space.

**Prevention:** After the initial sweep of one parameter, deliberately vary others. Track which parameters have been explored in tags. After 10 experiments, check: are multiple parameters represented?

## AP-05: Repeating Failed Hypotheses

Testing the same parameters or code changes that already failed.

**Prevention:** Before every hypothesis, scan the journal for similar experiments. If exact params were tried, do NOT repeat. If similar params were tried and failed, explain why this variation is different.

## AP-06: Premature Stopping

Stopping after the first improvement, before exploring whether better configurations exist.

**Prevention:** The plateau window (default 10 experiments) exists for this reason. Respect it. Early improvements are often local optima — there may be better configurations in unexplored regions.

## AP-07: Code Mode — Large Changes

Making multiple conceptual changes in a single experiment.

**Example:** "Replaced the sort algorithm AND added lazy loading AND minified CSS" — if the metric improves, which change caused it?

**Prevention:** One conceptual change per experiment. If the change is large, break it into smaller experiments. Each experiment should test a single hypothesis.

## AP-08: Wrong Metric Direction

Maximizing when you should minimize, or vice versa.

**Example:** Maximizing load_time_ms (making the site slower) instead of minimizing it.

**Prevention:** The skill validates metric direction in Phase 1. But double-check: does the first experiment's result make sense given the direction? If metric goes from 50ms to 200ms and is recorded as "improvement" with direction=maximize — something is wrong.
