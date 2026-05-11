#!/usr/bin/env python3
"""
Figure 3 (per-label weighting variant)
======================================

Recency weighting anchored to each label's own emergence year, not a global
1956 anchor.  See companion README.md in output/figures_newWeight/.

For each label L (mechanism or evidence-theory category):
    YEAR_MIN(L) = year by which the cumulative count of papers carrying L
                  first reaches THRESHOLD_N (default 5).

Per-cell weight (anchor = column label) — THRESHOLDED:
    w(r, L) = 0                                   if year(r) < YEAR_MIN(L)
             = exp(LAMBDA * (year(r) - YEAR_MIN(L)))   if year(r) >= YEAR_MIN(L)

Why threshold?  Without it, w factors as exp(LAMBDA*year) * exp(-LAMBDA*YEAR_MIN(L)),
i.e. weight = A_p * B_L.  In any same-anchor ratio (num/den) the per-column
B_L cancels exactly, so an un-thresholded "per-label" matrix collapses to the
global time-weighted matrix.  Thresholding pre-emergence papers to zero
breaks this factorization and lets cells differ meaningfully across columns.

Each cell uses its column-label's clock, so cells in a row are NOT on a
common scale.  Cell value = "weighted fraction within the column-label's
mature era".  See README for caveats.

Outputs (all in output/figures_newWeight/):
    figure3_per_label_weight.png   - 2x3 main panel (per-label + delta)
    year_min_diagnostic.png        - bar chart of YEAR_MIN(L) per label
    comparison_fam_mech.png        - 1x3 side-by-side (flat / global / per-label)
    comparison_fam_evid.png        - 1x3 side-by-side
    comparison_mech_evid.png       - 1x3 side-by-side
    year_min_mechanism.csv         - YEAR_MIN per mechanism + n_papers
    year_min_evidence.csv          - YEAR_MIN per evidence category + n_papers
    year_min_family.csv            - YEAR_MIN per family + n_papers
    matrices.npz                   - all matrices for downstream use
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
EVIDENCE_CATS = [
    "Phenomenological SC", "Microscopic pairing", "Field theory & RG",
    "Response & transport", "Topological", "Junction & interface",
    "Many-body & correlation", "Quantum circuits & info", "Other methods",
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
EVID_SHORT = {
    "Phenomenological SC":     "Phenom.",
    "Microscopic pairing":     "Micro.pair",
    "Field theory & RG":       "FT&RG",
    "Response & transport":    "Resp.&Trans.",
    "Topological":             "Topol.",
    "Junction & interface":    "Junction",
    "Many-body & correlation": "Many-body",
    "Quantum circuits & info": "Quantum",
    "Other methods":           "Other",
}
FAM_IDX  = {f: i for i, f in enumerate(DISP_FAMS)}
MECH_IDX = {m: i for i, m in enumerate(MECH_ORDER)}
EVID_IDX = {e: i for i, e in enumerate(EVIDENCE_CATS)}
NF, NM, NE = len(DISP_FAMS), len(MECH_ORDER), len(EVIDENCE_CATS)

LAMBDA          = 0.05
THRESHOLD_N     = 5      # YEAR_MIN(L) = year cumulative count of L crosses N
ROBUST_PCT      = 10     # robust variant: YEAR_MIN(L) = 10th-percentile year
GLOBAL_YEAR_MIN = 1956   # used only for the "global time-weighted" comparison

# ── load data ─────────────────────────────────────────────────────────────────
with open(CSV_PATH, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))


def parse_year(r):
    try:
        return int(r["year"])
    except (ValueError, KeyError, TypeError):
        return None


def evid_tags(r):
    """Multi-label evidence categories from the evidence_theory column."""
    ev = (r.get("evidence_theory") or "").strip()
    if not ev or ev == "none":
        return []
    return [c.strip() for c in ev.split(" | ") if c.strip()]


# ── per-label YEAR_MIN ────────────────────────────────────────────────────────
def collect_label_years(rows):
    mech_years = defaultdict(list)
    evid_years = defaultdict(list)
    fam_years  = defaultdict(list)
    for r in rows:
        yr = parse_year(r)
        if yr is None:
            continue
        if r.get("mechanism") in MECH_IDX:
            mech_years[r["mechanism"]].append(yr)
        if r.get("family") in FAM_IDX:
            fam_years[r["family"]].append(yr)
        for tag in evid_tags(r):
            if tag in EVID_IDX:
                evid_years[tag].append(yr)
    return mech_years, evid_years, fam_years


def compute_year_min_n(label_to_years, threshold=THRESHOLD_N):
    """YEAR_MIN(L) = year by which cumulative count of L reaches `threshold`."""
    out = {}
    for L, years in label_to_years.items():
        if not years:
            continue
        ys = sorted(years)
        out[L] = ys[min(threshold - 1, len(ys) - 1)]
    return out


def compute_year_min_pct(label_to_years, pct=ROBUST_PCT):
    """YEAR_MIN(L) = `pct`-th percentile of years for label L."""
    out = {}
    for L, years in label_to_years.items():
        if not years:
            continue
        ys = sorted(years)
        out[L] = ys[int(len(ys) * pct / 100)]
    return out


mech_years, evid_years, fam_years = collect_label_years(rows)
mech_year_min = compute_year_min_n(mech_years)
evid_year_min = compute_year_min_n(evid_years)
fam_year_min  = compute_year_min_n(fam_years)

mech_year_min_r = compute_year_min_pct(mech_years)
evid_year_min_r = compute_year_min_pct(evid_years)
fam_year_min_r  = compute_year_min_pct(fam_years)

# fill any missing labels with the global anchor
for m in MECH_ORDER:
    mech_year_min.setdefault(m, GLOBAL_YEAR_MIN)
    mech_year_min_r.setdefault(m, GLOBAL_YEAR_MIN)
for e in EVIDENCE_CATS:
    evid_year_min.setdefault(e, GLOBAL_YEAR_MIN)
    evid_year_min_r.setdefault(e, GLOBAL_YEAR_MIN)
for f in DISP_FAMS:
    fam_year_min.setdefault(f, GLOBAL_YEAR_MIN)
    fam_year_min_r.setdefault(f, GLOBAL_YEAR_MIN)


def w_anchor(year, year_min_L, lam=LAMBDA):
    """Thresholded exp weight.  Pre-emergence papers (year < ymin) get 0;
    otherwise exp(lam * (year - ymin)).  The threshold breaks the
    multiplicative factorization that would otherwise make this identical
    to the global time-weighted scheme after normalization."""
    if year < year_min_L:
        return 0.0
    return float(np.exp(lam * (year - year_min_L)))


# ── matrix builders: per-cell column-anchored ─────────────────────────────────
def build_fam_mech_perlabel(rows, mech_ymin, lam=LAMBDA):
    """Cell (fi, mi):
         num = sum over (family fi, mech mi) papers of exp(lam*(yr - YEAR_MIN(mi)))
         den = sum over family fi papers          of exp(lam*(yr - YEAR_MIN(mi)))
       Each row's cells use different clocks; row-sums are not 1.
    """
    num = np.zeros((NF, NM))
    den = np.zeros((NF, NM))
    for r in rows:
        yr = parse_year(r)
        if yr is None: continue
        fi = FAM_IDX.get(r.get("family"))
        if fi is None: continue
        for mech_label, mi in MECH_IDX.items():
            den[fi, mi] += w_anchor(yr, mech_ymin[mech_label], lam)
        mi_self = MECH_IDX.get(r.get("mechanism"))
        if mi_self is not None:
            num[fi, mi_self] += w_anchor(yr, mech_ymin[MECH_ORDER[mi_self]], lam)
    den[den == 0] = 1
    return num / den


def build_fam_evid_perlabel(rows, evid_ymin, lam=LAMBDA):
    num = np.zeros((NF, NE))
    den = np.zeros((NF, NE))
    for r in rows:
        yr = parse_year(r)
        if yr is None: continue
        fi = FAM_IDX.get(r.get("family"))
        if fi is None: continue
        my_tags = set(evid_tags(r))
        for evid_label, ei in EVID_IDX.items():
            w = w_anchor(yr, evid_ymin[evid_label], lam)
            den[fi, ei] += w
            if evid_label in my_tags:
                num[fi, ei] += w
    den[den == 0] = 1
    return num / den


def build_mech_evid_perlabel(rows, evid_ymin, lam=LAMBDA):
    num = np.zeros((NM, NE))
    den = np.zeros((NM, NE))
    for r in rows:
        yr = parse_year(r)
        if yr is None: continue
        mi = MECH_IDX.get(r.get("mechanism"))
        if mi is None: continue
        my_tags = set(evid_tags(r))
        for evid_label, ei in EVID_IDX.items():
            w = w_anchor(yr, evid_ymin[evid_label], lam)
            den[mi, ei] += w
            if evid_label in my_tags:
                num[mi, ei] += w
    den[den == 0] = 1
    return num / den


# ── matrix builders: unweighted (for delta) and global-time (for comparison) ─
def build_fam_mech_flat(rows):
    mat = np.zeros((NF, NM))
    for r in rows:
        fi = FAM_IDX.get(r.get("family"))
        mi = MECH_IDX.get(r.get("mechanism"))
        if fi is not None and mi is not None:
            mat[fi, mi] += 1
    rs = mat.sum(axis=1, keepdims=True);  rs[rs == 0] = 1
    return mat / rs


def build_fam_evid_flat(rows):
    mat   = np.zeros((NF, NE))
    fam_n = np.zeros(NF)
    for r in rows:
        fi = FAM_IDX.get(r.get("family"))
        if fi is None: continue
        fam_n[fi] += 1
        for cat in evid_tags(r):
            ei = EVID_IDX.get(cat)
            if ei is not None:
                mat[fi, ei] += 1
    fam_n[fam_n == 0] = 1
    return mat / fam_n[:, None]


def build_mech_evid_flat(rows):
    mat    = np.zeros((NM, NE))
    mech_n = np.zeros(NM)
    for r in rows:
        mi = MECH_IDX.get(r.get("mechanism"))
        if mi is None: continue
        mech_n[mi] += 1
        for cat in evid_tags(r):
            ei = EVID_IDX.get(cat)
            if ei is not None:
                mat[mi, ei] += 1
    mech_n[mech_n == 0] = 1
    return mat / mech_n[:, None]


def build_fam_mech_global(rows, lam=LAMBDA, year_min=GLOBAL_YEAR_MIN):
    mat = np.zeros((NF, NM))
    for r in rows:
        yr = parse_year(r)
        if yr is None: continue
        fi = FAM_IDX.get(r.get("family"))
        mi = MECH_IDX.get(r.get("mechanism"))
        if fi is not None and mi is not None:
            mat[fi, mi] += float(np.exp(lam * (yr - year_min)))
    rs = mat.sum(axis=1, keepdims=True);  rs[rs == 0] = 1
    return mat / rs


def build_fam_evid_global(rows, lam=LAMBDA, year_min=GLOBAL_YEAR_MIN):
    mat   = np.zeros((NF, NE))
    fam_w = np.zeros(NF)
    for r in rows:
        yr = parse_year(r)
        if yr is None: continue
        fi = FAM_IDX.get(r.get("family"))
        if fi is None: continue
        w = float(np.exp(lam * (yr - year_min)))
        fam_w[fi] += w
        for cat in evid_tags(r):
            ei = EVID_IDX.get(cat)
            if ei is not None:
                mat[fi, ei] += w
    fam_w[fam_w == 0] = 1
    return mat / fam_w[:, None]


def build_mech_evid_global(rows, lam=LAMBDA, year_min=GLOBAL_YEAR_MIN):
    mat    = np.zeros((NM, NE))
    mech_w = np.zeros(NM)
    for r in rows:
        yr = parse_year(r)
        if yr is None: continue
        mi = MECH_IDX.get(r.get("mechanism"))
        if mi is None: continue
        w = float(np.exp(lam * (yr - year_min)))
        mech_w[mi] += w
        for cat in evid_tags(r):
            ei = EVID_IDX.get(cat)
            if ei is not None:
                mat[mi, ei] += w
    mech_w[mech_w == 0] = 1
    return mat / mech_w[:, None]


# ── compute all matrices ──────────────────────────────────────────────────────
# N=5 ("first appears") variant
mat_fm_pl = build_fam_mech_perlabel(rows, mech_year_min)
mat_fe_pl = build_fam_evid_perlabel(rows, evid_year_min)
mat_me_pl = build_mech_evid_perlabel(rows, evid_year_min)

# 10th-percentile ("robust") variant
mat_fm_pr = build_fam_mech_perlabel(rows, mech_year_min_r)
mat_fe_pr = build_fam_evid_perlabel(rows, evid_year_min_r)
mat_me_pr = build_mech_evid_perlabel(rows, evid_year_min_r)

mat_fm_fl = build_fam_mech_flat(rows)
mat_fe_fl = build_fam_evid_flat(rows)
mat_me_fl = build_mech_evid_flat(rows)

mat_fm_gl = build_fam_mech_global(rows)
mat_fe_gl = build_fam_evid_global(rows)
mat_me_gl = build_mech_evid_global(rows)

delta_fm   = mat_fm_pl - mat_fm_fl
delta_fe   = mat_fe_pl - mat_fe_fl
delta_me   = mat_me_pl - mat_me_fl

delta_fm_r = mat_fm_pr - mat_fm_fl
delta_fe_r = mat_fe_pr - mat_fe_fl
delta_me_r = mat_me_pr - mat_me_fl


# ── write YEAR_MIN tables ─────────────────────────────────────────────────────
def write_csv(path, rows_iter, header):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows_iter:
            w.writerow(r)


write_csv(OUT_DIR / "year_min_mechanism.csv",
          [(m, mech_year_min[m], mech_year_min_r[m], len(mech_years.get(m, [])))
           for m in MECH_ORDER],
          ["mechanism", "YEAR_MIN_N5", "YEAR_MIN_p10", "n_papers"])
write_csv(OUT_DIR / "year_min_evidence.csv",
          [(e, evid_year_min[e], evid_year_min_r[e], len(evid_years.get(e, [])))
           for e in EVIDENCE_CATS],
          ["evidence_category", "YEAR_MIN_N5", "YEAR_MIN_p10", "n_papers"])
write_csv(OUT_DIR / "year_min_family.csv",
          [(f, fam_year_min[f], fam_year_min_r[f], len(fam_years.get(f, [])))
           for f in DISP_FAMS],
          ["family", "YEAR_MIN_N5", "YEAR_MIN_p10", "n_papers"])

np.savez(OUT_DIR / "matrices.npz",
         fam_mech_perlabel=mat_fm_pl,    fam_mech_perlabel_robust=mat_fm_pr,
         fam_mech_flat=mat_fm_fl,        fam_mech_global=mat_fm_gl,
         fam_evid_perlabel=mat_fe_pl,    fam_evid_perlabel_robust=mat_fe_pr,
         fam_evid_flat=mat_fe_fl,        fam_evid_global=mat_fe_gl,
         mech_evid_perlabel=mat_me_pl,   mech_evid_perlabel_robust=mat_me_pr,
         mech_evid_flat=mat_me_fl,       mech_evid_global=mat_me_gl,
         delta_fm=delta_fm,   delta_fe=delta_fe,   delta_me=delta_me,
         delta_fm_r=delta_fm_r, delta_fe_r=delta_fe_r, delta_me_r=delta_me_r)


# ── heatmap helper ────────────────────────────────────────────────────────────
def draw_heatmap(ax, mat, row_lbl, col_lbl, cmap, vmin, vmax, title,
                 cbar_label="", annot_frac=0.10, diverging=False, fmt=".2f"):
    im = ax.imshow(mat, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(col_lbl)))
    ax.set_xticklabels(col_lbl, rotation=42, ha="right", fontsize=7)
    ax.set_yticks(range(len(row_lbl)))
    ax.set_yticklabels(row_lbl, fontsize=7.5)
    ax.set_title(title, fontsize=8.8, fontweight="bold", pad=4)
    thresh = vmax * annot_frac
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            if np.isnan(v): continue
            show = (abs(v) >= thresh) if diverging else (v >= thresh)
            if show:
                tc = "white" if (abs(v) if diverging else v) >= vmax * 0.60 else "black"
                ax.text(j, i, f"{v:{fmt}}", ha="center", va="center",
                        fontsize=5.8, color=tc)
    plt.colorbar(im, ax=ax, label=cbar_label, shrink=0.84, pad=0.02)
    return im


MLS = [MECH_SHORT[m] for m in MECH_ORDER]
ELS = [EVID_SHORT[e] for e in EVIDENCE_CATS]
FML = DISP_FAMS


# ── main combined figure ──────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(21, 13))
fig.suptitle(
    "Figure 3 (per-label weighting) - recency anchored to each label's emergence\n"
    f"YEAR_MIN(L) = year cumulative count of L crosses {THRESHOLD_N};   "
    f"weight  w(r,L) = exp({LAMBDA} * (year - YEAR_MIN(L)));   anchor = column label",
    fontsize=12, fontweight="bold", y=0.998,
)
plt.subplots_adjust(hspace=0.55, wspace=0.42)

draw_heatmap(axes[0, 0], mat_fm_pl, FML, MLS, "YlOrRd", 0, 1,
             "NW.1 - Family x Mechanism (per-label weighted)\n"
             "fraction within mechanism's mature era",
             cbar_label="P_L(mech|family)", annot_frac=0.05)

draw_heatmap(axes[0, 1], mat_fe_pl, FML, ELS, "YlOrRd", 0, max(mat_fe_pl.max(), 0.01),
             "NW.2 - Family x Evidence (per-label weighted)\n"
             "fraction within evidence's mature era",
             cbar_label="fraction (per-label)", annot_frac=0.08)

draw_heatmap(axes[0, 2], mat_me_pl, MLS, ELS, "YlOrRd", 0, max(mat_me_pl.max(), 0.01),
             "NW.3 - Mechanism x Evidence (per-label weighted)\n"
             "fraction within evidence's mature era",
             cbar_label="fraction (per-label)", annot_frac=0.08)

lim_fm = max(abs(delta_fm).max(), 1e-6)
draw_heatmap(axes[1, 0], delta_fm, FML, MLS, "RdBu_r", -lim_fm, lim_fm,
             "NW.4 - Delta Family x Mechanism\n"
             "(per-label - flat;  red = riser within mech's lifetime)",
             cbar_label="delta P", annot_frac=0.15, diverging=True)

lim_fe = max(abs(delta_fe).max(), 1e-6)
draw_heatmap(axes[1, 1], delta_fe, FML, ELS, "RdBu_r", -lim_fe, lim_fe,
             "NW.5 - Delta Family x Evidence\n"
             "(per-label - flat)",
             cbar_label="delta fraction", annot_frac=0.15, diverging=True)

lim_me = max(abs(delta_me).max(), 1e-6)
draw_heatmap(axes[1, 2], delta_me, MLS, ELS, "RdBu_r", -lim_me, lim_me,
             "NW.6 - Delta Mechanism x Evidence\n"
             "(per-label - flat)",
             cbar_label="delta fraction", annot_frac=0.15, diverging=True)

plt.savefig(OUT_DIR / "figure3_per_label_weight_N5.png", dpi=150, bbox_inches="tight")
plt.close()


# ── second main figure: robust (10th-percentile) variant ─────────────────────
fig, axes = plt.subplots(2, 3, figsize=(21, 13))
fig.suptitle(
    f"Figure 3 (per-label weighting, ROBUST p{ROBUST_PCT}) - anchor at {ROBUST_PCT}th-percentile year\n"
    f"weight  w(r,L) = 0 if year<YEAR_MIN(L) else exp({LAMBDA} * (year - YEAR_MIN(L)));   anchor = column label",
    fontsize=12, fontweight="bold", y=0.998,
)
plt.subplots_adjust(hspace=0.55, wspace=0.42)

draw_heatmap(axes[0, 0], mat_fm_pr, FML, MLS, "YlOrRd", 0, 1,
             "RW.1 - Family x Mechanism (per-label, robust)\n"
             f"anchor = mechanism's p{ROBUST_PCT} year",
             cbar_label="P_L(mech|family)", annot_frac=0.05)
draw_heatmap(axes[0, 1], mat_fe_pr, FML, ELS, "YlOrRd", 0, max(mat_fe_pr.max(), 0.01),
             "RW.2 - Family x Evidence (per-label, robust)\n"
             f"anchor = evidence's p{ROBUST_PCT} year",
             cbar_label="fraction (per-label)", annot_frac=0.08)
draw_heatmap(axes[0, 2], mat_me_pr, MLS, ELS, "YlOrRd", 0, max(mat_me_pr.max(), 0.01),
             "RW.3 - Mechanism x Evidence (per-label, robust)\n"
             f"anchor = evidence's p{ROBUST_PCT} year",
             cbar_label="fraction (per-label)", annot_frac=0.08)

lim = max(abs(delta_fm_r).max(), 1e-6)
draw_heatmap(axes[1, 0], delta_fm_r, FML, MLS, "RdBu_r", -lim, lim,
             "RW.4 - Delta Family x Mechanism (robust)\n(per-label - flat)",
             cbar_label="delta P", annot_frac=0.15, diverging=True)
lim = max(abs(delta_fe_r).max(), 1e-6)
draw_heatmap(axes[1, 1], delta_fe_r, FML, ELS, "RdBu_r", -lim, lim,
             "RW.5 - Delta Family x Evidence (robust)\n(per-label - flat)",
             cbar_label="delta fraction", annot_frac=0.15, diverging=True)
lim = max(abs(delta_me_r).max(), 1e-6)
draw_heatmap(axes[1, 2], delta_me_r, MLS, ELS, "RdBu_r", -lim, lim,
             "RW.6 - Delta Mechanism x Evidence (robust)\n(per-label - flat)",
             cbar_label="delta fraction", annot_frac=0.15, diverging=True)

plt.savefig(OUT_DIR / "figure3_per_label_weight_p10.png", dpi=150, bbox_inches="tight")
plt.close()


# ── diagnostic: YEAR_MIN bar chart ────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

def draw_year_min_bar(ax, labels, short_labels, year_min, year_min_r, n_dict, color, title):
    """Show both N=5 (filled bar) and p10 (open dot) anchors per label."""
    y_n5 = [year_min[L]            for L in labels]
    y_p  = [year_min_r[L]          for L in labels]
    ns   = [len(n_dict.get(L, [])) for L in labels]
    ax.barh(range(len(labels)), y_n5, color=color, alpha=0.85, label=f"N={THRESHOLD_N}")
    ax.scatter(y_p, range(len(labels)), color="black", marker="D", s=20,
               zorder=5, label=f"p{ROBUST_PCT}")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(short_labels, fontsize=8)
    ax.invert_yaxis()
    ax.set_xlim(1955, 2026)
    ax.axvline(GLOBAL_YEAR_MIN, color="grey", lw=0.6, ls="--")
    for i, (y, p, n) in enumerate(zip(y_n5, y_p, ns)):
        ax.text(max(y, p) + 0.5, i, f" n={n}", va="center", fontsize=7)
    ax.set_xlabel(f"YEAR_MIN  (bar=N{THRESHOLD_N},  diamond=p{ROBUST_PCT})")
    ax.set_title(title, fontsize=10, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    ax.legend(loc="lower right", fontsize=7)

draw_year_min_bar(axes[0], MECH_ORDER,    MLS, mech_year_min, mech_year_min_r, mech_years,
                  "steelblue",   "Mechanism emergence years")
draw_year_min_bar(axes[1], EVIDENCE_CATS, ELS, evid_year_min, evid_year_min_r, evid_years,
                  "darkorange",  "Evidence-category emergence years")
draw_year_min_bar(axes[2], DISP_FAMS,     DISP_FAMS, fam_year_min, fam_year_min_r, fam_years,
                  "seagreen",    "Family emergence years")

plt.suptitle("Per-label YEAR_MIN (anchor years used by the new weighting)",
             fontsize=11, fontweight="bold", y=1.01)
plt.tight_layout()
plt.savefig(OUT_DIR / "year_min_diagnostic.png", dpi=150, bbox_inches="tight")
plt.close()


# ── side-by-side comparisons (flat / global / per-label-N5 / per-label-p10) ──
def comparison_panel(out_path, title, mat_flat, mat_global, mat_pl, mat_pr,
                     row_lbl, col_lbl, vmax_flat=1.0, vmax_w=None):
    if vmax_w is None:
        vmax_w = max(mat_global.max(), mat_pl.max(), mat_pr.max(), vmax_flat)
    fig, axes = plt.subplots(1, 4, figsize=(28, 7))
    fig.suptitle(title, fontsize=12, fontweight="bold", y=1.0)
    draw_heatmap(axes[0], mat_flat, row_lbl, col_lbl, "Blues", 0, vmax_flat,
                 "Unweighted (flat)", cbar_label="fraction", annot_frac=0.05)
    draw_heatmap(axes[1], mat_global, row_lbl, col_lbl, "YlOrRd", 0, vmax_w,
                 f"Global time-weighted (YEAR_MIN={GLOBAL_YEAR_MIN})",
                 cbar_label="fraction", annot_frac=0.05)
    draw_heatmap(axes[2], mat_pl, row_lbl, col_lbl, "YlOrRd", 0, vmax_w,
                 f"Per-label weighted (N={THRESHOLD_N})",
                 cbar_label="fraction", annot_frac=0.05)
    draw_heatmap(axes[3], mat_pr, row_lbl, col_lbl, "YlOrRd", 0, vmax_w,
                 f"Per-label weighted (p{ROBUST_PCT}, robust)",
                 cbar_label="fraction", annot_frac=0.05)
    plt.tight_layout()
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close()

comparison_panel(OUT_DIR / "comparison_fam_mech.png",
                 "Family x Mechanism - four weighting schemes",
                 mat_fm_fl, mat_fm_gl, mat_fm_pl, mat_fm_pr, FML, MLS, vmax_flat=1.0)

comparison_panel(OUT_DIR / "comparison_fam_evid.png",
                 "Family x Evidence - four weighting schemes",
                 mat_fe_fl, mat_fe_gl, mat_fe_pl, mat_fe_pr, FML, ELS,
                 vmax_flat=max(mat_fe_fl.max(), 0.01))

comparison_panel(OUT_DIR / "comparison_mech_evid.png",
                 "Mechanism x Evidence - four weighting schemes",
                 mat_me_fl, mat_me_gl, mat_me_pl, mat_me_pr, MLS, ELS,
                 vmax_flat=max(mat_me_fl.max(), 0.01))


# ── short summary to stdout ───────────────────────────────────────────────────
print(f"Saved 6 figures + 3 CSVs + matrices.npz -> {OUT_DIR}")
print()
print(f"{'label':32s}  N{THRESHOLD_N}    p{ROBUST_PCT}    n_papers")
print("--- mechanisms ---")
for m in MECH_ORDER:
    print(f"  {m:30s}  {mech_year_min[m]}  {mech_year_min_r[m]}  {len(mech_years.get(m, []))}")
print("--- evidence_theory ---")
for e in EVIDENCE_CATS:
    print(f"  {e:30s}  {evid_year_min[e]}  {evid_year_min_r[e]}  {len(evid_years.get(e, []))}")
print("--- family ---")
for f in DISP_FAMS:
    print(f"  {f:30s}  {fam_year_min[f]}  {fam_year_min_r[f]}  {len(fam_years.get(f, []))}")

# Magnitude summary
print()
print(f"Max |delta| (per-label - flat):")
print(f"  fam_mech  N{THRESHOLD_N}: {abs(delta_fm).max():.3f}    p{ROBUST_PCT}: {abs(delta_fm_r).max():.3f}")
print(f"  fam_evid  N{THRESHOLD_N}: {abs(delta_fe).max():.3f}    p{ROBUST_PCT}: {abs(delta_fe_r).max():.3f}")
print(f"  mech_evid N{THRESHOLD_N}: {abs(delta_me).max():.3f}    p{ROBUST_PCT}: {abs(delta_me_r).max():.3f}")
print(f"Max |per-label - global|:")
print(f"  fam_mech  N{THRESHOLD_N}: {abs(mat_fm_pl-mat_fm_gl).max():.3f}    p{ROBUST_PCT}: {abs(mat_fm_pr-mat_fm_gl).max():.3f}")
print(f"  fam_evid  N{THRESHOLD_N}: {abs(mat_fe_pl-mat_fe_gl).max():.3f}    p{ROBUST_PCT}: {abs(mat_fe_pr-mat_fe_gl).max():.3f}")
print(f"  mech_evid N{THRESHOLD_N}: {abs(mat_me_pl-mat_me_gl).max():.3f}    p{ROBUST_PCT}: {abs(mat_me_pr-mat_me_gl).max():.3f}")
