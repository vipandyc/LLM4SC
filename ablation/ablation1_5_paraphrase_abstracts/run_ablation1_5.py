#!/usr/bin/env python3
"""
Ablation 1.5 — Paraphrase Input Abstracts.

For each paper in a held-out sample, generate 5 paraphrases of the abstract,
score each independently with the baseline prompt, then aggregate by averaging.
Saves one raw-scores CSV and one aggregated CSV per K in {original, 1, 3, 5}.

Usage (from repo root):
    python ablation/ablation1_5_paraphrase_abstracts/run_ablation1_5.py [--n 50]
"""

import argparse
import json
import os
import re
from multiprocessing import Pool, cpu_count
from pathlib import Path

import pandas as pd
from openai import OpenAI
from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = REPO_ROOT / "data" / "SC_related_cites_010.csv"
PROMPT_GENERAL = REPO_ROOT / "superconductivity" / "prompt" / "prompt_general.md"
PROMPT_FEWSHOT = REPO_ROOT / "superconductivity" / "prompt" / "prompt_fewshot_distilled.md"

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

MAX_K = 5  # generate this many paraphrases per abstract

PARAPHRASE_SYSTEM = (
    "You are a scientific writing assistant. Rewrite the given physics abstract "
    "with varied phrasing and sentence structure while preserving all scientific "
    "claims, terminology, entities, and meaning exactly. "
    "Do not add or remove any facts. Return only the rewritten abstract."
)

# Globals for multiprocessing workers
_SYSTEM_PROMPT: str = ""
_API_KEY: str = ""


def load_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        return key
    local_key_file = REPO_ROOT / "superconductivity" / "utils" / "openai_key_local.py"
    if local_key_file.exists():
        ns: dict = {}
        exec(local_key_file.read_text(), ns)
        key = ns.get("OPENAI_KEY", "").strip()
        if key:
            return key
    raise RuntimeError("OpenAI API key not found.")


def load_scoring_prompt() -> str:
    general = PROMPT_GENERAL.read_text(encoding="utf-8")
    fewshot = PROMPT_FEWSHOT.read_text(encoding="utf-8")
    return general + "\n\n" + fewshot


# ── Paraphrase workers ────────────────────────────────────────────────────────

def _paraphrase_one(args):
    """Generate one paraphrase; args = (paper_idx, para_idx, abstract)."""
    paper_idx, para_idx, abstract = args
    client = OpenAI(api_key=_API_KEY)
    try:
        resp = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": PARAPHRASE_SYSTEM},
                {"role": "user", "content": abstract},
            ],
        )
        out = resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Paraphrase] Error paper {paper_idx} para {para_idx}: {e}")
        out = abstract  # fall back to original on error
    return paper_idx, para_idx, out


def generate_paraphrases(df: pd.DataFrame, k: int, api_key: str) -> pd.DataFrame:
    """Return DataFrame with columns [paper_idx, para_idx, abstract]."""
    cache_file = RESULTS_DIR / f"paraphrases_k{k}.csv"
    if cache_file.exists():
        print(f"  Loaded cached paraphrases from {cache_file.name}")
        return pd.read_csv(cache_file)

    global _API_KEY
    _API_KEY = api_key

    tasks = [
        (i, j, df.loc[i, "abstract"])
        for i in range(len(df))
        for j in range(k)
    ]
    N = min(4, cpu_count(), len(tasks))
    results = []
    with Pool(N) as pool:
        for paper_idx, para_idx, text in tqdm(
            pool.imap_unordered(_paraphrase_one, tasks), total=len(tasks),
            desc=f"Paraphrasing (k={k})"
        ):
            results.append({"paper_idx": paper_idx, "para_idx": para_idx, "abstract": text})

    para_df = pd.DataFrame(results).sort_values(["paper_idx", "para_idx"]).reset_index(drop=True)
    para_df.to_csv(cache_file, index=False)
    return para_df


# ── Scoring workers ───────────────────────────────────────────────────────────

def _score_one(args):
    paper_idx, para_idx, text = args
    client = OpenAI(api_key=_API_KEY)
    user_msg = f"Begin your output from here. Return ONLY the JSON dictionary.\n\n{text}"
    try:
        resp = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
        )
        out = resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Scoring] Error paper {paper_idx} para {para_idx}: {e}")
        out = None
    return paper_idx, para_idx, out


