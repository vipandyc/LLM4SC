#!/usr/bin/env python3
"""
Ablation 6 — Benchmark Different Models.

Scores the same 50-paper sample (seed 42) with each available model using the
baseline prompt, then saves per-model CSV to results/.

gpt-5-mini results are reused from ablation1_paraphrase_examples/results/baseline_scores.csv.

Usage (from repo root):
    python ablation/ablation6_model_benchmark/run_ablation6.py [--models gpt-4.1-mini gpt-4.1 o4-mini]
"""

import argparse
import os
import shutil
from multiprocessing import Pool, cpu_count
from pathlib import Path

import pandas as pd
from openai import OpenAI
from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = REPO_ROOT / "data" / "SC_related_cites_010.csv"
PROMPT_GENERAL = REPO_ROOT / "superconductivity" / "prompt" / "prompt_general.md"
PROMPT_FEWSHOT = REPO_ROOT / "superconductivity" / "prompt" / "prompt_fewshot_distilled.md"
BASELINE_SRC = REPO_ROOT / "ablation" / "ablation1_paraphrase_examples" / "results" / "baseline_scores.csv"

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

OPENAI_MODELS = ["gpt-5-mini", "gpt-4.1-mini", "gpt-4.1", "o4-mini", "gpt-5", "o3", "gpt-5.4"]
ALL_MODELS = OPENAI_MODELS  # extend when Anthropic SDK available

_SYSTEM_PROMPT: str = ""
_API_KEY: str = ""
_MODEL: str = ""


def load_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        return key
    local = REPO_ROOT / "superconductivity" / "utils" / "openai_key_local.py"
    if local.exists():
        ns: dict = {}
        exec(local.read_text(), ns)
        key = ns.get("OPENAI_KEY", "").strip()
        if key:
            return key
    raise RuntimeError("OpenAI API key not found.")


def load_system_prompt() -> str:
    return PROMPT_GENERAL.read_text(encoding="utf-8") + "\n\n" + PROMPT_FEWSHOT.read_text(encoding="utf-8")


def _score_one(args):
    paper_idx, text = args
    client = OpenAI(api_key=_API_KEY)
    user_msg = f"Begin your output from here. Return ONLY the JSON dictionary.\n\n{text}"
    try:
        resp = client.chat.completions.create(
            model=_MODEL,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
        )
        out = resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[{_MODEL}] Error at {paper_idx}: {e}")
        out = None
    return paper_idx, out


def score_model(sample: pd.DataFrame, model: str, api_key: str, system_prompt: str) -> pd.DataFrame:
    global _SYSTEM_PROMPT, _API_KEY, _MODEL
    out_file = RESULTS_DIR / f"scores_{model.replace('/', '_')}.csv"

    if out_file.exists():
        print(f"  [{model}] Loaded cached results.")
        return pd.read_csv(out_file)

    _SYSTEM_PROMPT = system_prompt
    _API_KEY = api_key
    _MODEL = model

    result = sample[["id", "abstract"]].copy()
    result["GPT_output"] = None
    tasks = list(enumerate(result["abstract"].tolist()))
    N = min(4, cpu_count(), len(tasks))

    with Pool(N) as pool:
        for idx, out in tqdm(pool.imap_unordered(_score_one, tasks), total=len(tasks), desc=model):
            result.loc[idx, "GPT_output"] = out

    result.to_csv(out_file, index=False)
    print(f"  [{model}] Saved to {out_file.name}")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", default=["gpt-5", "o3"],
                        help="Models to run (gpt-5-mini is reused from ablation 1)")
    parser.add_argument("--n", type=int, default=50)
    args = parser.parse_args()

    # Copy gpt-5-mini baseline
    dst_baseline = RESULTS_DIR / "scores_gpt-5-mini.csv"
    if not dst_baseline.exists():
        shutil.copy(BASELINE_SRC, dst_baseline)
        print(f"Copied gpt-5-mini baseline from {BASELINE_SRC.name}")

    api_key = load_api_key()
    system_prompt = load_system_prompt()

    df_full = pd.read_csv(DATA_FILE)
    sample = df_full.sample(n=min(args.n, len(df_full)), random_state=42).reset_index(drop=True)
    print(f"Sample: {len(sample)} papers (seed 42)\n")

    for model in args.models:
        if model not in OPENAI_MODELS:
            print(f"Skipping {model} — not available (install anthropic SDK)")
            continue
        score_model(sample, model, api_key, system_prompt)

    print(f"\nDone. Results in {RESULTS_DIR}")


if __name__ == "__main__":
    main()
