import pandas as pd
import time
import json
from openai import OpenAI
from utils.openai_APIKEY import OPENAI_KEY
from tqdm import tqdm

client = OpenAI(api_key=OPENAI_KEY)
OUTPUT_FILE = "../data/SC_related_cites_010_GPT_processed.csv"

def load_system_prompt():
    with open("./prompt/prompt_general.md", "r", encoding="utf-8") as f1:
        part1 = f1.read()
    with open("./prompt/prompt_fewshot_distilled.md", "r", encoding="utf-8") as f2:
        part2 = f2.read()

    # Merge and create a final SYSTEM_PROMPT
    SYSTEM_PROMPT = part1 + "\n\n" + part2
    return SYSTEM_PROMPT

SYSTEM_PROMPT = load_system_prompt()

def generate_opinion(text):    
    prompt = f"""
Begin your output from here. Return ONLY the JSON dictionary.

{text}
"""
    resp = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
    )
    out = resp.choices[0].message.content.strip()
    return out

df = pd.read_csv("../data/SC_related_cites_010.csv")
df["GPT_output"] = None
results = []

for i in tqdm(range(len(df))):
    # Skip rows already processed
    if pd.notna(df.loc[i, "GPT_output"]):
        continue

    print(f"Processing row {i+1}/{len(df)}")

    text = df.loc[i, "abstract"]

    try:
        raw_json = generate_opinion(text)   # raw JSON string
        df.loc[i, "GPT_output"] = raw_json
    except Exception as e:
        print(f"Error at row {i}: {e}")
        df.loc[i, "GPT_output"] = None

    if ((i + 1) % 10 == 0):
        df.to_csv(OUTPUT_FILE, index=False)
        print(f"Checkpoint saved at row {i}")
        break
    # To avoid hitting API rate limits
    time.sleep(0.5)

# final save
df.to_csv(OUTPUT_FILE, index=False)
print("Finished. Saved full output.")