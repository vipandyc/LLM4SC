#!/usr/bin/env python3
"""
Per-theoretical-method weighting variant of Figure 3
====================================================

Same per-label scheme as `make_fig3_per_label_weight.py` and
`make_fig3_per_method_weight.py`, but operating on INDIVIDUAL theoretical
methods (Ginzburg-Landau Theory, Mean-Field Theory, BdG Theory,
Renormalization Group, AdS/CFT, RVB Theory, t-J Model, Floquet Theory, ...)
rather than the 9 aggregated evidence_theory categories.

These are the 38 theoretical-method binary columns whose categorization is
defined in `add_evidence_column.py`'s COLUMN_TO_EVIDENCE dict.  We drop
columns with n<10 papers (Bean Critical-State Model n=4, Input-Output
Theory n=3, Circuit Quantization n=3, Quantum Measurement Theory n=0,
Percolation Theory n=9) because their YEAR_MIN anchors are dominated by
single-paper variation.  That leaves 34 theoretical methods.

Per-cell weighting (same threshold + exp form as the other scripts):
    w(r, T) = 0                                if year(r) <  YEAR_MIN(T)
            = exp(LAMBDA * (year(r) - YEAR_MIN(T)))   else

Outputs (all in output/figures_newWeight/):
    figure3_per_theory_method_weight_N5.png   - 2x1: family/mech x theory-method
    figure3_per_theory_method_weight_p10.png  - same with p10 anchors
    comparison_fam_theory_method.png          - 1x4: flat / global / N5 / p10
    comparison_mech_theory_method.png         - 1x4
    year_min_theory_method_diagnostic.png     - YEAR_MIN bar chart
    year_min_theory_method.csv                - method, category, YEAR_MIN_*, n_papers
    theory_method_matrices.npz                - all matrices for downstream use
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

# ── canonical orders ──────────────────────────────────────────────────────────
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

# ── theoretical methods ───────────────────────────────────────────────────────
# (csv_column, short_label, evidence_category)  — order = category, then within
THEORY_METHODS = [
    # Phenomenological SC
    ("Ginzburg-Landau Theory",                  "GL",            "Phenom."),
    ("Phenomenological / Analytical Modeling",  "Phenom./Anal.", "Phenom."),
    ("London Theory",                           "London",        "Phenom."),
    ("Two-Fluid Model",                         "2-fluid",       "Phenom."),
    ("Collective Pinning Theory",               "ColPin",        "Phenom."),
    # Microscopic pairing
    ("Mean-Field Theory",                       "MFT",           "Micro.pair"),
    ("BdG Theory",                              "BdG",           "Micro.pair"),
    ("Proximity Effect Theory",                 "Prox.",         "Micro.pair"),
    ("Collective Mode Analysis",                "ColMode",       "Micro.pair"),
    ("Linearized Gap Equation",                 "LinGap",        "Micro.pair"),
    # Field theory & RG
    ("Effective Field Theory",                  "EFT",           "FT&RG"),
    ("Scaling Analysis",                        "Scaling",       "FT&RG"),
    ("Renormalization Group",                   "RG",            "FT&RG"),
    ("RPA",                                     "RPA",           "FT&RG"),
    ("Perturbation Theory",                     "Pert.",         "FT&RG"),
    ("AdS/CFT (Holographic Duality)",           "AdS/CFT",       "FT&RG"),
    ("Nonlinear Sigma Model",                   "NLSM",          "FT&RG"),
    # Response & transport
    ("Linear / Nonlinear Response Theory",      "Resp.",         "Resp.&Trans."),
    ("Green's Function Formalism",              "Green",         "Resp.&Trans."),
    ("Drude Model",                             "Drude",         "Resp.&Trans."),
    ("Anderson Localization Theory",            "AndLoc",        "Resp.&Trans."),
    # Topological
    ("Topological Band/Field Theory",           "TopBand",       "Topol."),
    ("Floquet Theory",                          "Floquet",       "Topol."),
    ("Bulk-Boundary Correspondence",            "BulkBnd",       "Topol."),
    # Junction & interface
    ("Andreev Theory",                          "Andreev",       "Junction"),
    ("Josephson Junction Theory",               "JJ-thy",        "Junction"),
    ("Scattering Theory",                       "Scatt.",        "Junction"),
    # Many-body & correlation
    ("Luttinger Liquid Theory",                 "Luttinger",     "Many-body"),
    ("Bosonization",                            "Bosoniz.",      "Many-body"),
    ("RVB Theory",                              "RVB",           "Many-body"),
    ("Fermi Liquid Theory",                     "FL",            "Many-body"),
    ("t-J Model",                               "t-J",           "Many-body"),
    # Other methods
    ("Linear Stability Analysis",               "LinStab",       "Other"),
    ("Asymptotic Analysis",                     "Asympt.",       "Other"),
]

# excluded for n<10:
#   ("Bean Critical-State Model",               "Bean",          "Phenom.")     n=4
#   ("Input-Output Theory",                     "I/O",           "Quantum")     n=3
#   ("Quantum Measurement Theory",              "QMeas",         "Quantum")     n=0
#   ("Circuit Quantization",                    "CircQ",         "Quantum")     n=3
#   ("Percolation Theory",                      "Perc.",         "Other")       n=9

THEORY_COLS   = [c for c, _, _ in THEORY_METHODS]
THEORY_LABELS = [s for _, s, _ in THEORY_METHODS]
THEORY_CATS   = [g for _, _, g in THEORY_METHODS]
THEORY_IDX    = {c: i for i, (c, _, _) in enumerate(THEORY_METHODS)}

# Category boundaries (for vertical dividers in the heatmap)
CAT_BOUNDS = []
prev = None
for i, g in enumerate(THEORY_CATS):
    if prev is not None and g != prev:
        CAT_BOUNDS.append(i - 0.5)
    prev = g

FAM_IDX  = {f: i for i, f in enumerate(DISP_FAMS)}
MECH_IDX = {m: i for i, m in enumerate(MECH_ORDER)}
NF, NM, NT = len(DISP_FAMS), len(MECH_ORDER), len(THEORY_METHODS)

LAMBDA          = 0.05
THRESHOLD_N     = 5
ROBUST_PCT      = 10
GLOBAL_YEAR_MIN = 1956
N_CUTOFF        = 10  # documented; columns excluded above

# ── load data ─────────────────────────────────────────────────────────────────
with open(CSV_PATH, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))


def parse_year(r):
    try:
        return int(r["year"])
    except (ValueError, KeyError, TypeError):
        return None


def theories_of(r):
    """Return list of theory-column names where this row's value is '1'."""
    return [c for c in THEORY_COLS if str(r.get(c, "0")).strip() == "1"]


