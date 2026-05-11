#!/usr/bin/env python3
"""
Recompute the 'family' column in SC_final_data_5k.csv using the updated
infer_family() logic (stdlib only — no pandas/seaborn required).

Run this whenever infer_family() in add_family_column.py is updated.
"""

import csv
import json
import ast
from pathlib import Path
from collections import Counter

CSV_PATH = Path(__file__).parent.parent / "SC_final_data_5k.csv"


def load_gpt_object(text: str) -> dict:
    if not text or text.strip() in ("", "{}", "nan"):
        return {}
    try:
        return json.loads(text)
    except Exception:
        pass
    try:
        return ast.literal_eval(text)
    except Exception:
        return {}


def infer_family(system: str) -> str:
    """
    Canonical family classifier — keep in sync with add_family_column.py.
    Priority order matters: first match wins.
    """
    s = (system or "").lower()

    # ── named families ────────────────────────────────────────────────────
    if any(token in s for token in [
        "cuprate", "yba", "bi2sr2ca", "la2-xsrxcuo4", "cuo2", "hgba2",
        "lscbo", "bi-2212", "bi-2223", "tl-2201", "tl2ba2",
    ]):
        return "cuprate"
    if any(token in s for token in [
        "fe-based", "iron-based", "fese", "pnictide", "lifeas", "feas",
        "lafeaso", "bafe2as2", "smfeaso", "ndfeaso", "iron pnictide",
    ]):
        return "iron-based"
    if any(token in s for token in [
        "heavy-fermion", "cecoin5", "upt3", "cecu2si2", "cerhin5", "urf",
        "ube13", "kondo lattice", "heavy fermion",
    ]):
        return "heavy-fermion"
    if any(token in s for token in [
        "nickelate", "la3ni2o7", "la4ni3o10", "ndnio2", "infinite-layer nickel",
        "prni", "lanio",
    ]):
        return "nickelate"
    if any(token in s for token in [
        "h3s", "sulfur hydride", "high-pressure hydride", "superhydride",
        "hydrogen-rich high-pressure", "high-pressure hydrogen-rich",
        "lah10", "yh6", "csh", "hydride superconductor",
    ]):
        return "hydrogen"
    if any(token in s for token in [
        "kagome", "av3sb5", "csv3sb5", "rbv3sb5", "kv3sb5", "cov3sb5",
    ]):
        return "kagome"
    if any(token in s for token in ["ruthenate", "sr2ruo4"]):
        return "ruthenate"

    # ── A15 intermetallic compounds (β-W structure) ───────────────────────
    # Must come before elemental to avoid Nb/V being caught there first
    if any(token in s for token in [
        "a15 ", "a-15", "a15 compound", "a15 superconductor",
        "nb3sn", "nb3ge", "nb3al", "nb3ga", "nb3sb",
        "v3si", "v3ge", "v3ga", "v3co",
        "β-tungsten", "beta-tungsten", "β-w structure", "beta-w structure",
    ]):
        return "A15"

    # ── fullerides (alkali-doped C60) ─────────────────────────────────────
    if any(token in s for token in [
        "c60", "fullerid", "fullerene", "a3c60", "k3c60", "rb3c60",
        "kxc60", "alkali-doped c60", "alkali metal fullerid",
        "alkali-intercalated c60",
    ]):
        return "fulleride"

    # ── oxide superconductors (incl. bismuthates) ─────────────────────────
    if any(token in s for token in [
        "srtio3", "liti2o4", "litio2o4", "spinel oxide",
        "bismuthate", "babio3", "bapb", "ba0.6k0.4bio3", "ba1-xkxbio3",
        "bkbo", "baxk1-xbio3", "ba0.5k0.5bio3", "ba0.9", "babixpb",
        "bapb1-xbixo3",
    ]):
        return "oxide"

    # ── transition-metal carbides and nitrides ────────────────────────────
    if any(token in s for token in [
        "transition-metal carbide", "transition metal carbide",
        "transition-metal nitride", "transition metal nitride",
        "niobium nitride", "niobium carbide", "titanium nitride",
        "nbnx", "nbc;", " nbc,", "nbc (", "vn;", "vn,", "tan;", "tan,",
        "hfc;", "hfc,", "moc;", "moc,", "mon;", "mon,",
        "nbcx", "tin thin film", "titanium nitride",
    ]):
        return "carbide/nitride"

    # ── MgB2 ─────────────────────────────────────────────────────────────
    if any(token in s for token in ["mgb2", "mgb₂", "magnesium diboride", "diboride"]):
        return "MgB2"

    # ── 2D / moiré / van-der-Waals ───────────────────────────────────────
    if any(token in s for token in [
        "monolayer", "twisted bilayer", "twisted graphene", "moiré", "moire",
        "graphene", "transition metal dichalcogenide", "tmdc", "dichalcogenide",
        "2d superconductor", "two-dimensional superconductor",
        "2d material", "two-dimensional material", "van der waals",
        "nbse2", "nbs2", "mos2", "ws2", "mote2", "wse2",
    ]):
        return "2D"

    # ── elemental metals (expanded) ───────────────────────────────────────
    if any(token in s for token in [
        "elemental superconductor", "elemental superconductors",
        "elemental metal", "elemental metals",
        "conventional superconductor", "conventional metallic",
        "superconducting metal", "superconducting metals",
        "metallic superconductor",
        "simple metal", "simple metals",
        "conventional bcs", "bcs-type superconductor", "bcs type superconductor",
        "conventional low-tc", "low-tc metal",
        "lead (pb)", "tin (sn)", "niobium (nb)", "tantalum (ta)",
        "aluminum (al)", "aluminium (al)", "indium (in)", "gallium (ga)",
        "mercury (hg)", "hg (mercury)", "thallium (tl)", "rhenium (re)",
        "cadmium (cd)", "zinc (zn)", "molybdenum (mo)", "osmium (os)",
        "vanadium (v)",
        "niobium", "tantalum", "mercury", "indium", "gallium",
        "thallium", "cadmium", "rhenium", "molybdenum", "osmium",
        "vanadium", "aluminum", "aluminium",
        "lead superconductor", "tin superconductor",
        "palladium hydride", "palladium deuteride", "pdh", "pdd",
    ]):
        return "elemental"

    # ── metallic alloys (non-A15, non-elemental) ──────────────────────────
    if any(token in s for token in [
        "transition-metal alloy", "transition metal alloy",
        "binary alloy", "metallic alloy", "alloy superconductor",
        "alloy series", "superconducting alloy",
    ]):
        return "alloy"

    # ── general theory (abstract models, no specific material) ───────────
    if any(token in s for token in [
        "hubbard model", "t-j model", "hubbard-heisenberg", "hubbard and t-j",
        "attractive-u hubbard", "negative-u hubbard", "half-filled hubbard",
        "extended hubbard", "two-dimensional hubbard", "2d hubbard",
        "1d hubbard", "3d hubbard", "hubbard cluster",
        "generic superconductor", "generic fermion", "general superconductor",
        "bcs model", "bcs framework", "homogeneous bcs",
        "infinitely extended superconductor", "model superconductor",
        "generic strong-coupling", "electron gas", "fermi gas",
        "fermion gas", "charged bose gas", "jellium",
        "tight-binding electronic system", "anyon", "fractional statistic",
        "fractional quantum hall", "chern-simons",
        "nonlinear spinor", "nambu-jona-lasinio", "particle physics (nucleon",
    ]):
        return "general-theory"

    if "organic" in s:
        return "organic"
    if s.strip() in {"", "n/a"}:
        return "unknown"
    return "other"


def main():
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames[:]
        for row in reader:
            rows.append(row)

    old_counts = Counter(r["family"] for r in rows)

    for row in rows:
        obj = load_gpt_object(row.get("opinion_scores_dict", ""))
        system = obj.get("system", "")
        row["family"] = infer_family(system)

    new_counts = Counter(r["family"] for r in rows)

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. Rewrote {len(rows)} rows → {CSV_PATH}\n")
    print(f"{'family':<22}  {'before':>7}  {'after':>7}  {'delta':>7}")
    print("-" * 50)
    all_fams = sorted(set(old_counts) | set(new_counts))
    for fam in all_fams:
        o, n = old_counts.get(fam, 0), new_counts.get(fam, 0)
        print(f"{fam:<22}  {o:>7}  {n:>7}  {n-o:>+7}")


if __name__ == "__main__":
    main()
