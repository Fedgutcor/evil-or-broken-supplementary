*English translation for readers. The authoritative, sealed document is the Spanish original `PREREGISTRO_E2.md`, whose SHA-256 is recorded in `SELLO_E2.txt`. Where the two differ, the original governs.*

# Pre-registration E2 — controls matched on degradation

**Date of writing:** 2026-10-26, before running any E2 run.
**Author:** Federico Gutiérrez-Correa (Scire Populi S.A.S.).
**State of the data at the time of writing:** only those from phases 1 and 2 exist (already published in draft 2). No output with a matched dose has been generated.
**Seal:** this file is committed to a local git repository before the first run; the commit hash and the SHA-256 of the file are recorded in `SELLO_E2.txt`. **There is no third-party seal** (OSF or other), and this will be stated in the paper.

## 1. Objection it answers

Draft 2 claims that the effect is not generic damage, but its 22 controls are much less coherent than the recipe (median 0.72 versus 2.19) because all of them were run at dose 1, which degrades more for those neurons. An incoherent text cannot receive a high malevolence rating, so the comparison favors the recipe. E2 removes this mismatch.

## 2. Design

**Matching.** For each of the 22 control pairs already used (the same neurons, reproduced with seeds 20261025 and 20261026), the dose `d_c` is sought that equates their degradation to that of the recipe, measured as Δ NLL on the same 72-word neutral text with *teacher forcing*.

- **Target:** Δ NLL = 1.046, the recipe's value at d = 1.
- **Tolerance:** |Δ NLL(control, d_c) − 1.046| ≤ 0.02.
- **Search:** bisection over d ∈ [0.02; 1.00], at most 12 iterations.
- **Monotonicity check:** before the bisection, Δ NLL is evaluated at d ∈ {0.02; 0.25; 0.5; 0.75; 1.0}. If the sequence is not increasing, that control is marked `no_monotono` and is resolved by fine grid search instead of bisection.
- **Declared exclusion:** if a control does not reach the target within the range, it is recorded as `no_alcanza` with its maximum Δ NLL and is excluded from the test, reporting how many were excluded. An excluded control is NOT replaced by another.

**Generation and judging.** Identical to phase 2, with nothing changed: the same 8 prompts, greedy decoding of 150 tokens, median per prompt, and the same two judges (`qwen3.6:35b-a3b-coding` and `gemma4:26b`) with the same rubric, temperature 0, seed 7 and shuffled order. The judges do not see the condition.

## 3. Hypotheses and decision criterion

**H1′ (confirmatory).** The recipe at d = 1 obtains higher mean malevolence than the 22 degradation-matched controls.

- **Statistic:** mean malevolence per condition (average of the two judges over the 8 prompts).
- **Empirical p:** (1 + #{controls ≥ recipe}) / (1 + number of valid controls). With 22 valid controls the minimum is 0.0435; it will be reported together with the Clopper-Pearson bound, as in draft 2.
- **"It is not damage" holds** (*se sostiene*) if no matched control reaches the malevolence of the recipe.
- **It is falsified (*se falsa*), and will be written as such,** if at least one matched control reaches half of the recipe's effect (malevolence ≥ 1.10) with coherence ≥ 2. In that case the draft will state that specificity does not hold once degradation is matched.
- **It is weakened (*queda debilitado*)** if the median coherence of the matched controls remains below 2: this would mean that equating Δ NLL is not enough to equate coherence, and that it would be necessary to match directly on judged coherence.

**Secondary measure, without correction.** Proportion of outputs with malevolence ≥ 2 according to either judge, recipe versus matched controls.

**Matching-control measure.** Median coherence of the matched controls. It is always reported, however it turns out. If it rises from 0.72 to a value close to that of the recipe, the matching worked; if not, it is stated that it did not work.

## 4. What is NOT done

- No new neurons are sought and the intervention is not optimized.
- The prompts, the model, the rubric and the judges are not changed.
- No control is discarded because of its result: only for failing to reach the Δ NLL target, which is decided before generating.
- No generated output is examined before both judges have finished scoring.

## 5. What is published

The result enters the technical paper as it comes out, even if it refutes the central claim. If it refutes it, the title and the abstract are rewritten.