# ── per-label YEAR_MIN ────────────────────────────────────────────────────────
def collect_theory_years(rows):
    out = defaultdict(list)
    for r in rows:
        yr = parse_year(r)
        if yr is None:
            continue
        for c in theories_of(r):
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


theory_years = collect_theory_years(rows)
ymin_n5  = compute_year_min_n(theory_years)
ymin_p10 = compute_year_min_pct(theory_years)
for c in THEORY_COLS:
    ymin_n5.setdefault(c,  GLOBAL_YEAR_MIN)
    ymin_p10.setdefault(c, GLOBAL_YEAR_MIN)


def w_anchor(year, ymin_L, lam=LAMBDA):
    if year < ymin_L:
        return 0.0
    return float(np.exp(lam * (year - ymin_L)))


# ── matrix builders ───────────────────────────────────────────────────────────
def build_fam_theory_perlabel(rows, ymin_dict, lam=LAMBDA):
    num = np.zeros((NF, NT))
    den = np.zeros((NF, NT))
    for r in rows:
        yr = parse_year(r)
        if yr is None: continue
        fi = FAM_IDX.get(r.get("family"))
        if fi is None: continue
        my = set(theories_of(r))
        for c, ti in THEORY_IDX.items():
            w = w_anchor(yr, ymin_dict[c], lam)
            den[fi, ti] += w
            if c in my:
                num[fi, ti] += w
    den[den == 0] = 1
    return num / den


