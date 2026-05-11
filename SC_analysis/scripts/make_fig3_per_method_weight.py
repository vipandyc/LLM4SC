#!/usr/bin/env python3
"""
Per-method weighting variant of Figure 3
========================================

Same per-label scheme as `make_fig3_per_label_weight.py`, but operating on
INDIVIDUAL experimental + computational methods (ARPES, DMRG, DFT, NMR, ...)
rather than the 9 aggregated evidence_theory categories.

Method columns are binary 0/1 indicators in SC_final_data_5k.csv.  The 28
"core" methods used here are the same set defined in add_evidence_columns.py
(6 computational + 22 experimental).

Per-cell weighting (anchor = column = method M, threshold at YEAR_MIN(M)):
    w(r, M) = 0                                if year(r) <  YEAR_MIN(M)
            = exp(LAMBDA * (year(r) - YEAR_MIN(M)))   else

Outputs (all in output/figures_newWeight/):
    figure3_per_method_weight_N5.png    - 2x2: family/mech x method, per-label + delta
    figure3_per_method_weight_p10.png   - same, with p10 anchors
    comparison_fam_method.png           - 1x4: flat / global / per-label-N5 / p10
    comparison_mech_method.png          - 1x4
    year_min_method.csv                 - method, YEAR_MIN_N5, YEAR_MIN_p10, n_papers
    method_matrices.npz                 - all matrices for downstream use
"""

import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import defaultdict
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────────
ROOT     = Path(__file__).parent.parent
CSV_PATH = ROOT / "SC_final_data_5k.csv"
OUT_DIR  = ROOT / "output" / "figures_newWeight"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── canonical orders (mirrors fig_common) ─────────────────────────────────────
DISP_FAMS = [
    "cuprate", "iron-based", "heavy-fermion", "nickelate",
    "hydrogen", "kagome", "ruthenate", "elemental", "MgB2", "2D",
    "organic", "A15", "alloy", "fulleride", "oxide", "carbide/nitride",
]
MECH_ORDER = [
    "pure el-ph coupling", "bipolaron el-ph coupling",
    "AFM fluctuation", "FM fluctuation", "charge density wave",
    "nematic fluctuation", "plasmon fluctuation",
    "pure el correlation", "spin liquid el correlation",
]
MECH_SHORT = {
    "pure el-ph coupling":       "El-ph",
    "bipolaron el-ph coupling":  "Bipolaron",
    "AFM fluctuation":           "AFM",
    "FM fluctuation":            "FM",
    "charge density wave":       "CDW",
    "nematic fluctuation":       "Nematic",
    "plasmon fluctuation":       "Plasmon",
    "pure el correlation":       "El-corr",
    "spin liquid el correlation":"Spin liq",
}

# ── methods (column name in CSV, short display label) ─────────────────────────
COMPUTATION = [
    ("DFT",                    "DFT"),
    ("DFPT",                   "DFPT"),
    ("QMC",                    "QMC"),
    ("DMFT",                   "DMFT"),
    ("Exact Diagonalization",  "ED"),
    ("DMRG",                   "DMRG"),
]
EXPERIMENT = [
    ("Electrical Resistivity / Transport",     "Resistivity"),
    ("Magnetic Susceptibility / Magnetization","MagSusc"),
    ("Tc Measurement",                         "Tc"),
    ("Magnetoresistance / Magnetotransport",   "MR"),
    ("Microwave Spectroscopy",                 "Microwave"),
    ("Infrared / Optical Spectroscopy",        "IR/Optical"),
    ("SQUID Magnetometry",                     "SQUID"),
    ("Specific Heat / Heat Capacity",          "SpecHeat"),
    ("Neutron Scattering",                     "Neutron"),
    ("ARPES",                                  "ARPES"),
    ("Josephson Junction Measurements",        "JJ-meas"),
    ("STM/STS",                                "STM/STS"),
    ("NMR",                                    "NMR"),
    ("Hall Effect",                            "Hall"),
    ("Raman Spectroscopy",                     "Raman"),
    ("muSR",                                   "muSR"),
    ("Thermal Conductivity",                   "ThermCond"),
    ("Quantum Oscillations",                   "QuantOsc"),
    ("XAS",                                    "XAS"),
    ("RIXS",                                   "RIXS"),
    ("EELS",                                   "EELS"),
    ("RHEED",                                  "RHEED"),
]

