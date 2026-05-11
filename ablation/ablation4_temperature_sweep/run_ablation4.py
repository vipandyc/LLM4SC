#!/usr/bin/env python3
"""
Ablation 4 — Temperature Sweep.

Scores the same 50-paper sample (seed 42) with gpt-4.1-mini at
temperatures T = {0.0, 0.3, 0.5, 0.7, 1.0} and saves per-temperature CSVs.

Usage (from repo root):
    python ablation/ablation4_temperature_sweep/run_ablation4.py
"""

import os
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

MODEL = "gpt-4.1-mini"
TEMPERATURES = [0.0, 0.3, 0.5, 0.7, 1.0]
N_SAMPLE = 50
SEED = 42

_SYSTEM_PROMPT: str = ""
_API_KEY: str = ""
_MODEL: str = ""
_TEMPERATURE: float = 1.0


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
            temperature=_TEMPERATURE,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
        )
        out = resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[T={_TEMPERATURE}] Error at {paper_idx}: {e}")
        out = None
    return paper_idx, out


def score_temperature(sample: pd.DataFrame, temp: float, api_key: str, system_prompt: str) -> pd.DataFrame:
    global _SYSTEM_PROMPT, _API_KEY, _MODEL, _TEMPERATURE
    label = str(temp).replace(".", "p")
    out_file = RESULTS_DIR / f"scores_T{label}.csv"

    if out_file.exists():
        print(f"  [T={temp}] Loaded cached results.")
        return pd.read_csv(out_file)

    _SYSTEM_PROMPT = system_prompt
    _API_KEY = api_key
    _MODEL = MODEL
    _TEMPERATURE = temp

    result = sample[["id", "abstract"]].copy()
    result["GPT_output"] = None
    tasks = list(enumerate(result["abstract"].tolist()))
    N = min(4, cpu_count(), len(tasks))

    with Pool(N) as pool:
        for idx, out in tqdm(pool.imap_unordered(_score_one, tasks), total=len(tasks), desc=f"T={temp}"):
            result.loc[idx, "GPT_output"] = out

    result.to_csv(out_file, index=False)
    print(f"  [T={temp}] Saved to {out_file.name}")
    return result


def main():
    api_key = load_api_key()
    system_prompt = load_system_prompt()

    df_full = pd.read_csv(DATA_FILE)
    sample = df_full.sample(n=min(N_SAMPLE, len(df_full)), random_state=SEED).reset_index(drop=True)
    print(f"Model: {MODEL}")
    print(f"Sample: {len(sample)} papers (seed {SEED})\n")

    for temp in TEMPERATURES:
        score_temperature(sample, temp, api_key, system_prompt)

    print(f"\nDone. Results in {RESULTS_DIR}")


if __name__ == "__main__":
    main()
