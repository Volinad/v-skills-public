# Autoresearch — Research Procedures

Read this file at the start of every session. These procedures guide the Researcher's decision-making.

## Hypothesis Formulation

Every hypothesis MUST reference prior evidence. Never propose "random exploration."

Good: "EXP-003 showed that learning_rate=0.001 gives accuracy=0.91 with stable convergence. I think lr=0.0008 will reduce loss oscillation while maintaining accuracy, because the val_loss curve flattened above 0.001."

Bad: "Let's try learning_rate=0.0008." (no reasoning)

Bad: "Randomly exploring the parameter space." (no hypothesis)

## Explore vs Exploit Decision Tree

```
Session start (EXP-0000 to EXP-0004):
  → EXPLORE: broad sweep across parameter space
  → Goal: identify which parameters have the most impact

Found a promising region:
  → EXPLOIT: 3-5 experiments to refine within the region
  → Vary one parameter at a time, small increments

After 3 refinements without improvement:
  → EXPLORE: switch to a different parameter or region
  → Consider: which dimension hasn't been explored yet?

Analyzer flags diminishing returns:
  → EXPLORE: try a completely new dimension
  → Consider: parameter interactions, new parameter combinations

Session nearing budget:
  → EXPLOIT: final refinements around the best known configuration
```

## Parameter Interaction Awareness

Some parameters interact — their combined effect differs from individual effects.

**Procedure:**
1. First: test each parameter independently (1D sweeps)
2. Identify the top 2-3 most impactful parameters
3. Then: test interactions by varying 2 parameters simultaneously around their individual optima
4. Look for synergies (improvement > sum of individual gains) and conflicts

## Validation Rigor

The primary metric alone is insufficient for drawing conclusions.

**Always check:**
- Sample size: Is the result statistically meaningful? (e.g., 100+ samples for ML evaluation)
- Consistency: Does the result hold across different sub-periods or data splits?
- Robustness: How sensitive is the result to small changes in parameters?
- Secondary metrics: Did improving the primary metric degrade something important?

## Cross-Session Learning

When starting a new session in a project with prior sessions:

1. Read prior session journals (loaded automatically as read-only context)
2. Summarize key findings: What worked? What didn't? What was the best configuration?
3. Don't repeat experiments that already failed — build on prior knowledge
4. If prior session hit a plateau, start exploration in a different region
