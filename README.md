# LLM for Superconductivity — Project Overview

This project uses LLMs to extract mechanism opinions, evidence types, and experimental/computational methods from superconductivity paper abstracts, then analyzes trends across families and decades.

---

## Repository Layout

```
RevGPT_dev/
├── data/                          # All CSV data files
├── superconductivity/             # LLM inference scripts + prompts + notebooks
│   ├── prompt/                    # Opinion-scoring prompts
│   ├── prompt_evidence/           # Evidence-extraction prompts
│   ├── prompt_method_classify/    # Method-classification prompts
│   └── utils/                     # API key loader, helpers
├── SC_analysis/                   # Post-processing scripts and outputs
│   ├── scripts/                   # Python scripts to build final data and figures
│   ├── output/                    # Generated CSVs and figures
│   ├── SC_final_data_5k.csv       # Curated 5k-paper analysis dataset
│   └── SC_final_data_17k.csv      # Full 17k-paper dataset
├── ablation/                      # Ablation study results (see below)
└── todo.md                        # Planned ablation studies
```

---

## Full Pipeline Workflow

### Step 0 — Prerequisites

- Python 3.10+, `openai`, `pandas`, `tqdm`, `matplotlib`, `seaborn`, `pyyaml`
- OpenAI API key stored in `superconductivity/utils/openai_key_local.py` as `OPENAI_KEY = "sk-..."` (gitignored)
  or export `OPENAI_API_KEY` environment variable
- Working directory for LLM scripts: `superconductivity/`

---

### Step 1 — Opinion Scoring (`5_LLM_opinions_parallel.py`)

Scores each abstract on 9 unconventional superconductivity mechanisms (0–5 scale).

**Input:** `data/SC_related_cites_010.csv` — base paper metadata with `abstract` column.

**Prompts loaded:**
- `superconductivity/prompt/prompt_general.md` — system instructions + scoring schema
- `superconductivity/prompt/prompt_fewshot_distilled.md` — 23 few-shot examples

**Output:** `data/SC_related_cites_010_GPT_processed.csv`  
Adds column `GPT_output` — raw JSON string with keys:
```json
{
  "system": "...",
  "model": "...",
  "pure el-ph coupling": 0.0,
  "bipolaron el-ph coupling": 0.0,
  "AFM fluctuation": 0.0,
  "FM fluctuation": 0.0,
  "charge density wave": 0.0,
  "nematic fluctuation": 0.0,
  "plasmon fluctuation": 0.0,
  "pure el correlation": 0.0,
  "spin liquid el correlation": 0.0
}
```

**Run:**
```bash
cd superconductivity/
python 5_LLM_opinions_parallel.py
```
Checkpoints every 32 rows; safe to interrupt and resume.

---

### Step 2 — Evidence Extraction (`5_5_LLM_evidence_parallel.py`)

Extracts experimental and computational evidence from each abstract.

**Input:** `data/SC_related_cites_010.csv`

**Prompts loaded:**
- `superconductivity/prompt_evidence/prompt_general.md`
- `superconductivity/prompt_evidence/prompt_fewshot_distilled.md` (if present)

**Output:** `data/SC_related_cites_010_GPT_evidence.csv`  
Adds column `GPT_evidence_output` — JSON with fields including `computational_methods`, `experimental_methods`, `theoretical_analytic_methods`, `method_summary`.

**Run:**
```bash
cd superconductivity/
python 5_5_LLM_evidence_parallel.py
```

---

### Step 3 — Method Classification (`5_7_LLM_method_classify_parallel.py`)

Classifies extracted methods into 128 standardized categories (multi-hot binary).

**Input:** `data/SC_related_cites_010_GPT_evidence.csv`

**Prompt loaded:**
- `superconductivity/prompt_method_classify/prompt_general.md`

**Output:**
- `data/SC_related_cites_010_method_binary_raw.csv` — raw LLM output (intermediate checkpoint)
- `data/SC_related_cites_010_method_binary.csv` — one binary column per method category + `id`

**Run:**
```bash
cd superconductivity/
python 5_7_LLM_method_classify_parallel.py
# Or for a quick test:
python 5_7_LLM_method_classify_parallel.py --test 5
```

---

### Step 4 — Build Final Dataset (`SC_analysis/scripts/build_sc_final_data.py`)

Joins method binary labels + opinion scores + internal citation graph into a single analysis-ready CSV.

**Inputs:**
- `data/SC_related_cites_010_method_binary.csv`
- `data/SC_related_cites_010_GPT_processed.csv`
- `superconductivity/citation_edges_internal.csv`

**Output:** `SC_analysis/SC_final_data.csv` (full) + `SC_analysis/SC_final_data_validation.txt`