def score_texts(tasks: list, system_prompt: str, api_key: str) -> list:
    global _SYSTEM_PROMPT, _API_KEY
    _SYSTEM_PROMPT = system_prompt
    _API_KEY = api_key
    N = min(4, cpu_count(), len(tasks))
    results = []
    with Pool(N) as pool:
        for paper_idx, para_idx, out in tqdm(
            pool.imap_unordered(_score_one, tasks), total=len(tasks), desc="Scoring"
        ):
            results.append({"paper_idx": paper_idx, "para_idx": para_idx, "GPT_output": out})
    return results


MECHANISMS = [
    "pure el-ph coupling", "bipolaron el-ph coupling", "AFM fluctuation",
    "FM fluctuation", "charge density wave", "nematic fluctuation",
    "plasmon fluctuation", "pure el correlation", "spin liquid el correlation",
]


def parse_output(raw) -> dict:
    if not isinstance(raw, str) or not raw.strip():
        return {m: 0.0 for m in MECHANISMS}
    raw = re.sub(r"```[a-z]*\n?", "", raw).strip().rstrip("`")
    try:
        obj = json.loads(raw)
    except Exception:
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        obj = json.loads(match.group()) if match else {}
    return {m: float(obj.get(m, 0)) for m in MECHANISMS}


def build_aggregated(scores_df: pd.DataFrame, ids: list, k: int) -> pd.DataFrame:
    """Average scores across k paraphrases per paper."""
    rows = []
    for i, paper_id in enumerate(ids):
        subset = scores_df[scores_df["paper_idx"] == i]
        parsed = [parse_output(r) for r in subset["GPT_output"]]
        avg = {m: sum(p[m] for p in parsed) / len(parsed) for m in MECHANISMS}
        avg["id"] = paper_id
        avg["n_paraphrases"] = len(parsed)
        rows.append(avg)
    return pd.DataFrame(rows)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=50)
    args = parser.parse_args()

    api_key = load_api_key()
    system_prompt = load_scoring_prompt()

    df_full = pd.read_csv(DATA_FILE)
    sample = df_full.sample(n=min(args.n, len(df_full)), random_state=42).reset_index(drop=True)
    ids = sample["id"].tolist()
    print(f"Sampled {len(sample)} papers.")

    # ── Step 1: Score original abstracts (K=0 baseline) ──────────────────────
    orig_cache = RESULTS_DIR / "scores_k0_original.csv"
    if orig_cache.exists():
        orig_scores = pd.read_csv(orig_cache)
        print("Loaded cached original scores.")
    else:
        tasks = [(i, 0, sample.loc[i, "abstract"]) for i in range(len(sample))]
        results = score_texts(tasks, system_prompt, api_key)
        orig_scores = pd.DataFrame(results)
        orig_scores.to_csv(orig_cache, index=False)

    orig_agg = build_aggregated(orig_scores, ids, k=1)
    orig_agg.to_csv(RESULTS_DIR / "aggregated_k0_original.csv", index=False)

    # ── Step 2: Generate MAX_K paraphrases per abstract ───────────────────────
    para_df = generate_paraphrases(sample, MAX_K, api_key)

    # ── Step 3: Score all paraphrases ─────────────────────────────────────────
    score_cache = RESULTS_DIR / f"scores_paraphrases_k{MAX_K}.csv"
    if score_cache.exists():
        para_scores = pd.read_csv(score_cache)
        print(f"Loaded cached paraphrase scores from {score_cache.name}")
    else:
        tasks = [
            (int(row["paper_idx"]), int(row["para_idx"]), row["abstract"])
            for _, row in para_df.iterrows()
        ]
        results = score_texts(tasks, system_prompt, api_key)
        para_scores = pd.DataFrame(results)
        para_scores.to_csv(score_cache, index=False)

    # ── Step 4: Aggregate for K = 1, 3, 5 ────────────────────────────────────
    for k in [1, 3, 5]:
        subset = para_scores[para_scores["para_idx"] < k].copy()
        agg = build_aggregated(subset, ids, k=k)
        agg.to_csv(RESULTS_DIR / f"aggregated_k{k}.csv", index=False)
        print(f"Saved aggregated_k{k}.csv ({len(agg)} papers, k={k} paraphrases each)")

    print(f"\nDone. All results in {RESULTS_DIR}")


if __name__ == "__main__":
    main()