METHODS       = COMPUTATION + EXPERIMENT
METHOD_COLS   = [c for c, _ in METHODS]
METHOD_LABELS = [s for _, s in METHODS]
METHOD_IDX    = {c: i for i, (c, _) in enumerate(METHODS)}

FAM_IDX  = {f: i for i, f in enumerate(DISP_FAMS)}
MECH_IDX = {m: i for i, m in enumerate(MECH_ORDER)}
NF, NM, NK = len(DISP_FAMS), len(MECH_ORDER), len(METHODS)

LAMBDA          = 0.05
THRESHOLD_N     = 5
ROBUST_PCT      = 10
GLOBAL_YEAR_MIN = 1956


# ── load data ─────────────────────────────────────────────────────────────────
with open(CSV_PATH, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))


def parse_year(r):
    try:
        return int(r["year"])
    except (ValueError, KeyError, TypeError):
        return None


def methods_of(r):
    """Return list of method-column names where this row's value is '1'."""
    return [c for c in METHOD_COLS if str(r.get(c, "0")).strip() == "1"]


# ── per-label YEAR_MIN ────────────────────────────────────────────────────────
def collect_method_years(rows):
    out = defaultdict(list)
    for r in rows:
        yr = parse_year(r)
        if yr is None:
            continue
        for c in methods_of(r):
            out[c].append(yr)
    return out


def compute_year_min_n(label_to_years, threshold=THRESHOLD_N):
    out = {}
    for L, years in label_to_years.items():
        if not years: continue
        ys = sorted(years)
        out[L] = ys[min(threshold - 1, len(ys) - 1)]
    return out


def compute_year_min_pct(label_to_years, pct=ROBUST_PCT):
    out = {}
    for L, years in label_to_years.items():
        if not years: continue
        ys = sorted(years)
        out[L] = ys[int(len(ys) * pct / 100)]
    return out


method_years = collect_method_years(rows)
method_ymin_n5  = compute_year_min_n(method_years)
method_ymin_p10 = compute_year_min_pct(method_years)
for c in METHOD_COLS:
    method_ymin_n5.setdefault(c,  GLOBAL_YEAR_MIN)
    method_ymin_p10.setdefault(c, GLOBAL_YEAR_MIN)


def w_anchor(year, ymin_L, lam=LAMBDA):
    """Threshold weight: 0 before ymin, exp(lam*(year-ymin)) after."""
    if year < ymin_L:
        return 0.0
    return float(np.exp(lam * (year - ymin_L)))


# ── matrix builders ───────────────────────────────────────────────────────────
def build_fam_method_perlabel(rows, ymin_dict, lam=LAMBDA):
    num = np.zeros((NF, NK))
    den = np.zeros((NF, NK))
    for r in rows:
        yr = parse_year(r)
        if yr is None: continue
        fi = FAM_IDX.get(r.get("family"))
        if fi is None: continue
        my = set(methods_of(r))
        for c, ki in METHOD_IDX.items():
            w = w_anchor(yr, ymin_dict[c], lam)
            den[fi, ki] += w
            if c in my:
                num[fi, ki] += w
    den[den == 0] = 1
    return num / den


def build_mech_method_perlabel(rows, ymin_dict, lam=LAMBDA):
    num = np.zeros((NM, NK))
    den = np.zeros((NM, NK))
    for r in rows:
        yr = parse_year(r)
        if yr is None: continue
        mi = MECH_IDX.get(r.get("mechanism"))
        if mi is None: continue
        my = set(methods_of(r))
        for c, ki in METHOD_IDX.items():
            w = w_anchor(yr, ymin_dict[c], lam)
            den[mi, ki] += w
            if c in my:
                num[mi, ki] += w
    den[den == 0] = 1
    return num / den


def build_fam_method_flat(rows):
    mat   = np.zeros((NF, NK))
    fam_n = np.zeros(NF)
    for r in rows:
        fi = FAM_IDX.get(r.get("family"))
        if fi is None: continue
        fam_n[fi] += 1
        for c in methods_of(r):
            ki = METHOD_IDX.get(c)
            if ki is not None:
                mat[fi, ki] += 1
    fam_n[fam_n == 0] = 1
    return mat / fam_n[:, None]