def build_mech_theory_perlabel(rows, ymin_dict, lam=LAMBDA):
    num = np.zeros((NM, NT))
    den = np.zeros((NM, NT))
    for r in rows:
        yr = parse_year(r)
        if yr is None: continue
        mi = MECH_IDX.get(r.get("mechanism"))
        if mi is None: continue
        my = set(theories_of(r))
        for c, ti in THEORY_IDX.items():
            w = w_anchor(yr, ymin_dict[c], lam)
            den[mi, ti] += w
            if c in my:
                num[mi, ti] += w
    den[den == 0] = 1
    return num / den


def build_fam_theory_flat(rows):
    mat   = np.zeros((NF, NT))
    fam_n = np.zeros(NF)
    for r in rows:
        fi = FAM_IDX.get(r.get("family"))
        if fi is None: continue
        fam_n[fi] += 1
        for c in theories_of(r):
            ti = THEORY_IDX.get(c)
            if ti is not None:
                mat[fi, ti] += 1
    fam_n[fam_n == 0] = 1
    return mat / fam_n[:, None]


def build_mech_theory_flat(rows):
    mat    = np.zeros((NM, NT))
    mech_n = np.zeros(NM)
    for r in rows:
        mi = MECH_IDX.get(r.get("mechanism"))
        if mi is None: continue
        mech_n[mi] += 1
        for c in theories_of(r):
            ti = THEORY_IDX.get(c)
            if ti is not None:
                mat[mi, ti] += 1
    mech_n[mech_n == 0] = 1
    return mat / mech_n[:, None]


def build_fam_theory_global(rows, lam=LAMBDA, year_min=GLOBAL_YEAR_MIN):
    mat   = np.zeros((NF, NT))
    fam_w = np.zeros(NF)
    for r in rows:
        yr = parse_year(r)
        if yr is None: continue
        fi = FAM_IDX.get(r.get("family"))
        if fi is None: continue
        w = float(np.exp(lam * (yr - year_min)))
        fam_w[fi] += w
        for c in theories_of(r):
            ti = THEORY_IDX.get(c)
            if ti is not None:
                mat[fi, ti] += w
    fam_w[fam_w == 0] = 1
    return mat / fam_w[:, None]


def build_mech_theory_global(rows, lam=LAMBDA, year_min=GLOBAL_YEAR_MIN):
    mat    = np.zeros((NM, NT))
    mech_w = np.zeros(NM)
    for r in rows:
        yr = parse_year(r)
        if yr is None: continue
        mi = MECH_IDX.get(r.get("mechanism"))
        if mi is None: continue
        w = float(np.exp(lam * (yr - year_min)))
        mech_w[mi] += w
        for c in theories_of(r):
            ti = THEORY_IDX.get(c)
            if ti is not None:
                mat[mi, ti] += w
    mech_w[mech_w == 0] = 1
    return mat / mech_w[:, None]


# ── compute ───────────────────────────────────────────────────────────────────
mat_ft_pl = build_fam_theory_perlabel(rows,  ymin_n5)
mat_ft_pr = build_fam_theory_perlabel(rows,  ymin_p10)
mat_ft_fl = build_fam_theory_flat(rows)
mat_ft_gl = build_fam_theory_global(rows)

mat_mt_pl = build_mech_theory_perlabel(rows, ymin_n5)
mat_mt_pr = build_mech_theory_perlabel(rows, ymin_p10)
mat_mt_fl = build_mech_theory_flat(rows)
mat_mt_gl = build_mech_theory_global(rows)

delta_ft   = mat_ft_pl - mat_ft_fl
delta_ft_r = mat_ft_pr - mat_ft_fl
delta_mt   = mat_mt_pl - mat_mt_fl
delta_mt_r = mat_mt_pr - mat_mt_fl


# ── write CSV + matrices ──────────────────────────────────────────────────────
def write_csv(path, rows_iter, header):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows_iter:
            w.writerow(r)

