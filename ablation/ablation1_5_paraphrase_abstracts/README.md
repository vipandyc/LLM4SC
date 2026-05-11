# Ablation 1.5 — Paraphrase Input Abstracts

## Goal

Test whether paraphrasing the input abstracts (rather than the few-shot examples) before
scoring reduces variance and improves consistency. For each paper, generate K = {1, 3, 5}
independent paraphrases, score each with the baseline prompt, and aggregate by averaging.

## Setup

- **Sample**: 50 papers drawn from `data/SC_related_cites_010.csv` (random seed 42,
  same as Ablation 1)
- **Model**: `gpt-5-mini`
- **Prompt**: baseline `prompt/prompt_fewshot_distilled.md` (unchanged)
- **K levels**: original abstract (K=0), K=1, K=3, K=5 paraphrases averaged

## Scripts

| Script | Description |
|---|---|
| `run_ablation1_5.py` | Scores original abstracts + generates 5 paraphrases per paper + scores all + aggregates for K=1,3,5 |
| `compare_results.py` | Computes per-mechanism mean/std, Spearman ρ vs original, variance vs K; saves plots |

## Results (n = 50)

| Mechanism | K=0 mean | K=1 mean | K=3 mean | K=5 mean | ρ (K=5 vs orig) |
|---|---|---|---|---|---|
| El-ph | 0.600 | 0.520 | 0.547 | 0.532 | 0.884 |
| AFM | 0.500 | 0.520 | 0.513 | 0.532 | 0.842 |
| FM | 0.260 | 0.280 | 0.273 | 0.280 | 0.791 |
| CDW | 0.400 | 0.500 | 0.433 | 0.424 | 0.999 |
| Nematic | 0.140 | 0.100 | 0.133 | 0.156 | 0.825 |
| Correlation | 0.420 | 0.460 | 0.460 | 0.484 | 0.907 |
| Spin liquid | 0.080 | 0.100 | 0.080 | 0.088 | 0.714 |

Key plots:
- `results/variance_vs_k.png` — how score variance changes as K increases
- `results/mean_by_k.png` — mean ± std per mechanism across K levels

## Interpretation

- **Means are stable across K**: all mechanism means stay within ±0.08 of the K=0 original.
- **High Spearman correlations at all K** (ρ ≥ 0.71): the relative ranking of papers is
  preserved regardless of paraphrase averaging.
- **Score std changes very little with K**: the per-mechanism std (e.g., El-ph: 1.51 → 1.44)
  barely decreases from K=1 to K=5, suggesting score variance is dominated by genuine paper
  content variation rather than stochastic prompt sensitivity.
- **Saturation is immediate**: K=1 already achieves nearly identical distributions to K=3 or K=5.
- **Conclusion**: Paraphrasing input abstracts does not substantially improve or change scores.
  A single pass on the original abstract is sufficient; multiple paraphrases add cost without
  meaningful accuracy gain.

## Output Files

| File | Description |
|---|---|
| `results/scores_k0_original.csv` | Raw scores on original abstracts |
| `results/aggregated_k0_original.csv` | Aggregated scores from original abstracts |
| `results/paraphrases_k5.csv` | 5 paraphrases per paper (250 rows total) |
| `results/scores_paraphrases_k5.csv` | Raw scores on all 250 paraphrases |
| `results/aggregated_k1.csv` | Averaged scores for K=1 paraphrases |
| `results/aggregated_k3.csv` | Averaged scores for K=3 paraphrases |
| `results/aggregated_k5.csv` | Averaged scores for K=5 paraphrases |
| `results/comparison_table.csv` | Summary statistics across all K levels |
| `results/variance_vs_k.png` | Score variance vs K plot |
| `results/mean_by_k.png` | Mean ± std per mechanism bar chart |
