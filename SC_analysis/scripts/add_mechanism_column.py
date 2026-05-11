"""
Add a 'mechanism' column (after 'family') to SC_final_data_5k.csv.

The mechanism is extracted from 'opinion_scores_dict' by finding the key with
the highest numeric score. Ties are broken by the priority order in
MECHANISM_LABELS (first in that list wins).
"""

import csv
import json
import ast
import sys
from pathlib import Path

CSV_PATH = Path(__file__).parent.parent / "SC_final_data_5k.csv"

# Priority order: first entry wins on ties.
MECHANISM_LABELS = [
    "pure el-ph coupling",
    "bipolaron el-ph coupling",
    "AFM fluctuation",
    "FM fluctuation",
    "charge density wave",
    "nematic fluctuation",
    "plasmon fluctuation",
    "pure el correlation",
    "spin liquid el correlation",
    "none",
]
MECHANISM_PRIORITY = {k: i for i, k in enumerate(MECHANISM_LABELS)}
NON_MECHANISM_KEYS = {"system", "model"}


def parse_scores(raw: str) -> dict:
    if not raw or raw.strip() in ("", "{}", "nan"):
        return {}
    try:
        return json.loads(raw)
    except Exception:
        pass
    try:
        return ast.literal_eval(raw)
    except Exception:
        return {}


def top_mechanism(scores: dict) -> str:
    mech = {k: v for k, v in scores.items() if k not in NON_MECHANISM_KEYS}
    if not mech:
        return "none"
    max_score = max(mech.values())
    if max_score == 0:
        return "none"
    candidates = [k for k, v in mech.items() if v == max_score]
    # Break ties by priority order; unknown keys go last.
    candidates.sort(key=lambda k: MECHANISM_PRIORITY.get(k, len(MECHANISM_LABELS)))
    return candidates[0]


def main():
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        original_fields = reader.fieldnames[:]
        for row in reader:
            rows.append(row)

    if "family" not in original_fields:
        sys.exit("ERROR: 'family' column not found in CSV.")

    # Build new field order: insert 'mechanism' right after 'family'.
    family_idx = original_fields.index("family")
    if "mechanism" in original_fields:
        # Column already exists — overwrite in place, keep field order.
        new_fields = original_fields
        print("'mechanism' column already exists — values will be overwritten.")
    else:
        new_fields = (
            original_fields[: family_idx + 1]
            + ["mechanism"]
            + original_fields[family_idx + 1 :]
        )

    stats = {}
    for row in rows:
        raw = row.get("opinion_scores_dict", "")
        mech = top_mechanism(parse_scores(raw))
        row["mechanism"] = mech
        stats[mech] = stats.get(mech, 0) + 1

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=new_fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. Wrote {len(rows)} rows to {CSV_PATH}")
    print("\nMechanism distribution:")
    for mech, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {count:5d}  {mech}")


if __name__ == "__main__":
    main()