write_csv(OUT_DIR / "year_min_theory_method.csv",
          [(short, full, cat,
            ymin_n5[full], ymin_p10[full],
            len(theory_years.get(full, [])))
           for full, short, cat in THEORY_METHODS],
          ["short_label", "csv_column", "evidence_category",
           "YEAR_MIN_N5", "YEAR_MIN_p10", "n_papers"])

np.savez(OUT_DIR / "theory_method_matrices.npz",
         fam_theory_perlabel_n5=mat_ft_pl, fam_theory_perlabel_p10=mat_ft_pr,
         fam_theory_flat=mat_ft_fl,        fam_theory_global=mat_ft_gl,
         mech_theory_perlabel_n5=mat_mt_pl, mech_theory_perlabel_p10=mat_mt_pr,
         mech_theory_flat=mat_mt_fl,        mech_theory_global=mat_mt_gl,
         delta_ft=delta_ft, delta_ft_r=delta_ft_r,
         delta_mt=delta_mt, delta_mt_r=delta_mt_r)


# ── heatmap helper ────────────────────────────────────────────────────────────
def draw_heatmap(ax, mat, row_lbl, col_lbl, cmap, vmin, vmax, title,
                 cbar_label="", annot_frac=0.10, diverging=False, fmt=".2f",
                 col_dividers=None):
    im = ax.imshow(mat, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(col_lbl)))
    ax.set_xticklabels(col_lbl, rotation=60, ha="right", fontsize=6.0)
    ax.set_yticks(range(len(row_lbl)))
    ax.set_yticklabels(row_lbl, fontsize=7.5)
    ax.set_title(title, fontsize=9.0, fontweight="bold", pad=4)
    if col_dividers:
        for x in col_dividers:
            ax.axvline(x, color="black", lw=0.6, alpha=0.45)
    thresh = vmax * annot_frac
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            if np.isnan(v): continue
            show = (abs(v) >= thresh) if diverging else (v >= thresh)
            if show:
                tc = "white" if (abs(v) if diverging else v) >= vmax * 0.60 else "black"
                ax.text(j, i, f"{v:{fmt}}", ha="center", va="center",
                        fontsize=4.4, color=tc)
    plt.colorbar(im, ax=ax, label=cbar_label, shrink=0.84, pad=0.02)
    return im


FML = DISP_FAMS
MLS = [MECH_SHORT[m] for m in MECH_ORDER]
TLS = THEORY_LABELS


# ── main combined figures ─────────────────────────────────────────────────────
def make_main_figure(out_path, suffix, mat_ft, mat_mt, delta_ft_use, delta_mt_use):
    fig, axes = plt.subplots(2, 1, figsize=(22, 14))
    fig.suptitle(
        f"Figure 3 (per-THEORY-METHOD weighting, {suffix}) - recency anchored to each theory method's emergence\n"
        f"weight  w(r,T) = 0 if year<YEAR_MIN(T) else exp({LAMBDA} * (year - YEAR_MIN(T)));   "
        f"vertical lines = evidence_theory category boundaries",
        fontsize=12, fontweight="bold", y=0.998,
    )
    plt.subplots_adjust(hspace=0.55)

    vmax_ft = max(mat_ft.max(), 0.01)
    draw_heatmap(axes[0], mat_ft, FML, TLS, "YlOrRd", 0, vmax_ft,
                 f"Family x Theory-Method (per-label, {suffix})",
                 cbar_label="fraction (per-label)", annot_frac=0.06,
                 col_dividers=CAT_BOUNDS)

    lim = max(abs(delta_ft_use).max(), 1e-6)
    draw_heatmap(axes[1], delta_ft_use, FML, TLS, "RdBu_r", -lim, lim,
                 f"Delta Family x Theory-Method (per-label - flat, {suffix})",
                 cbar_label="delta fraction", annot_frac=0.15, diverging=True,
                 col_dividers=CAT_BOUNDS)

    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


