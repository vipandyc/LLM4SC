#!/usr/bin/env python3
"""
Figure 3 – Self-correlation and cross-correlation among family, mechanism,
           evidence; plus time-weighted (recency-biased) versions.
Sub-panels 3.1 – 3.11  (4 rows × 3 cols, last cell empty)

Row 1 – unweighted cross-correlations:
  3.1  Family × Mechanism          P(mech | family)
  3.2  Family × Evidence           fraction with evidence tag  (multi-label)
  3.3  Mechanism × Evidence        fraction with evidence tag  (multi-label)

Row 2 – evidence self-correlation + time-weighted:
  3.4  Evidence × Evidence         phi coefficient (multi-label self-correlation)
  3.5  Family × Mechanism          time-weighted
  3.6  Family × Evidence           time-weighted

Row 3 – time-weighted mech×evid + delta maps (recent shift):
  3.7  Mechanism × Evidence        time-weighted
  3.8  Δ Family × Mechanism        (weighted – unweighted)
  3.9  Δ Family × Evidence         (weighted – unweighted)

Row 4 – per-family breakdowns (moved from Figure 2):
  3.10 Mechanism composition per family  (normalised stacked bars)
  3.11 Evidence fraction per family      (heatmap)

Time weight:  w(year) = exp(λ · (year − 1956)),  λ = 0.05
  → 2024 papers are ~29× heavier than 1956 papers.
"""

import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────────
CSV_PATH = Path(__file__).parent.parent / "SC_final_data_5k.csv"
OUT_PATH = Path(__file__).parent.parent / "output" / "figures" / "figure3.png"
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# ── canonical orders ──────────────────────────────────────────────────────────
DISP_FAMS = [
    "cuprate", "iron-based", "heavy-fermion", "nickelate",
    "hydrogen", "kagome", "ruthenate", "elemental", "MgB2", "2D",
    "organic", "A15", "alloy", "fulleride", "oxide", "carbide/nitride",
]
MECH_SHORT_FIG3 = {
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

# ── time-weighting parameters ─────────────────────────────────────────────────
YEAR_MIN = 1956
LAMBDA   = 0.05   # weight = exp(LAMBDA * (year - YEAR_MIN))

# ── load data ─────────────────────────────────────────────────────────────────
with open(CSV_PATH, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))


def get_weight(r):
    try:
        return float(np.exp(LAMBDA * (int(r["year"]) - YEAR_MIN)))
    except (ValueError, KeyError):
        return 1.0


def ev_cats(r):
    ev = r["evidence"].strip()
    if not ev or ev == "none":
        return []
    return [c.strip() for c in ev.split(" | ") if c.strip()]


# ── matrix builders ───────────────────────────────────────────────────────────
def build_fam_mech(rows, W):
    """Shape (NF, NM). Normalised by family row sum → P(mech|family)."""
    mat = np.zeros((NF, NM))
    for r, w in zip(rows, W):
        fi = FAM_IDX.get(r["family"])
        mi = MECH_IDX.get(r["mechanism"])
        if fi is not None and mi is not None:
            mat[fi, mi] += w
    rs = mat.sum(axis=1, keepdims=True)
    rs[rs == 0] = 1
    return mat / rs


def build_fam_evid(rows, W):
    """Shape (NF, NE). Multi-label; normalised by weighted family total."""
    mat    = np.zeros((NF, NE))
    fam_w  = np.zeros(NF)
    for r, w in zip(rows, W):
        fi = FAM_IDX.get(r["family"])
        if fi is None:
            continue
        fam_w[fi] += w
        for cat in ev_cats(r):
            ei = EVID_IDX.get(cat)
            if ei is not None:
                mat[fi, ei] += w
    fam_w[fam_w == 0] = 1
    return mat / fam_w[:, None]


def build_mech_evid(rows, W):
    """Shape (NM, NE). Multi-label; normalised by weighted mechanism total."""
    mat    = np.zeros((NM, NE))
    mech_w = np.zeros(NM)
    for r, w in zip(rows, W):
        mi = MECH_IDX.get(r["mechanism"])
        if mi is None:
            continue
        mech_w[mi] += w
        for cat in ev_cats(r):
            ei = EVID_IDX.get(cat)
            if ei is not None:
                mat[mi, ei] += w
    mech_w[mech_w == 0] = 1
    return mat / mech_w[:, None]


def build_evid_selfcorr(rows, W):
    """
    Shape (NE, NE). Weighted Pearson (phi) coefficient matrix for binary
    evidence indicators.  Only papers with ≥1 evidence tag are included.
    """
    X = np.zeros((len(rows), NE))
    Warr = np.array(W, dtype=float)
    for i, r in enumerate(rows):
        for cat in ev_cats(r):
            ei = EVID_IDX.get(cat)
            if ei is not None:
                X[i, ei] = 1.0

    has_ev = X.sum(axis=1) > 0
    Xs     = X[has_ev]
    Ws     = Warr[has_ev]
    Wn     = Ws / Ws.sum()                    # normalised weights

    mu     = (Xs * Wn[:, None]).sum(axis=0)   # weighted mean of each indicator
    Xc     = Xs - mu[None, :]                 # centred

    cov    = (Xc * Wn[:, None]).T @ Xc        # weighted covariance  (NE×NE)
    var    = np.diag(cov)
    denom  = np.sqrt(np.outer(var, var))
    denom[denom == 0] = np.nan
    phi    = cov / denom
    np.fill_diagonal(phi, 1.0)
    return phi


