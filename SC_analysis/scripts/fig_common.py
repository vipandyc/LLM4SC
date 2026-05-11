#!/usr/bin/env python3
"""
Shared constants, data-loading, colour maps, and helpers for all figure scripts.
Import with:  from fig_common import *
"""

import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter
from pathlib import Path

# ── paths ──────────────────────────────────────────────────────────────────────
CSV_PATH = Path(__file__).parent.parent / "SC_final_data_5k.csv"
OUT_DIR  = Path(__file__).parent.parent / "output" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── canonical orders ───────────────────────────────────────────────────────────
FAMILY_ORDER = [
    "cuprate", "iron-based", "heavy-fermion", "nickelate",
    "hydrogen", "kagome", "ruthenate", "elemental", "MgB2", "2D",
    "organic", "A15", "alloy", "fulleride", "oxide", "carbide/nitride",
    "general-theory", "other", "unknown",
]
# named families for per-family breakdowns (excludes catch-all buckets)
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
    "Phenomenological SC":      "Phenom. SC",
    "Microscopic pairing":      "Micro. pair",
    "Field theory & RG":        "FT & RG",
    "Response & transport":     "Resp. & Trans.",
    "Topological":              "Topol.",
    "Junction & interface":     "Junction",
    "Many-body & correlation":  "Many-body",
    "Quantum circuits & info":  "Quantum",
    "Other methods":            "Other",
}

# index look-ups
FAM_IDX  = {f: i for i, f in enumerate(DISP_FAMS)}
MECH_IDX = {m: i for i, m in enumerate(MECH_ORDER)}
EVID_IDX = {e: i for i, e in enumerate(EVIDENCE_CATS)}
NF, NM, NE = len(DISP_FAMS), len(MECH_ORDER), len(EVIDENCE_CATS)

# ── colour maps ────────────────────────────────────────────────────────────────
FAM_COLORS  = {f: plt.cm.tab20(i / max(len(FAMILY_ORDER), 1))
               for i, f in enumerate(FAMILY_ORDER)}
_TAB10 = plt.get_cmap("tab10").colors
_TAB20 = plt.get_cmap("tab20").colors
MECH_COLORS = {m: _TAB10[i % len(_TAB10)] for i, m in enumerate(MECH_ORDER)}
EVID_COLORS = {e: _TAB20[i % len(_TAB20)] for i, e in enumerate(EVIDENCE_CATS)}

# ── time-weighting ─────────────────────────────────────────────────────────────
YEAR_MIN = 1956
LAMBDA   = 0.05      # weight = exp(LAMBDA * (year − YEAR_MIN))
YEARS    = list(range(1956, 2025))


# ── data loading ───────────────────────────────────────────────────────────────
def load_rows():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ── helpers ────────────────────────────────────────────────────────────────────
def explode_evidence(rows):
    """Yield (category, row) for every evidence tag (multi-label)."""
    for r in rows:
        ev = r["evidence"].strip()
        if ev and ev != "none":
            for cat in ev.split(" | "):
                cat = cat.strip()
                if cat:
                    yield cat, r


def ev_cats(r):
    ev = r["evidence"].strip()
    if not ev or ev == "none":
        return []
    return [c.strip() for c in ev.split(" | ") if c.strip()]


def get_weight(r):
    try:
        return float(np.exp(LAMBDA * (int(r["year"]) - YEAR_MIN)))
    except (ValueError, KeyError):
        return 1.0


def flat_weights(rows):
    return [1.0] * len(rows)


def time_weights(rows):
    return [get_weight(r) for r in rows]


# ── matrix builders ────────────────────────────────────────────────────────────
def build_fam_mech(rows, W):
    """(NF, NM) — P(mech | family), row-normalised."""
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
    """(NF, NE) — fraction with evidence tag, multi-label."""
    mat   = np.zeros((NF, NE))
    fam_w = np.zeros(NF)
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
    """(NM, NE) — fraction with evidence tag, multi-label."""
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
    """(NE, NE) — weighted Pearson (phi) coefficient matrix."""
    X    = np.zeros((len(rows), NE))
    Warr = np.array(W, dtype=float)
    for i, r in enumerate(rows):
        for cat in ev_cats(r):
            ei = EVID_IDX.get(cat)
            if ei is not None:
                X[i, ei] = 1.0
    has_ev = X.sum(axis=1) > 0
    Xs = X[has_ev];  Ws = Warr[has_ev];  Wn = Ws / Ws.sum()
    mu  = (Xs * Wn[:, None]).sum(axis=0)
    Xc  = Xs - mu[None, :]
    cov = (Xc * Wn[:, None]).T @ Xc
    var = np.diag(cov)
    denom = np.sqrt(np.outer(var, var))
    denom[denom == 0] = np.nan
    phi = cov / denom
    np.fill_diagonal(phi, 1.0)
    return phi


# ── heatmap helper ─────────────────────────────────────────────────────────────
def draw_heatmap(ax, mat, row_lbl, col_lbl, cmap, vmin, vmax,
                 title, cbar_label="", annot_frac=0.10, diverging=False, fmt=".2f"):
    im = ax.imshow(mat, aspect="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(col_lbl)))
    ax.set_xticklabels(col_lbl, rotation=42, ha="right", fontsize=9)
    ax.set_yticks(range(len(row_lbl)))
    ax.set_yticklabels(row_lbl, fontsize=9)
    #ax.set_title(title, fontsize=11, fontweight="bold", pad=6)
    thresh = vmax * annot_frac
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            if np.isnan(v):
                continue
            show = (abs(v) >= thresh) if diverging else (v >= thresh)
            if show:
                tc = "white" if (abs(v) if diverging else v) >= vmax * 0.60 else "black"
                ax.text(j, i, f"{v:{fmt}}", ha="center", va="center",
                        fontsize=7.5, color=tc)
    plt.colorbar(im, ax=ax, label=cbar_label, shrink=0.88, pad=0.02)
    return im
