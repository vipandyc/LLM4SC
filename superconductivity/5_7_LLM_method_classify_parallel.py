"""
Classify each paper's methods into 128 standardized categories (multi-hot).
Reads GPT_evidence_output from the evidence CSV, sends method info to GPT,
and produces a binary CSV with one column per method category.

Usage:
    python 5_7_LLM_method_classify_parallel.py           # full run
    python 5_7_LLM_method_classify_parallel.py --test 5   # test on 5 rows
"""

import argparse
import json
import os
import yaml
from multiprocessing import Pool, cpu_count
from pathlib import Path

import pandas as pd
from openai import OpenAI
from tqdm import tqdm

# -------------------------------------------------
# Paths
# -------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
INPUT_FILE = ROOT / "data" / "SC_related_cites_010_GPT_evidence.csv"
OUTPUT_FILE = ROOT / "data" / "SC_related_cites_010_method_binary.csv"
EVIDENCE_COLUMN = "GPT_evidence_output"
CLASSIFY_COLUMN = "GPT_method_classify_output"

# -------------------------------------------------
# Load API key from ~/.openaikey.yaml
# -------------------------------------------------
def load_api_key():
    key_file = Path.home() / ".openaikey.yaml"
    if key_file.exists():
        with open(key_file, "r") as f:
            data = yaml.safe_load(f)
        key = data.get("OPENAI_KEY", "")
        if key:
            return key
    env_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if env_key:
        return env_key
    raise RuntimeError(
        "OpenAI API key not found. Either set ~/.openaikey.yaml with "
        "OPENAI_KEY or export OPENAI_API_KEY."
    )


API_KEY = load_api_key()

# -------------------------------------------------
# Load system prompt
# -------------------------------------------------
def load_system_prompt():
    prompt_file = SCRIPT_DIR / "prompt_method_classify" / "prompt_general.md"
    return prompt_file.read_text(encoding="utf-8")


SYSTEM_PROMPT = load_system_prompt()