def build_mech_method_flat(rows):
    mat    = np.zeros((NM, NK))
    mech_n = np.zeros(NM)
    for r in rows:
        mi = MECH_IDX.get(r.get("mechanism"))
        if mi is None: continue
        mech_n[mi] += 1
        for c in methods_of(r):
            ki = METHOD_IDX.get(c)
            if ki is not None:
                mat[mi, ki] += 1
    mech_n[mech_n == 0] = 1
    return mat / mech_n[:, None]


def build_fam_method_global(rows, lam=LAMBDA, year_min=GLOBAL_YEAR_MIN):
    mat   = np.zeros((NF, NK))
    fam_w = np.zeros(NF)
    for r in rows:
        yr = parse_year(r)
        if yr is None: continue
        fi = FAM_IDX.get(r.get("family"))
        if fi is None: continue
        w = float(np.exp(lam * (yr - year_min)))
        fam_w[fi] += w
        for c in methods_of(r):
            ki = METHOD_IDX.get(c)
            if ki is not None:
                mat[fi, ki] += w
    fam_w[fam_w == 0] = 1
    return mat / fam_w[:, None]


def build_mech_method_global(rows, lam=LAMBDA, year_min=GLOBAL_YEAR_MIN):
    mat    = np.zeros((NM, NK))
    mech_w = np.zeros(NM)
    for r in rows:
        yr = parse_year(r)
        if yr is None: continue
        mi = MECH_IDX.get(r.get("mechanism"))
        if mi is None: continue
        w = float(np.exp(lam * (yr - year_min)))
        mech_w[mi] += w
        for c in methods_of(r):
            ki = METHOD_IDX.get(c)
            if ki is not None:
                mat[mi, ki] += w
    mech_w[mech_w == 0] = 1
    return mat / mech_w[:, None]


# ── compute ───────────────────────────────────────────────────────────────────
mat_fk_pl  = build_fam_method_perlabel(rows,  method_ymin_n5)
mat_fk_pr  = build_fam_method_perlabel(rows,  method_ymin_p10)
mat_fk_fl  = build_fam_method_flat(rows)
mat_fk_gl  = build_fam_method_global(rows)

mat_mk_pl  = build_mech_method_perlabel(rows, method_ymin_n5)
mat_mk_pr  = build_mech_method_perlabel(rows, method_ymin_p10)
mat_mk_fl  = build_mech_method_flat(rows)
mat_mk_gl  = build_mech_method_global(rows)

delta_fk    = mat_fk_pl - mat_fk_fl
delta_fk_r  = mat_fk_pr - mat_fk_fl
delta_mk    = mat_mk_pl - mat_mk_fl
delta_mk_r  = mat_mk_pr - mat_mk_fl


# ── write YEAR_MIN table + matrices ───────────────────────────────────────────
def write_csv(path, rows_iter, header):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows_iter:
            w.writerow(r)

write_csv(OUT_DIR / "year_min_method.csv",
          [(short, full,
            "computational" if (full, short) in COMPUTATION else "experimental",
            method_ymin_n5[full], method_ymin_p10[full],
            len(method_years.get(full, [])))
           for full, short in METHODS],
          ["short_label", "csv_column", "type", "YEAR_MIN_N5", "YEAR_MIN_p10", "n_papers"])

np.savez(OUT_DIR / "method_matrices.npz",
         fam_method_perlabel_n5=mat_fk_pl, fam_method_perlabel_p10=mat_fk_pr,
         fam_method_flat=mat_fk_fl,        fam_method_global=mat_fk_gl,
         mech_method_perlabel_n5=mat_mk_pl, mech_method_perlabel_p10=mat_mk_pr,
         mech_method_flat=mat_mk_fl,        mech_method_global=mat_mk_gl,
         delta_fk=delta_fk, delta_fk_r=delta_fk_r,
         delta_mk=delta_mk, delta_mk_r=delta_mk_r)