def make_mech_figure(out_path, suffix, mat_mt, delta_mt_use):
    fig, axes = plt.subplots(2, 1, figsize=(22, 11))
    fig.suptitle(
        f"Figure 3 (per-THEORY-METHOD weighting, {suffix}) - Mechanism axis\n"
        f"vertical lines = evidence_theory category boundaries",
        fontsize=12, fontweight="bold", y=0.998,
    )
    plt.subplots_adjust(hspace=0.55)

    vmax_mt = max(mat_mt.max(), 0.01)
    draw_heatmap(axes[0], mat_mt, MLS, TLS, "YlOrRd", 0, vmax_mt,
                 f"Mechanism x Theory-Method (per-label, {suffix})",
                 cbar_label="fraction (per-label)", annot_frac=0.06,
                 col_dividers=CAT_BOUNDS)

    lim = max(abs(delta_mt_use).max(), 1e-6)
    draw_heatmap(axes[1], delta_mt_use, MLS, TLS, "RdBu_r", -lim, lim,
                 f"Delta Mechanism x Theory-Method (per-label - flat, {suffix})",
                 cbar_label="delta fraction", annot_frac=0.15, diverging=True,
                 col_dividers=CAT_BOUNDS)

    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


make_main_figure(OUT_DIR / "figure3_per_theory_method_weight_N5.png",
                 f"N={THRESHOLD_N}", mat_ft_pl, mat_mt_pl, delta_ft,   delta_mt)
make_main_figure(OUT_DIR / "figure3_per_theory_method_weight_p10.png",
                 f"p{ROBUST_PCT}",   mat_ft_pr, mat_mt_pr, delta_ft_r, delta_mt_r)

make_mech_figure(OUT_DIR / "figure3_per_theory_method_weight_mech_N5.png",
                 f"N={THRESHOLD_N}", mat_mt_pl, delta_mt)
make_mech_figure(OUT_DIR / "figure3_per_theory_method_weight_mech_p10.png",
                 f"p{ROBUST_PCT}",   mat_mt_pr, delta_mt_r)


# ── YEAR_MIN diagnostic ───────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 11))
y_n5  = [ymin_n5[c]                    for c, _, _ in THEORY_METHODS]
y_p10 = [ymin_p10[c]                   for c, _, _ in THEORY_METHODS]
ns    = [len(theory_years.get(c, [])) for c, _, _ in THEORY_METHODS]

# colour by category
cat_colors = {
    "Phenom.":      "#8da0cb",
    "Micro.pair":   "#fc8d62",
    "FT&RG":        "#66c2a5",
    "Resp.&Trans.": "#e78ac3",
    "Topol.":       "#a6d854",
    "Junction":     "#ffd92f",
    "Many-body":    "#e5c494",
    "Other":        "#b3b3b3",
}
colors = [cat_colors[g] for _, _, g in THEORY_METHODS]

ax.barh(range(NT), y_n5, color=colors, alpha=0.9, label=f"N={THRESHOLD_N}")
ax.scatter(y_p10, range(NT), color="black", marker="D", s=22, zorder=5, label=f"p{ROBUST_PCT}")
ax.set_yticks(range(NT))
ax.set_yticklabels([f"{s}  [{g}]" for _, s, g in THEORY_METHODS], fontsize=7.5)
ax.invert_yaxis()
ax.set_xlim(1955, 2026)
ax.axvline(GLOBAL_YEAR_MIN, color="grey", lw=0.6, ls="--")
for x in CAT_BOUNDS:
    ax.axhline(x, color="black", lw=0.4, alpha=0.4)
for i, (y, p, n) in enumerate(zip(y_n5, y_p10, ns)):
    ax.text(max(y, p) + 0.5, i, f" n={n}", va="center", fontsize=7)
ax.set_xlabel(f"YEAR_MIN  (bar=N{THRESHOLD_N},  diamond=p{ROBUST_PCT})")
ax.set_title(f"Theoretical-method emergence years\n(coloured by evidence_theory category;  n>={N_CUTOFF})",
             fontsize=11, fontweight="bold")
