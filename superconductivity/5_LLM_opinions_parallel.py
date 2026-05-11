import pandas as pd
import time
import json
from openai import OpenAI
from utils.openai_APIKEY import OPENAI_KEY
from multiprocessing import Pool, cpu_count
from tqdm import tqdm
import os

OUTPUT_FILE = "../data/SC_related_cites_010_GPT_processed.csv"

# -------------------------------------------------
# Load system prompt ONCE
# -------------------------------------------------
def load_system_prompt():
    with open("./prompt/prompt_general.md", "r", encoding="utf-8") as f1:
        part1 = f1.read()
    with open("./prompt/prompt_fewshot_distilled.md", "r", encoding="utf-8") as f2:
        part2 = f2.read()
    return part1 + "\n\n" + part2

SYSTEM_PROMPT = load_system_prompt()

# -------------------------------------------------
# Worker function (runs INSIDE each process)
# -------------------------------------------------
def process_one(args):
    index, text = args

    client = OpenAI(api_key=OPENAI_KEY)  # each worker gets its own client

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

    # Return (row_index, output_string)
    return index, out

# -------------------------------------------------
# MAIN
# -------------------------------------------------
if os.path.exists(OUTPUT_FILE):
    df = pd.read_csv(OUTPUT_FILE)
    print("Loaded existing checkpoint.")
else:
    df = pd.read_csv("../data/SC_related_cites_010.csv")
    df["GPT_output"] = None

# Prepare task list
tasks = [(i, df.loc[i, "abstract"]) for i in range(len(df)) if pd.isna(df.loc[i, "GPT_output"])]

print(f"Total remaining items: {len(tasks)}")

# Use N processes
N_WORKERS = min(8, cpu_count())  # or manually set a number like 4 or 6
print(f"Using {N_WORKERS} parallel workers.")

# Run in parallel
with Pool(N_WORKERS) as pool:
    for idx, out in tqdm(pool.imap_unordered(process_one, tasks), total=len(tasks)):
        df.loc[idx, "GPT_output"] = out

        # Save every 100 rows
        if idx % 32 == 0:
            df.to_csv(OUTPUT_FILE, index=False)
            print(f"Checkpoint saved at row {idx}")

# Final save
df.to_csv(OUTPUT_FILE, index=False)
print("Finished. Saved full output.")