# -------------------------------------------------
# 128 standardized category names (must match prompt exactly)
# -------------------------------------------------
METHOD_CATEGORIES = [
    # Computational (17)
    "DFT", "DFPT", "Electron-Phonon Coupling Calculations",
    "Band Structure Calculations", "Electronic Structure Calculations",
    "Phonon Calculations", "BCS / Eliashberg", "DMFT",
    "QMC", "Monte Carlo Simulations", "Exact Diagonalization",
    "DMRG", "NRG", "FEM", "Numerical Simulations",
    "Tight-Binding Model", "Fermi Surface Calculations",
    # Experimental (68)
    "ARPES", "Electrical Resistivity / Transport", "TEM", "STM/STS",
    "XRD", "SQUID Magnetometry", "Magnetic Susceptibility / Magnetization",
    "Neutron Scattering", "Specific Heat / Heat Capacity", "Raman Spectroscopy",
    "SEM", "Electron Microscopy (General)", "NMR", "NQR", "muSR",
    "Tc Measurement", "Hc2 Measurement", "Jc Measurement",
    "Magnetoresistance / Magnetotransport", "Hall Effect",
    "XPS", "XAS", "RIXS", "EDX", "EELS", "FTIR",
    "Infrared / Optical Spectroscopy", "Microwave Spectroscopy",
    "Mossbauer Spectroscopy", "ESR/EPR", "Electron Diffraction", "RHEED",
    "Quantum Oscillations", "Thermal Conductivity", "Thermal Expansion",
    "Thermoelectric / Seebeck", "TGA", "DTA", "PLD", "MBE", "CVD",
    "Epitaxial Thin Film Growth", "Sample Synthesis / Characterization",
    "Temperature-Dependent Measurements", "Pressure-Dependent Measurements",
    "Magnetic-Field-Dependent Measurements", "Magnetic-Field-Dependent Transport",
    "Low-Temperature Measurements", "AFM", "MFM", "Scanning SQUID Microscopy",
    "Magneto-Optical Imaging", "Josephson Junction Measurements",
    "I-V Measurements", "Point-Contact Spectroscopy",
    "Andreev Reflection Spectroscopy", "Circuit QED / Superconducting Qubits",
    "SNSPD", "Device Fabrication", "AC Loss Measurements", "MEG", "MRI",
    "Temperature-Dependent Spectroscopy", "DLS", "Electron Microprobe Analysis",
    "Electrostatic Gating", "Cryogenic Testing",
    "Electrical Resistivity Under Pressure",
    # Theoretical / analytic (43)
    "Ginzburg-Landau Theory", "Mean-Field Theory", "Effective Field Theory",
    "Symmetry Analysis", "Linear / Nonlinear Response Theory",
    "Topological Band/Field Theory", "Scaling Analysis",
    "Model Hamiltonian Analysis", "Renormalization Group", "RPA",
    "Perturbation Theory", "Andreev Theory", "Josephson Junction Theory",
    "Phenomenological / Analytical Modeling", "BdG Theory", "Floquet Theory",
    "Bulk-Boundary Correspondence", "Luttinger Liquid Theory",
    "Bean Critical-State Model", "Proximity Effect Theory", "London Theory",
    "Percolation Theory", "Bosonization", "Linear Stability Analysis",
    "Effective Hamiltonian", "Phase Diagram Analysis",
    "AdS/CFT (Holographic Duality)", "RVB Theory", "Two-Fluid Model",
    "Collective Pinning Theory", "Fermi Liquid Theory", "Scattering Theory",
    "Collective Mode Analysis", "Input-Output Theory",
    "Linearized Gap Equation", "Asymptotic Analysis",
    "Green's Function Formalism", "Quantum Measurement Theory",
    "Nonlinear Sigma Model", "t-J Model", "Circuit Quantization",
    "Drude Model", "Anderson Localization Theory",
]

assert len(METHOD_CATEGORIES) == 128, f"Expected 128 categories, got {len(METHOD_CATEGORIES)}"


# -------------------------------------------------
# Build user prompt from evidence JSON
# -------------------------------------------------
def build_user_prompt(evidence_json_str: str) -> str:
    try:
        obj = json.loads(evidence_json_str)
    except Exception:
        return None

    # Extract the method-relevant fields
    subset = {
        "computational_methods": obj.get("computational_methods", []),
        "experimental_methods": obj.get("experimental_methods", []),
        "theoretical_analytic_methods": obj.get("theoretical_analytic_methods", []),
        "method_summary": obj.get("method_summary", "N/A"),
    }

    # Skip if all method lists are empty
    all_methods = (
        (subset["computational_methods"] or [])
        + (subset["experimental_methods"] or [])
        + (subset["theoretical_analytic_methods"] or [])
    )
    if not all_methods:
        return None

    return (
        "Classify the methods in the following evidence extraction "
        "into the standardized categories. Return ONLY the JSON.\n\n"
        + json.dumps(subset, ensure_ascii=False)
    )


# -------------------------------------------------
# Worker function
# -------------------------------------------------
def process_one(args):
    index, evidence_str = args

    user_prompt = build_user_prompt(evidence_str)
    if user_prompt is None:
        # No methods to classify — return empty
        result = json.dumps({"matched_methods": [], "other": []})
        return index, result

    client = OpenAI(api_key=API_KEY)
    try:
        resp = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        out = resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Worker] Error at index {index}: {e}")
        out = None

    return index, out


def _row_needs_classify(df, i):
    v = df.loc[i, CLASSIFY_COLUMN]
    if pd.isna(v):
        return True
    return not str(v).strip()