# ── heatmap helper ────────────────────────────────────────────────────────────
def draw_heatmap(ax, mat, row_lbl, col_lbl, cmap, vmin, vmax, title,
                 cbar_label="", annot_frac=0.10, diverging=False, fmt=".2f"):
    im = ax.imshow(mat, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(col_lbl)))
    ax.set_xticklabels(col_lbl, rotation=55, ha="right", fontsize=6.5)
    ax.set_yticks(range(len(row_lbl)))
    ax.set_yticklabels(row_lbl, fontsize=7.5)
    ax.set_title(title, fontsize=9.0, fontweight="bold", pad=4)
    # mark divider between computational and experimental (after column 5)
    ax.axvline(len(COMPUTATION) - 0.5, color="black", lw=0.8, alpha=0.5)
    thresh = vmax * annot_frac
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            if np.isnan(v): continue
            show = (abs(v) >= thresh) if diverging else (v >= thresh)
            if show:
                tc = "white" if (abs(v) if diverging else v) >= vmax * 0.60 else "black"
                ax.text(j, i, f"{v:{fmt}}", ha="center", va="center",
                        fontsize=4.8, color=tc)
    plt.colorbar(im, ax=ax, label=cbar_label, shrink=0.84, pad=0.02)
    return im


FML  = DISP_FAMS
MLS  = [MECH_SHORT[m] for m in MECH_ORDER]
KLS  = METHOD_LABELS


# ── main combined figures (N5 and p10 variants) ───────────────────────────────
def make_main_figure(out_path, suffix, mat_fk, mat_mk, delta_fk_use, delta_mk_use, ymin_dict):
    fig, axes = plt.subplots(2, 2, figsize=(22, 14))
    fig.suptitle(
        f"Figure 3 (per-METHOD weighting, {suffix}) - recency anchored to each method's emergence\n"
        f"weight  w(r,M) = 0 if year<YEAR_MIN(M) else exp({LAMBDA} * (year - YEAR_MIN(M)))",
        fontsize=12, fontweight="bold", y=0.998,
    )
    plt.subplots_adjust(hspace=0.55, wspace=0.30)

    vmax_fk = max(mat_fk.max(), 0.01)
    draw_heatmap(axes[0, 0], mat_fk, FML, KLS, "YlOrRd", 0, vmax_fk,
                 f"Family x Method (per-label, {suffix})",
                 cbar_label="fraction (per-label)", annot_frac=0.06)

    vmax_mk = max(mat_mk.max(), 0.01)
    draw_heatmap(axes[0, 1], mat_mk, MLS, KLS, "YlOrRd", 0, vmax_mk,
                 f"Mechanism x Method (per-label, {suffix})",
                 cbar_label="fraction (per-label)", annot_frac=0.06)

    lim = max(abs(delta_fk_use).max(), 1e-6)
    draw_heatmap(axes[1, 0], delta_fk_use, FML, KLS, "RdBu_r", -lim, lim,
                 f"Delta Family x Method (per-label - flat)",
                 cbar_label="delta fraction", annot_frac=0.15, diverging=True)

    lim = max(abs(delta_mk_use).max(), 1e-6)
    draw_heatmap(axes[1, 1], delta_mk_use, MLS, KLS, "RdBu_r", -lim, lim,
                 f"Delta Mechanism x Method (per-label - flat)",
                 cbar_label="delta fraction", annot_frac=0.15, diverging=True)

    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


make_main_figure(OUT_DIR / "figure3_per_method_weight_N5.png",
                 f"N={THRESHOLD_N}", mat_fk_pl, mat_mk_pl, delta_fk,   delta_mk,   method_ymin_n5)
make_main_figure(OUT_DIR / "figure3_per_method_weight_p10.png",
                 f"p{ROBUST_PCT}",   mat_fk_pr, mat_mk_pr, delta_fk_r, delta_mk_r, method_ymin_p10)


# ── YEAR_MIN diagnostic for methods ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 8))
y_n5  = [method_ymin_n5[c]              for c, _ in METHODS]
y_p10 = [method_ymin_p10[c]             for c, _ in METHODS]
ns    = [len(method_years.get(c, []))   for c, _ in METHODS]

colors = ["steelblue"] * len(COMPUTATION) + ["darkorange"] * len(EXPERIMENT)
ax.barh(range(NK), y_n5, color=colors, alpha=0.85, label=f"N={THRESHOLD_N}")
ax.scatter(y_p10, range(NK), color="black", marker="D", s=22, zorder=5, label=f"p{ROBUST_PCT}")
ax.set_yticks(range(NK))
ax.set_yticklabels(KLS, fontsize=8)
ax.invert_yaxis()
ax.set_xlim(1955, 2026)
ax.axvline(GLOBAL_YEAR_MIN, color="grey", lw=0.6, ls="--")
ax.axhline(len(COMPUTATION) - 0.5, color="black", lw=0.6, alpha=0.4)
for i, (y, p, n) in enumerate(zip(y_n5, y_p10, ns)):
    ax.text(max(y, p) + 0.5, i, f" n={n}", va="center", fontsize=7)
