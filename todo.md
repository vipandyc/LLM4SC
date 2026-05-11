# Ablation Study TODO

## Ablation 1 — Paraphrase Examples
Paraphrase the few-shot examples in `prompt/prompt_fewshot_distilled.md` using an LLM, keeping the scientific content identical but varying the phrasing. Re-run opinion scoring with paraphrased examples and compare score distributions against the baseline.

- [ ] Generate paraphrased versions of the 23 few-shot examples
- [ ] Save as `prompt/prompt_fewshot_paraphrased.md`
- [ ] Run `5_LLM_opinions_parallel.py` with paraphrased examples
- [ ] Compare score distributions (mean, std per mechanism) vs. baseline

## Ablation 1.5 — Paraphrase Prompt (Input Abstracts)
Paraphrase the input abstracts (not the examples) before feeding them to the model. Use an LLM to generate K = {1, 3, 5} paraphrases per abstract, score each independently, then aggregate by averaging.

- [ ] Write a paraphrase generation script (`paraphrase_abstracts.py`) using the OpenAI API
- [ ] Run for K = 1, 3, 5 paraphrases on a held-out sample (~200 papers)
- [ ] Aggregate scores by averaging across paraphrases
- [ ] Measure score variance vs. K — find the saturation point

## Ablation 2 — Sensitivity to Time (Temporal Bias)
Test whether the LLM's opinion scores are sensitive to the publication year context. Run the same abstract with and without the year prepended, and also compare scores on papers from different decades (1986–1999, 2000–2009, 2010–2019, 2020–present).

- [ ] Add a `--include_year` flag to the scoring pipeline
- [ ] Re-score a sample with year prepended to the abstract input
- [ ] Compare mechanism score distributions decade by decade
- [ ] Check if the model's priors (e.g., favoring AFM fluctuation for cuprates) shift with year context

## Ablation 3 — Enhance Prompt with Textbook Knowledge
Augment the system prompt with authoritative condensed matter physics definitions sourced from *Condensed Matter Field Theory* (Alexander Altland & Ben Simons). Add concise textbook-level descriptions of each mechanism to ground the LLM's scoring.

- [ ] Extract relevant mechanism descriptions from Altland & Simons (chapters on superconductivity, spin fluctuations, strong correlations)
- [ ] Write an enriched system prompt: `prompt/prompt_textbook_enhanced.md`
- [ ] Run scoring pipeline with new prompt on held-out sample
- [ ] Compare against baseline: does precision on edge-case papers improve?

## Ablation 4 — Tune Temperature
Sweep LLM sampling temperature T = {0.0, 0.3, 0.5, 0.7, 1.0} and measure score variance and consistency.

- [ ] Add `--temperature` argument to `5_LLM_opinions_parallel.py`
- [ ] Run each temperature on the same ~200-paper sample
- [ ] For each temperature, compute: per-mechanism score std, parse failure rate, fraction of all-zero outputs
- [ ] Identify the temperature that minimizes variance while preserving non-trivial scores (not all zeros)

## Ablation 6 — Benchmark Different Models
Compare opinion scoring quality and consistency across different LLMs using the same prompt (baseline few-shot) and the same held-out paper sample. Current baseline is `gpt-5-mini`.

Models to benchmark:

| Model | Provider | Notes |
|---|---|---|
| `gpt-5-mini` | OpenAI | **baseline** |
| `gpt-4.1-mini` | OpenAI | Stronger OpenAI mid-tier |
| `gpt-4.1` | OpenAI | Best OpenAI, higher cost |
| `o4-mini` | OpenAI | Reasoning model; test if chain-of-thought helps |
| `claude-sonnet-4-5` | Anthropic | Mid-tier Claude |
| `claude-opus-4-5` | Anthropic | Strongest Claude |

- [ ] Extend scoring script to accept `--model` argument
- [ ] Run all models on the same ~200-paper held-out sample
- [ ] Collect per-model: score distributions per mechanism, parse failure rate, fraction all-zero outputs, API cost estimate
- [ ] If gold labels available: compute MAE and Spearman correlation per model
- [ ] Plot score heatmap (model × mechanism) to visualize systematic biases between models

## Ablation 7 — Adversarial Scoring
Test robustness against adversarial inputs: abstracts designed to mislead the model into assigning wrong mechanism scores. This probes whether the model is doing genuine semantic reasoning or superficial keyword matching.

Three adversarial strategies:

**7a — Keyword Injection**
Take real abstracts scored all-zeros (irrelevant papers) and inject mechanism keywords (e.g., "spin fluctuation", "AFM", "CDW") without changing the actual scientific claim. Check if scores spuriously jump above 0.
- [ ] Select ~50 all-zero-scored papers from the dataset
- [ ] Inject one or two mechanism keywords per paper into the abstract (e.g., append "This work is unrelated to spin fluctuations.")
- [ ] Re-score and measure false-positive rate per injected keyword

**7b — Mechanism Substitution**
Take real abstracts with a clear dominant mechanism (score ≥ 4 on one mechanism) and replace the mechanism's keyword phrases with those of a different mechanism, keeping everything else intact.
- [ ] Select ~50 papers with a clear dominant mechanism
- [ ] Substitute keywords (e.g., replace all AFM-fluctuation terms with CDW terms)
- [ ] Re-score and measure how often the model follows the injected keywords vs. the broader context

**7c — Out-of-Domain Papers**
Feed abstracts from adjacent but unrelated fields (e.g., topological insulators, quantum computing, conventional BCS superconductors, high-energy physics) and verify the model correctly outputs all-zero scores.
- [ ] Collect ~50 out-of-domain abstracts (can pull from existing papers already scored all-zero)
- [ ] Re-score and compute false-positive rate (any mechanism score > 0 is a hallucination)
- [ ] Compare false-positive rates across models (links to Ablation 6)

**Metric for all 7a/7b/7c**: adversarial robustness score = fraction of papers where the model is NOT fooled.

- [ ] Summarize results in a 3-row table (7a / 7b / 7c) × models

## Ablation 5 — Majority Vote
Run the model N = {3, 5, 10} times per abstract at a fixed temperature (e.g., T = 0.7), then aggregate scores by majority vote (for discrete scores) or averaging (for continuous).

- [ ] Implement a multi-sample wrapper in a new script `5_LLM_opinions_majority_vote.py`
- [ ] For each paper, collect N raw score dicts and aggregate
- [ ] Compare majority-vote scores vs. single-call baseline against gold labels
- [ ] Plot score variance vs. N to find the practical saturation point