# -------------------------------------------------
# Parse GPT output into binary columns
# -------------------------------------------------
def parse_classify_output(raw: str) -> dict:
    """Parse the GPT classification output into a dict of {category: 0/1}."""
    row = {cat: 0 for cat in METHOD_CATEGORIES}
    row["other"] = 0
    row["other_details"] = ""

    if not raw or pd.isna(raw):
        return row

    try:
        obj = json.loads(raw)
    except Exception:
        # Try to extract JSON from markdown fences
        import re
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                obj = json.loads(match.group())
            except Exception:
                return row
        else:
            return row

    matched = obj.get("matched_methods", [])
    if isinstance(matched, list):
        for m in matched:
            m_str = str(m).strip()
            if m_str in row:
                row[m_str] = 1

    other_list = obj.get("other", [])
    if isinstance(other_list, list) and other_list:
        row["other"] = 1
        row["other_details"] = "; ".join(str(x) for x in other_list)

    return row


def build_binary_csv(df: pd.DataFrame) -> pd.DataFrame:
    """Convert the classify column into a binary DataFrame."""
    records = []
    for i, raw in enumerate(df[CLASSIFY_COLUMN]):
        parsed = parse_classify_output(raw)
        parsed["id"] = df.loc[i, "id"]
        records.append(parsed)

    binary_df = pd.DataFrame(records)
    # Reorder: id first, then categories, then other
    cols = ["id"] + METHOD_CATEGORIES + ["other", "other_details"]
    return binary_df[cols]


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", type=int, default=0,
                        help="Test mode: only process N rows")
    args = parser.parse_args()

    # Load or create working dataframe
    if os.path.exists(OUTPUT_FILE):
        # Check if we have raw classify output saved
        raw_file = OUTPUT_FILE.with_name(
            OUTPUT_FILE.stem + "_raw.csv"
        )
        if raw_file.exists():
            df = pd.read_csv(raw_file)
            print(f"Loaded existing raw checkpoint ({len(df)} rows).")
        else:
            # First run, load from evidence
            df = pd.read_csv(INPUT_FILE)
            if CLASSIFY_COLUMN not in df.columns:
                df[CLASSIFY_COLUMN] = None
    else:
        raw_file = OUTPUT_FILE.with_name(
            OUTPUT_FILE.stem + "_raw.csv"
        )
        if raw_file.exists():
            df = pd.read_csv(raw_file)
            print(f"Loaded existing raw checkpoint ({len(df)} rows).")
        else:
            df = pd.read_csv(INPUT_FILE)
            if CLASSIFY_COLUMN not in df.columns:
                df[CLASSIFY_COLUMN] = None

    raw_file = OUTPUT_FILE.with_name(OUTPUT_FILE.stem + "_raw.csv")

    # Build task list
    tasks = [
        (i, df.loc[i, EVIDENCE_COLUMN])
        for i in range(len(df))
        if _row_needs_classify(df, i)
    ]

    if args.test > 0:
        tasks = tasks[: args.test]
        print(f"TEST MODE: processing {len(tasks)} rows only.")

    print(f"Total remaining items: {len(tasks)}")

    if tasks:
        N_WORKERS = min(8, cpu_count())
        if args.test:
            N_WORKERS = min(2, len(tasks))
        print(f"Using {N_WORKERS} parallel workers.")

        with Pool(N_WORKERS) as pool:
            for idx, out in tqdm(
                pool.imap_unordered(process_one, tasks), total=len(tasks)
            ):
                df.loc[idx, CLASSIFY_COLUMN] = out

                if idx % 32 == 0:
                    df.to_csv(raw_file, index=False)

        # Save raw output
        df.to_csv(raw_file, index=False)
        print(f"Raw classify output saved to {raw_file}")

    # Convert to binary CSV
    print("Building binary CSV...")
    binary_df = build_binary_csv(df)
    binary_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Binary method CSV saved to {OUTPUT_FILE}")
    print(f"  Shape: {binary_df.shape}")
    print(f"  Papers with 'other' methods: {binary_df['other'].sum()}")


if __name__ == "__main__":
    main()