**Run (from repo root):**
```bash
python SC_analysis/scripts/build_sc_final_data.py
```

---

### Step 5 — Post-Processing Columns

These scripts enrich `SC_analysis/SC_final_data_5k.csv` with derived columns:

| Script | Adds column(s) | Description |
|---|---|---|
| `add_family_column.py` | `family` | Infers superconductor family from `system` field |
| `add_mechanism_column.py` | `mechanism` | Top-scoring mechanism from `opinion_scores_dict` |
| `add_evidence_columns.py` | `evidence_computation`, `evidence_experiment` | Pipe-separated active method labels |

**Run (from repo root):**
```bash
python SC_analysis/scripts/add_family_column.py
python SC_analysis/scripts/add_mechanism_column.py
python SC_analysis/scripts/add_evidence_columns.py
```

---

### Step 6 — Figures

Individual figure scripts in `SC_analysis/scripts/`. All output goes to `SC_analysis/output/figures/`.

**Figure 2 — Data Statistics:**
```bash
python SC_analysis/scripts/make_figure2.py   # panels 2.1–2.6 combined
# Or individual panels:
python SC_analysis/scripts/make_fig2_1.py    # Family distribution
python SC_analysis/scripts/make_fig2_2.py    # Mechanism distribution
python SC_analysis/scripts/make_fig2_3_1.py  # Theoretical evidence distribution
python SC_analysis/scripts/make_fig2_4.py    # Timeline by family
python SC_analysis/scripts/make_fig2_5.py    # Timeline by mechanism
python SC_analysis/scripts/make_fig2_6.py    # Timeline by evidence
```

**Figure 3 — Correlation Matrices:**
```bash
python SC_analysis/scripts/make_figure3.py   # All fig3 panels
```

---

## Key Data Files

| File | Description |
|---|---|
| `data/SC_related_cites_010.csv` | Base ~10k SC paper metadata + abstracts |
| `data/SC_related_cites_010_GPT_processed.csv` | + opinion scores (`GPT_output`) |
| `data/SC_related_cites_010_GPT_evidence.csv` | + evidence extraction (`GPT_evidence_output`) |
| `data/SC_related_cites_010_method_binary.csv` | + 128-category method binary labels |
| `SC_analysis/SC_final_data_5k.csv` | Curated 5k subset with all columns |
| `SC_analysis/SC_final_data_17k.csv` | Full 17k dataset |
| `data/SC_theory_highlights.csv` | Theory-focused subset with confidence scores |
| `superconductivity/citation_edges_internal.csv` | Internal citation graph edges |

---

## Prompts

| Directory | Purpose |
|---|---|
| `superconductivity/prompt/` | Opinion scoring (9 mechanisms, 0–5 scale) |
| `superconductivity/prompt_evidence/` | Evidence/method extraction (JSON schema) |
| `superconductivity/prompt_method_classify/` | 128-category method classification |

---

## Ablation Studies

Ablation experiments are run on a small held-out sample (~50 papers) to avoid large API costs. Results are stored in `ablation/` with one subdirectory per ablation.

See `todo.md` for the full list of planned ablations. Current studies:

| Ablation | Directory | Description |
|---|---|---|
| Ablation 1 | `ablation/ablation1_paraphrase_examples/` | Paraphrase few-shot examples; compare score distributions |

### Running Ablation 1

```bash
# Step 1: Generate paraphrased few-shot examples
python ablation/ablation1_paraphrase_examples/generate_paraphrased_prompt.py

# Step 2: Run opinion scoring with paraphrased examples on sample
python ablation/ablation1_paraphrase_examples/run_ablation1.py

# Step 3: Compare distributions against baseline
python ablation/ablation1_paraphrase_examples/compare_results.py
```

Results summary: `ablation/ablation1_paraphrase_examples/results/`

---

## Dev Notes

Figure 3 time-weighting:

```
w(year) = exp(0.05 × (year − 1956))
```

| Year | Weight |
|------|--------|
| 1956 | 1× |
| 1980 | 3.3× |
| 2000 | 9× |
| 2010 | 15× |
| 2020 | 24× |
| 2024 | 29× |

Correlation matrices use weighted conditional probabilities (e.g. P(mechanism | family)), normalised by the weighted row sum. Delta maps (Fig. 3.8, 3.9) show weighted minus unweighted.

**TODO**: re-weigh not just on publication date, but on the date that the used technique is invented.

**Figure 4 ideas** — leverage citation graph:
- Re-weigh opinion with citation counts of papers
- Along citation graph, how "evidence" generates and propagates (diffuses)
- Along citation graph, how "mechanisms" generate and propagate (diffuse)