ax.grid(axis="x", alpha=0.3)
ax.legend(loc="lower right", fontsize=8)
plt.tight_layout()
plt.savefig(OUT_DIR / "year_min_theory_method_diagnostic.png", dpi=150, bbox_inches="tight")
plt.close()


# ── side-by-side comparisons ──────────────────────────────────────────────────
def comparison_panel(out_path, title, mat_flat, mat_global, mat_pl, mat_pr,
                     row_lbl, col_lbl, vmax_flat=None, vmax_w=None):
    if vmax_flat is None:
        vmax_flat = max(mat_flat.max(), 0.01)
    if vmax_w is None:
        vmax_w = max(mat_global.max(), mat_pl.max(), mat_pr.max(), vmax_flat)
    fig, axes = plt.subplots(1, 4, figsize=(36, 7))
    fig.suptitle(title, fontsize=12, fontweight="bold", y=1.0)
    draw_heatmap(axes[0], mat_flat, row_lbl, col_lbl, "Blues", 0, vmax_flat,
                 "Unweighted (flat)", cbar_label="fraction", annot_frac=0.05,
                 col_dividers=CAT_BOUNDS)
    draw_heatmap(axes[1], mat_global, row_lbl, col_lbl, "YlOrRd", 0, vmax_w,
                 f"Global time-weighted (YEAR_MIN={GLOBAL_YEAR_MIN})",
                 cbar_label="fraction", annot_frac=0.05, col_dividers=CAT_BOUNDS)
    draw_heatmap(axes[2], mat_pl, row_lbl, col_lbl, "YlOrRd", 0, vmax_w,
                 f"Per-theory-method (N={THRESHOLD_N})",
                 cbar_label="fraction", annot_frac=0.05, col_dividers=CAT_BOUNDS)
    draw_heatmap(axes[3], mat_pr, row_lbl, col_lbl, "YlOrRd", 0, vmax_w,
                 f"Per-theory-method (p{ROBUST_PCT}, robust)",
                 cbar_label="fraction", annot_frac=0.05, col_dividers=CAT_BOUNDS)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()


comparison_panel(OUT_DIR / "comparison_fam_theory_method.png",
                 "Family x Theory-Method - four weighting schemes",
                 mat_ft_fl, mat_ft_gl, mat_ft_pl, mat_ft_pr, FML, TLS)
comparison_panel(OUT_DIR / "comparison_mech_theory_method.png",
                 "Mechanism x Theory-Method - four weighting schemes",
                 mat_mt_fl, mat_mt_gl, mat_mt_pl, mat_mt_pr, MLS, TLS)


# ── summary ───────────────────────────────────────────────────────────────────
print(f"Saved 7 figures + 1 CSV + theory_method_matrices.npz -> {OUT_DIR}")
print()
print(f"{'theory method':28s}  category        N{THRESHOLD_N}    p{ROBUST_PCT}    n_papers")
for full, short, cat in THEORY_METHODS:
    print(f"  {short:26s}  {cat:14s}  {ymin_n5[full]}  {ymin_p10[full]}  "
          f"{len(theory_years.get(full, []))}")

print()
print(f"Max |delta| (per-theory-method - flat):")
print(f"  fam_theory   N{THRESHOLD_N}: {abs(delta_ft).max():.3f}    p{ROBUST_PCT}: {abs(delta_ft_r).max():.3f}")
print(f"  mech_theory  N{THRESHOLD_N}: {abs(delta_mt).max():.3f}    p{ROBUST_PCT}: {abs(delta_mt_r).max():.3f}")
print(f"Max |per-theory-method - global|:")
print(f"  fam_theory   N{THRESHOLD_N}: {abs(mat_ft_pl-mat_ft_gl).max():.3f}    p{ROBUST_PCT}: {abs(mat_ft_pr-mat_ft_gl).max():.3f}")
print(f"  mech_theory  N{THRESHOLD_N}: {abs(mat_mt_pl-mat_mt_gl).max():.3f}    p{ROBUST_PCT}: {abs(mat_mt_pr-mat_mt_gl).max():.3f}")