ax.set_xlabel(f"YEAR_MIN  (bar=N{THRESHOLD_N},  diamond=p{ROBUST_PCT})")
ax.set_title("Method emergence years\n(blue=computational, orange=experimental)",
             fontsize=11, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.legend(loc="lower right", fontsize=8)
plt.tight_layout()
plt.savefig(OUT_DIR / "year_min_method_diagnostic.png", dpi=150, bbox_inches="tight")
plt.close()


# ── side-by-side comparison panels ────────────────────────────────────────────
def comparison_panel(out_path, title, mat_flat, mat_global, mat_pl, mat_pr,
                     row_lbl, col_lbl, vmax_flat=None, vmax_w=None):
    if vmax_flat is None:
        vmax_flat = max(mat_flat.max(), 0.01)
    if vmax_w is None:
        vmax_w = max(mat_global.max(), mat_pl.max(), mat_pr.max(), vmax_flat)
    fig, axes = plt.subplots(1, 4, figsize=(34, 7))
    fig.suptitle(title, fontsize=12, fontweight="bold", y=1.0)
    draw_heatmap(axes[0], mat_flat, row_lbl, col_lbl, "Blues", 0, vmax_flat,
                 "Unweighted (flat)", cbar_label="fraction", annot_frac=0.05)
    draw_heatmap(axes[1], mat_global, row_lbl, col_lbl, "YlOrRd", 0, vmax_w,
                 f"Global time-weighted (YEAR_MIN={GLOBAL_YEAR_MIN})",
                 cbar_label="fraction", annot_frac=0.05)
    draw_heatmap(axes[2], mat_pl, row_lbl, col_lbl, "YlOrRd", 0, vmax_w,
                 f"Per-method (N={THRESHOLD_N})",
                 cbar_label="fraction", annot_frac=0.05)
    draw_heatmap(axes[3], mat_pr, row_lbl, col_lbl, "YlOrRd", 0, vmax_w,
                 f"Per-method (p{ROBUST_PCT}, robust)",
                 cbar_label="fraction", annot_frac=0.05)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


comparison_panel(OUT_DIR / "comparison_fam_method.png",
                 "Family x Method - four weighting schemes",
                 mat_fk_fl, mat_fk_gl, mat_fk_pl, mat_fk_pr, FML, KLS)
comparison_panel(OUT_DIR / "comparison_mech_method.png",
                 "Mechanism x Method - four weighting schemes",
                 mat_mk_fl, mat_mk_gl, mat_mk_pl, mat_mk_pr, MLS, KLS)


# ── stdout summary ────────────────────────────────────────────────────────────
print(f"Saved 5 figures + 1 CSV + method_matrices.npz -> {OUT_DIR}")
print()
print(f"{'method':18s}  type            N{THRESHOLD_N}    p{ROBUST_PCT}    n_papers")
for full, short in METHODS:
    typ = "computational" if (full, short) in COMPUTATION else "experimental"
    print(f"  {short:16s}  {typ:14s}  {method_ymin_n5[full]}  {method_ymin_p10[full]}  "
          f"{len(method_years.get(full, []))}")

print()
print(f"Max |delta| (per-method - flat):")
print(f"  fam_method   N{THRESHOLD_N}: {abs(delta_fk).max():.3f}    p{ROBUST_PCT}: {abs(delta_fk_r).max():.3f}")
print(f"  mech_method  N{THRESHOLD_N}: {abs(delta_mk).max():.3f}    p{ROBUST_PCT}: {abs(delta_mk_r).max():.3f}")
print(f"Max |per-method - global|:")
print(f"  fam_method   N{THRESHOLD_N}: {abs(mat_fk_pl-mat_fk_gl).max():.3f}    p{ROBUST_PCT}: {abs(mat_fk_pr-mat_fk_gl).max():.3f}")
print(f"  mech_method  N{THRESHOLD_N}: {abs(mat_mk_pl-mat_mk_gl).max():.3f}    p{ROBUST_PCT}: {abs(mat_mk_pr-mat_mk_gl).max():.3f}")
