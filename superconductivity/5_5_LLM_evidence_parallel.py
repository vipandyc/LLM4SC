import pandas as pd
from openai import OpenAI
from utils.openai_APIKEY import OPENAI_KEY
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import os

INPUT_FILE = "../data/SC_related_cites_010.csv"
OUTPUT_FILE = "../data/SC_related_cites_010_GPT_evidence.csv"
EVIDENCE_COLUMN = "GPT_evidence_output"

# -------------------------------------------------
# Load system prompt ONCE
# -------------------------------------------------
def load_system_prompt():
    base = "./prompt_evidence"
    with open(f"{base}/prompt_general.md", "r", encoding="utf-8") as f1:
        part1 = f1.read()
    try:
        with open(f"{base}/prompt_fewshot_distilled.md", "r", encoding="utf-8") as f2:
            part2 = f2.read()
    except FileNotFoundError:
        part2 = ""
    return part1 + "\n\n" + part2


SYSTEM_PROMPT = load_system_prompt()

# -------------------------------------------------
# Worker function (runs INSIDE each process)
# -------------------------------------------------
def process_one(args):
    index, text = args

    client = OpenAI(api_key=OPENAI_KEY)

    prompt = f"""
Begin your output from here. Return ONLY the JSON dictionary.

{text}
"""

    try:
        resp = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        out = resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Worker] Error at {index}: {e}")
        out = None

    return index, out


def _row_needs_evidence(df, i):
    v = df.loc[i, EVIDENCE_COLUMN]
    if pd.isna(v):
        return True
    return not str(v).strip()


# -------------------------------------------------
# MAIN
# -------------------------------------------------
if os.path.exists(OUTPUT_FILE):
    df = pd.read_csv(OUTPUT_FILE)
    if EVIDENCE_COLUMN not in df.columns:
        df[EVIDENCE_COLUMN] = None
    print("Loaded existing checkpoint.")
else:
    df = pd.read_csv(INPUT_FILE)
    if EVIDENCE_COLUMN not in df.columns:
        df[EVIDENCE_COLUMN] = None

tasks = [
    (i, df.loc[i, "abstract"])
    for i in range(len(df))
    if _row_needs_evidence(df, i)
]

print(f"Total remaining items: {len(tasks)}")

N_WORKERS = min(8, cpu_count())
print(f"Using {N_WORKERS} parallel workers.")

with Pool(N_WORKERS) as pool:
    for idx, out in tqdm(pool.imap_unordered(process_one, tasks), total=len(tasks)):
        df.loc[idx, EVIDENCE_COLUMN] = out

        if idx % 32 == 0:
            df.to_csv(OUTPUT_FILE, index=False)
            print(f"Checkpoint saved at row {idx}")

df.to_csv(OUTPUT_FILE, index=False)
print("Finished. Saved full output.")
