import pandas as pd
import time
from openai import OpenAI
from utils.openai_APIKEY import OPENAI_KEY
from tqdm import tqdm

client = OpenAI(api_key=OPENAI_KEY)
INPUT_FILE = "../data/SC_related_cites_010.csv"
OUTPUT_FILE = "../data/SC_related_cites_010_GPT_evidence.csv"
EVIDENCE_COLUMN = "GPT_evidence_output"

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


def generate_evidence_json(text: str) -> str:
    prompt = f"""
Begin your output from here. Return ONLY the JSON dictionary.

{text}
"""
    resp = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return resp.choices[0].message.content.strip()


df = pd.read_csv(INPUT_FILE)
if EVIDENCE_COLUMN not in df.columns:
    df[EVIDENCE_COLUMN] = None

for i in tqdm(range(len(df))):
    if pd.notna(df.loc[i, EVIDENCE_COLUMN]) and str(df.loc[i, EVIDENCE_COLUMN]).strip():
        continue

    print(f"Processing row {i + 1}/{len(df)}")

    text = df.loc[i, "abstract"]

    try:
        df.loc[i, EVIDENCE_COLUMN] = generate_evidence_json(text)
    except Exception as e:
        print(f"Error at row {i}: {e}")
        df.loc[i, EVIDENCE_COLUMN] = None

    if (i + 1) % 100 == 0:
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Checkpoint saved at row {i}")
        break

    time.sleep(0.5)

df.to_csv(OUTPUT_FILE, index=False)
print("Finished. Saved full output.")
