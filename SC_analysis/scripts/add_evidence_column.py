"""
Add an 'evidence' column (last column) to SC_final_data_5k.csv.

Evidence is derived from binary indicator columns 86-128 (theoretical methods),
mapped to one of eight evidence categories per the scheme below.
Deleted columns (Symmetry Analysis, Model Hamiltonian Analysis,
Effective Hamiltonian, Phase Diagram Analysis) are excluded entirely.
Rows with no active theory columns get 'none'.
Multiple active categories are joined with ' | ' in canonical order.
"""

import csv
from pathlib import Path

CSV_PATH = Path(__file__).parent.parent / "SC_final_data_5k.csv"

# CSV column name -> evidence category.
# 'delete' columns (89, 93, 110, 111) are simply absent from this dict.
# 'residual' columns are treated identically to 'keep' — same category.
# Merged columns share the same category (e.g. London Theory -> Phenomenological SC).
COLUMN_TO_EVIDENCE = {
    # Phenomenological SC  (86, 99, 104, 106, 114, 115)
    "Ginzburg-Landau Theory":                "Phenomenological SC",
    "Phenomenological / Analytical Modeling": "Phenomenological SC",
    "Bean Critical-State Model":             "Phenomenological SC",
    "London Theory":                         "Phenomenological SC",
    "Two-Fluid Model":                       "Phenomenological SC",
    "Collective Pinning Theory":             "Phenomenological SC",

    # Microscopic pairing  (87, 100, 105, 118, 120)
    "Mean-Field Theory":                     "Microscopic pairing",
    "BdG Theory":                            "Microscopic pairing",
    "Proximity Effect Theory":               "Microscopic pairing",
    "Collective Mode Analysis":              "Microscopic pairing",
    "Linearized Gap Equation":               "Microscopic pairing",

    # Field theory & RG  (88, 92, 94, 95, 96, 112, 124)
    "Effective Field Theory":                "Field theory & RG",
    "Scaling Analysis":                      "Field theory & RG",
    "Renormalization Group":                 "Field theory & RG",
    "RPA":                                   "Field theory & RG",
    "Perturbation Theory":                   "Field theory & RG",
    "AdS/CFT (Holographic Duality)":         "Field theory & RG",
    "Nonlinear Sigma Model":                 "Field theory & RG",

    # Response & transport  (90, 122, 127, 128)
    "Linear / Nonlinear Response Theory":    "Response & transport",
    "Green's Function Formalism":            "Response & transport",
    "Drude Model":                           "Response & transport",
    "Anderson Localization Theory":          "Response & transport",

    # Topological  (91, 101, 102)
    "Topological Band/Field Theory":         "Topological",
    "Floquet Theory":                        "Topological",
    "Bulk-Boundary Correspondence":          "Topological",

    # Junction & interface  (97, 98, 117)
    "Andreev Theory":                        "Junction & interface",
    "Josephson Junction Theory":             "Junction & interface",
    "Scattering Theory":                     "Junction & interface",

    # Many-body & correlation  (103, 108, 113, 116, 125)
    "Luttinger Liquid Theory":               "Many-body & correlation",
    "Bosonization":                          "Many-body & correlation",
    "RVB Theory":                            "Many-body & correlation",
    "Fermi Liquid Theory":                   "Many-body & correlation",
    "t-J Model":                             "Many-body & correlation",

    # Quantum circuits & info  (119, 123, 126)
    "Input-Output Theory":                   "Quantum circuits & info",
    "Quantum Measurement Theory":            "Quantum circuits & info",
    "Circuit Quantization":                  "Quantum circuits & info",

    # Other methods  (107, 109, 121)
    "Percolation Theory":                    "Other methods",
    "Linear Stability Analysis":             "Other methods",
    "Asymptotic Analysis":                   "Other methods",
}

EVIDENCE_ORDER = [
    "Phenomenological SC",
    "Microscopic pairing",
    "Field theory & RG",
    "Response & transport",
    "Topological",
    "Junction & interface",
    "Many-body & correlation",
    "Quantum circuits & info",
    "Other methods",
]
EVIDENCE_RANK = {e: i for i, e in enumerate(EVIDENCE_ORDER)}


def is_active(val: str) -> bool:
    return val.strip() not in ("", "0", "0.0", "False", "nan")


def get_evidence(row: dict) -> str:
    active = set()
    for col, category in COLUMN_TO_EVIDENCE.items():
        if col in row and is_active(row[col]):
            active.add(category)
    if not active:
        return "none"
    return " | ".join(sorted(active, key=lambda e: EVIDENCE_RANK.get(e, 99)))


def main():
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        original_fields = reader.fieldnames[:]
        for row in reader:
            rows.append(row)

    if "evidence" in original_fields:
        new_fields = original_fields
        print("'evidence' column already exists — values will be overwritten.")
    else:
        new_fields = original_fields + ["evidence"]

    stats = {}
    for row in rows:
        ev = get_evidence(row)
        row["evidence"] = ev
        stats[ev] = stats.get(ev, 0) + 1

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=new_fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. Wrote {len(rows)} rows to {CSV_PATH}")
    print("\nEvidence distribution (sorted by count):")
    for ev, count in sorted(stats.items(), key=lambda x: -x[1]):
        print(f"  {count:5d}  {ev}")


if __name__ == "__main__":
    main()