# ── compute all matrices ──────────────────────────────────────────────────────
W_flat = [1.0]          * len(rows)
W_time = [get_weight(r) for r in rows]

mat_fm   = build_fam_mech(rows, W_flat)
mat_fe   = build_fam_evid(rows, W_flat)
mat_me   = build_mech_evid(rows, W_flat)
mat_ee   = build_evid_selfcorr(rows, W_flat)

mat_fm_w = build_fam_mech(rows, W_time)
mat_fe_w = build_fam_evid(rows, W_time)
mat_me_w = build_mech_evid(rows, W_time)

delta_fm = mat_fm_w - mat_fm
delta_fe = mat_fe_w - mat_fe

# ── heatmap helper ────────────────────────────────────────────────────────────
def draw_heatmap(ax, mat, row_lbl, col_lbl, cmap, vmin, vmax,
                 title, cbar_label="", annot_frac=0.10, diverging=False, fmt=".2f"):
    """Draw an annotated heatmap on *ax*."""
    im = ax.imshow(mat, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)

    ax.set_xticks(range(len(col_lbl)))
    ax.set_xticklabels(col_lbl, rotation=42, ha="right", fontsize=7)
    ax.set_yticks(range(len(row_lbl)))
    ax.set_yticklabels(row_lbl, fontsize=7.5)
    ax.set_title(title, fontsize=8.8, fontweight="bold", pad=4)

    # annotate cells above threshold
    thresh = vmax * annot_frac if not diverging else vmax * annot_frac
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            if np.isnan(v):
                continue
            if diverging:
                show = abs(v) >= thresh
                tc   = "white" if abs(v) >= vmax * 0.60 else "black"
            else:
                show = v >= thresh
                tc   = "white" if v >= vmax * 0.60 else "black"
            if show:
                ax.text(j, i, f"{v:{fmt}}", ha="center", va="center",
                        fontsize=5.8, color=tc)

    plt.colorbar(im, ax=ax, label=cbar_label, shrink=0.84, pad=0.02)
    return im


# ── colour maps for new panels ────────────────────────────────────────────────
MECH_COLORS_F3 = {m: plt.cm.Set2(i / (len(MECH_ORDER)-1)) for i, m in enumerate(MECH_ORDER)}
EVID_COLORS_F3 = {e: plt.cm.Set3(i / (len(EVIDENCE_CATS)-1)) for i, e in enumerate(EVIDENCE_CATS)}

# ── build figure ──────────────────────────────────────────────────────────────
fig, axes = plt.subplots(4, 3, figsize=(21, 26))
fig.suptitle(
    "Figure 3 – Correlations Among Family · Mechanism · Evidence\n"
    f"Time weight: exp({LAMBDA} × (year − {YEAR_MIN}))   "
    f"[{YEAR_MIN} – 2024;  2024 papers ≈ 29× heavier]",
    fontsize=13, fontweight="bold", y=0.995,
)
plt.subplots_adjust(hspace=0.58, wspace=0.42)

FML = DISP_FAMS
MLS = [MECH_SHORT[m] for m in MECH_ORDER]
ELS = [EVID_SHORT[e] for e in EVIDENCE_CATS]
NF  = len(DISP_FAMS)


# ── Row 1: unweighted cross-correlations ─────────────────────────────────────
draw_heatmap(axes[0, 0], mat_fm, FML, MLS,
             "Blues", 0, 1,
             "Fig. 3.1 – Family × Mechanism\n(unweighted,  P(mech|family))",
             cbar_label="P(mech|family)", annot_frac=0.05)

draw_heatmap(axes[0, 1], mat_fe, FML, ELS,
             "Blues", 0, mat_fe.max(),
             "Fig. 3.2 – Family × Evidence\n(unweighted,  fraction with tag)",
             cbar_label="fraction", annot_frac=0.08)

draw_heatmap(axes[0, 2], mat_me, MLS, ELS,
             "Blues", 0, mat_me.max(),
             "Fig. 3.3 – Mechanism × Evidence\n(unweighted,  fraction with tag)",
             cbar_label="fraction", annot_frac=0.08)


# ── Row 2: evidence self-correlation + time-weighted cross-correlations ───────
draw_heatmap(axes[1, 0], mat_ee, ELS, ELS,
             "RdBu_r", -1, 1,
             "Fig. 3.4 – Evidence Self-Correlation\n(φ coefficient,  papers with ≥1 tag)",
             cbar_label="φ coefficient", annot_frac=0.05, diverging=True)

