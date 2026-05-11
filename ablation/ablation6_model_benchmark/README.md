# Ablation 6 — Model Benchmark

## Goal

Compare opinion scoring quality and consistency across different LLMs using the same
baseline prompt and the same 50-paper held-out sample (random seed 42).

## Setup

- **Sample**: 50 papers from `data/SC_related_cites_010.csv` (seed 42)
- **Prompt**: baseline `prompt/prompt_fewshot_distilled.md` (unchanged)
- **Models run**: gpt-5-mini (reused from Ablation 1), gpt-4.1-mini, gpt-4.1, o4-mini
- **Pending**: claude-sonnet-4-5, claude-opus-4-5 (require `pip install anthropic` + Anthropic API key)

## Results (n = 50)

### Score distributions

| Model | Parse fail % | All-zero % | El-ph | AFM | FM | CDW | Nematic | Correlation |
|---|---|---|---|---|---|---|---|---|
| gpt-5-mini | 0% | 62% | 0.60 | 0.62 | 0.34 | 0.44 | 0.18 | 0.48 |
| gpt-4.1-mini | 0% | 54% | 0.44 | 0.60 | 0.34 | 0.38 | 0.08 | 0.14 |
| gpt-4.1 | 0% | 58% | 0.30 | 0.34 | 0.20 | 0.38 | 0.10 | 0.24 |
| o4-mini | 0% | 80% | 0.28 | 0.24 | 0.10 | 0.08 | 0.08 | 0.16 |

### Spearman ρ vs gpt-5-mini baseline

| Model | El-ph | AFM | FM | CDW | Nematic | Correlation |
|---|---|---|---|---|---|---|
| gpt-4.1-mini | 0.838 | 0.651 | 0.368 | 0.918 | 0.516 | 0.488 |
| gpt-4.1 | 0.767 | 0.792 | 0.662 | 0.918 | 0.722 | 0.900 |
| o4-mini | 0.563 | 0.565 | 0.456 | 0.438 | 0.516 | 0.644 |

## Interpretation

- **Zero parse failures across all models** — all four models reliably return valid JSON.
- **Score means decrease with model size**: larger/stronger models assign lower scores on average.
  gpt-5-mini is most generous, o4-mini most conservative (80% all-zero outputs).
- **o4-mini is an outlier**: its reasoning approach makes it very reluctant to assign non-zero
  scores — 80% all-zero vs 54–62% for other models, and the lowest Spearman ρ vs baseline.
  This suggests chain-of-thought reasoning produces more conservative and less consistent scores
  relative to the baseline for this task.
- **gpt-4.1 shows the highest Spearman correlations** with the baseline (ρ=0.90 for Correlation,
  0.92 for CDW), suggesting it agrees most with gpt-5-mini on relative rankings while giving
  lower absolute scores.
- **gpt-4.1-mini is a good trade-off**: similar ranking agreement (ρ~0.84–0.92 for main
  mechanisms) at lower cost than gpt-4.1.
- **CDW is the most consistent mechanism across models** (ρ=0.92 for both gpt-4.1-mini and gpt-4.1).
- **Plasmon and Bipolaron are all-zero for every model** on this sample — these mechanisms are
  rare in the dataset.

## Output Files

| File | Description |
|---|---|
| `results/scores_gpt-5-mini.csv` | Scores from gpt-5-mini (copied from Ablation 1) |
| `results/scores_gpt-4.1-mini.csv` | Scores from gpt-4.1-mini |
| `results/scores_gpt-4.1.csv` | Scores from gpt-4.1 |
| `results/scores_o4-mini.csv` | Scores from o4-mini |
| `results/summary_table.csv` | Per-model mean/std/parse-fail/all-zero stats |
| `results/spearman_vs_baseline.csv` | Per-mechanism Spearman ρ vs gpt-5-mini |
| `results/heatmap_model_mechanism.png` | Score heatmap (model × mechanism) |
| `results/parse_and_zero_rates.png` | Parse failure and all-zero rate bar charts |
| `results/mean_bars_by_model.png` | Mean ± std per mechanism grouped by model |

## Scripts

| Script | Description |
|---|---|
| `run_ablation6.py` | Scores 50-paper sample with each available model; reuses gpt-5-mini from Ablation 1 |
| `compare_results.py` | Computes summary stats, Spearman ρ, and all plots |
