#!/usr/bin/env python3
"""
Ablation 1 — Step 2: Score a small sample with both the baseline and paraphrased
few-shot prompts, saving results to ablation/ablation1_paraphrase_examples/results/.

Usage (from repo root):
    python ablation/ablation1_paraphrase_examples/run_ablation1.py [--n 50]

--n: number of papers to sample (default 50)
"""

import argparse
import os
import sys
from multiprocessing import Pool, cpu_count
from pathlib import Path

import pandas as pd
from openai import OpenAI
from tqdm import tqdm

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = REPO_ROOT / "data" / "SC_related_cites_010.csv"
PROMPT_GENERAL = REPO_ROOT / "superconductivity" / "prompt" / "prompt_general.md"
PROMPT_BASELINE = REPO_ROOT / "superconductivity" / "prompt" / "prompt_fewshot_distilled.md"
PROMPT_PARAPHRASED = REPO_ROOT / "superconductivity" / "prompt" / "prompt_fewshot_paraphrased.md"

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

BASELINE_OUT = RESULTS_DIR / "baseline_scores.csv"
PARAPHRASED_OUT = RESULTS_DIR / "paraphrased_scores.csv"

# Global so multiprocessing workers can pickle the function
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


def load_system_prompt(fewshot_path: Path) -> str:
    general = PROMPT_GENERAL.read_text(encoding="utf-8")
    fewshot = fewshot_path.read_text(encoding="utf-8")
    return general + "\n\n" + fewshot


def _process_one(args):
    index, text = args
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
        print(f"[Worker] Error at {index}: {e}")
        out = None
    return index, out


def run_scoring(df: pd.DataFrame, system_prompt: str, output_file: Path, api_key: str) -> pd.DataFrame:
    global _SYSTEM_PROMPT, _API_KEY
    if output_file.exists():
        result = pd.read_csv(output_file)
        print(f"  Loaded existing results from {output_file.name}")
        return result

    _SYSTEM_PROMPT = system_prompt
    _API_KEY = api_key

    result = df[["id", "abstract"]].copy()
    result["GPT_output"] = None

    tasks = list(enumerate(result["abstract"].tolist()))
    N = min(4, cpu_count(), len(tasks))

    with Pool(N) as pool:
        for idx, out in tqdm(pool.imap_unordered(_process_one, tasks), total=len(tasks)):
            result.loc[idx, "GPT_output"] = out

    result.to_csv(output_file, index=False)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=50, help="Number of papers to sample")
    args = parser.parse_args()

    if not PROMPT_PARAPHRASED.exists():
        print(f"ERROR: {PROMPT_PARAPHRASED} not found.")
        print("Run generate_paraphrased_prompt.py first.")
        sys.exit(1)

    api_key = load_api_key()
    df = pd.read_csv(DATA_FILE)

    # Fixed seed so both runs cover identical papers
    sample = df.sample(n=min(args.n, len(df)), random_state=42).reset_index(drop=True)
    print(f"Sampled {len(sample)} papers from {DATA_FILE.name}")

    print("\n=== Scoring with BASELINE prompt ===")
    run_scoring(sample, load_system_prompt(PROMPT_BASELINE), BASELINE_OUT, api_key)

    print("\n=== Scoring with PARAPHRASED prompt ===")
    run_scoring(sample, load_system_prompt(PROMPT_PARAPHRASED), PARAPHRASED_OUT, api_key)

    print(f"\nDone. Results saved in {RESULTS_DIR}")


if __name__ == "__main__":
    main()