draw_heatmap(axes[1, 1], mat_fm_w, FML, MLS,
             "YlOrRd", 0, 1,
             "Fig. 3.5 – Family × Mechanism\n(time-weighted,  P(mech|family))",
             cbar_label="P(mech|family) weighted", annot_frac=0.05)

draw_heatmap(axes[1, 2], mat_fe_w, FML, ELS,
             "YlOrRd", 0, mat_fe_w.max(),
             "Fig. 3.6 – Family × Evidence\n(time-weighted,  fraction with tag)",
             cbar_label="fraction weighted", annot_frac=0.08)


# ── Row 3: time-weighted mech×evid + Δ maps ──────────────────────────────────
draw_heatmap(axes[2, 0], mat_me_w, MLS, ELS,
             "YlOrRd", 0, mat_me_w.max(),
             "Fig. 3.7 – Mechanism × Evidence\n(time-weighted,  fraction with tag)",
             cbar_label="fraction weighted", annot_frac=0.08)

lim_fm = max(abs(delta_fm).max(), 1e-6)
draw_heatmap(axes[2, 1], delta_fm, FML, MLS,
             "RdBu_r", -lim_fm, lim_fm,
             "Fig. 3.8 – Δ Family × Mechanism\n(weighted − unweighted;  red = more recent)",
             cbar_label="Δ P(mech|family)", annot_frac=0.15, diverging=True)

lim_fe = max(abs(delta_fe).max(), 1e-6)
draw_heatmap(axes[2, 2], delta_fe, FML, ELS,
             "RdBu_r", -lim_fe, lim_fe,
             "Fig. 3.9 – Δ Family × Evidence\n(weighted − unweighted;  red = more recent)",
             cbar_label="Δ fraction", annot_frac=0.15, diverging=True)


# ── Row 4: per-family breakdowns (moved from Figure 2) ───────────────────────

# 3.10  Mechanism composition per family (normalised stacked horizontal bars)
ax = axes[3, 0]
import numpy as _np
fam_mech = _np.zeros((NF, len(MECH_ORDER)))
for r in rows:
    fi = FAM_IDX.get(r["family"])
    mi = MECH_IDX.get(r["mechanism"])
    if fi is not None and mi is not None:
        fam_mech[fi, mi] += 1
row_sums = fam_mech.sum(axis=1, keepdims=True)
row_sums[row_sums == 0] = 1
fam_mech_norm = fam_mech / row_sums

y_pos   = _np.arange(NF)
bots    = _np.zeros(NF)
for mi, mech in enumerate(MECH_ORDER):
    ax.barh(y_pos, fam_mech_norm[:, mi], left=bots,
            color=MECH_COLORS_F3[mech], label=MECH_SHORT_FIG3[mech], height=0.72)
    bots += fam_mech_norm[:, mi]

ax.set_yticks(y_pos)
ax.set_yticklabels(DISP_FAMS, fontsize=8)
ax.set_xlabel("Fraction", fontsize=9)
ax.set_xlim(0, 1.0)
ax.set_title("Fig. 3.10 – Mechanism Composition per Family\n(normalised)", fontsize=8.8, fontweight="bold")
ax.legend(fontsize=6.5, bbox_to_anchor=(1.01, 1), loc="upper left", ncol=1, framealpha=0.8)
ax.grid(axis="x", alpha=0.3, linewidth=0.5)
ax.spines[["top", "right"]].set_visible(False)

# 3.11  Evidence fraction per family (heatmap)
ax = axes[3, 1]
from collections import Counter as _Counter
fam_totals = _Counter(r["family"] for r in rows)
fam_evid   = _np.zeros((NF, len(EVIDENCE_CATS)))
for r in rows:
    ev = r["evidence"].strip()
    if ev and ev != "none":
        fi = FAM_IDX.get(r["family"])
        if fi is None:
            continue
        for cat in ev.split(" | "):
            cat = cat.strip()
            ei = EVID_IDX.get(cat)
            if ei is not None:
                fam_evid[fi, ei] += 1
for fi, fam in enumerate(DISP_FAMS):
    fam_evid[fi] /= max(fam_totals.get(fam, 1), 1)

vmax = fam_evid.max()
im = ax.imshow(fam_evid, aspect="auto", cmap="Blues", vmin=0, vmax=vmax)
ax.set_xticks(range(len(EVIDENCE_CATS)))
ax.set_xticklabels(ELS, rotation=38, ha="right", fontsize=7)
ax.set_yticks(range(NF))
ax.set_yticklabels(DISP_FAMS, fontsize=8)
for i in range(NF):
    for j in range(len(EVIDENCE_CATS)):
        v = fam_evid[i, j]
        if v > 0.02:
            tc = "white" if v > vmax * 0.60 else "black"
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=6, color=tc)
plt.colorbar(im, ax=ax, label="Fraction of family papers", shrink=0.88, pad=0.02)
ax.set_title("Fig. 3.11 – Evidence Fraction per Family", fontsize=8.8, fontweight="bold")

# hide unused cell [3, 2]
axes[3, 2].set_visible(False)


# ── save ──────────────────────────────────────────────────────────────────────
plt.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
print(f"Saved → {OUT_PATH}")
plt.close()
