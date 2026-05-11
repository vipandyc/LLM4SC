#!/usr/bin/env python3
"""
Add two new columns to SC_final_data_5k.csv, inserted just before 'year':

  evidence_computation  — pipe-separated list of active computational methods,
                          or 'none' if none are flagged.
                          Methods checked: DFT, DFPT, QMC, DMFT, Exact Diagonalization, DMRG

  evidence_experiment   — pipe-separated list of active experimental methods,
                          or 'none' if none are flagged.
                          Methods checked: see EXPERIMENT_COLS below.
"""

import csv
from pathlib import Path

CSV_PATH = Path("/home/wenhaohe/scratch/RevGPT_dev/SC_analysis/SC_final_data_5k.csv")

# ── column mappings ────────────────────────────────────────────────────────────
COMPUTATION_COLS = [
    "DFT",
    "DFPT",
    "QMC",
    "DMFT",
    "Exact Diagonalization",
    "DMRG",
]

EXPERIMENT_COLS = [
    "Electrical Resistivity / Transport",
    "Magnetic Susceptibility / Magnetization",
    "Tc Measurement",
    "Magnetoresistance / Magnetotransport",
    "Microwave Spectroscopy",
    "Infrared / Optical Spectroscopy",
    "SQUID Magnetometry",
    "Specific Heat / Heat Capacity",
    "Neutron Scattering",
    "ARPES",
    "Josephson Junction Measurements",
    "STM/STS",
    "NMR",
    "Hall Effect",
    "Raman Spectroscopy",
    "muSR",
    "Thermal Conductivity",
    "Quantum Oscillations",
    "XAS",
    "RIXS",
    "EELS",
    "RHEED",
]

# short labels for filling (same order as above)
COMPUTATION_LABELS = [
    "DFT", "DFPT", "QMC", "DMFT", "ED", "DMRG",
]

EXPERIMENT_LABELS = [
    "Electrical Resistivity", "Magnetic Susceptibility", "Tc Measurement",
    "Magnetoresistance", "Microwave Spectroscopy", "Infrared / Optical Spectroscopy",
    "SQUID", "Specific Heat", "Neutron Scattering", "ARPES",
    "Josephson Junction", "STM/STS", "NMR", "Hall Effect", "Raman",
    "muSR", "Thermal Conductivity", "Quantum Oscillation", "XAS", "RIXS",
    "EELS", "RHEED",
]


def active_methods(row, cols, labels):
    """Return ' | '-joined labels for columns whose value is '1', else 'none'."""
    active = [lbl for col, lbl in zip(cols, labels)
              if str(row.get(col, "0")).strip() == "1"]
    return " | ".join(active) if active else "none"


def main():
    # read
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    # insert new columns just before 'year'
    year_idx = fieldnames.index("year")
    new_fields = fieldnames[:year_idx] + \
                 ["evidence_computation", "evidence_experiment"] + \
                 fieldnames[year_idx:]

    # fill values
    for row in rows:
        row["evidence_computation"] = active_methods(row, COMPUTATION_COLS, COMPUTATION_LABELS)
        row["evidence_experiment"]  = active_methods(row, EXPERIMENT_COLS,  EXPERIMENT_LABELS)

    # write back
    tmp = CSV_PATH.with_suffix(".tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=new_fields)
        writer.writeheader()
        writer.writerows(rows)
    tmp.replace(CSV_PATH)

    # quick summary
    comp_filled = sum(1 for r in rows if r["evidence_computation"] != "none")
    exp_filled  = sum(1 for r in rows if r["evidence_experiment"]  != "none")
    print(f"Done. {len(rows)} rows written → {CSV_PATH}")
    print(f"  evidence_computation filled: {comp_filled} / {len(rows)}")
    print(f"  evidence_experiment  filled: {exp_filled}  / {len(rows)}")


if __name__ == "__main__":
    main()
