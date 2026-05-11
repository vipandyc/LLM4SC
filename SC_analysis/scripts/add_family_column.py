from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
SC_DIR = ROOT / "superconductivity"
SC_ANALYSIS_DIR = ROOT / "SC_analysis"
OUT_DIR = SC_ANALYSIS_DIR / "output"
FIG_DIR = OUT_DIR / "figures"

MECHANISM_COLS = [
    "pure el-ph coupling",
    "bipolaron el-ph coupling",
    "AFM fluctuation",
    "FM fluctuation",
    "charge density wave",
    "nematic fluctuation",
    "plasmon fluctuation",
    "pure el correlation",
    "spin liquid el correlation",
]

FAMILY_ORDER = [
    "cuprate",
    "iron-based",
    "heavy-fermion",
    "nickelate",
    "hydrogen",
    "kagome",
    "ruthenate",
    "elemental",
    "MgB2",
    "2D",
    "organic",
    "other",
    "unknown",
]

MECHANISM_LABELS = {
    "pure el-ph coupling": "El-ph",
    "bipolaron el-ph coupling": "Bipolaron",
    "AFM fluctuation": "AFM",
    "FM fluctuation": "FM",
    "charge density wave": "CDW",
    "nematic fluctuation": "Nematic",
    "plasmon fluctuation": "Plasmon",
    "pure el correlation": "Correlation",
    "spin liquid el correlation": "Spin liquid",
    "none": "None",
}


def load_gpt_object(text: str) -> dict:
    try:
        return json.loads(text)
    except Exception:
        return {}


def infer_family(system: str) -> str:
    s = (system or "").lower()

    # ── named families (checked in priority order) ────────────────────────
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

    # ── elemental metals (expanded token list) ────────────────────────────
    if any(token in s for token in [
        # phrases
        "elemental superconductor", "elemental superconductors",
        "elemental metal", "elemental metals",
        "conventional superconductor", "conventional metallic",
        "superconducting metal", "superconducting metals",
        "metallic superconductor",
        "simple metal", "simple metals",
        "conventional bcs", "bcs-type superconductor", "bcs type superconductor",
        "conventional low-tc", "low-tc metal",
        # element names with parenthetical symbol
        "lead (pb)", "tin (sn)", "niobium (nb)", "tantalum (ta)",
        "aluminum (al)", "aluminium (al)", "indium (in)", "gallium (ga)",
        "mercury (hg)", "hg (mercury)", "thallium (tl)", "rhenium (re)",
        "cadmium (cd)", "zinc (zn)", "molybdenum (mo)", "osmium (os)",
        "vanadium (v)",
        # element names alone (safe in SC context given priority order above)
        "niobium", "tantalum", "mercury", "indium", "gallium",
        "thallium", "cadmium", "rhenium", "molybdenum", "osmium",
        "vanadium", "aluminum", "aluminium",
        # element-name + descriptor
        "lead superconductor", "tin superconductor",
        # palladium hydrides (conventional, not high-pressure)
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


def shannon_entropy(series: pd.Series) -> float:
    probs = series.value_counts(normalize=True)
    return -sum(p * math.log(p, 2) for p in probs if p > 0)


def prepare_master_table() -> pd.DataFrame:
    papers = pd.read_csv(SC_ANALYSIS_DIR / "SC_final_data_5k.csv")
    # Merge title and times_cited from the original GPT-processed file
    meta = pd.read_csv(
        DATA_DIR / "SC_related_cites_010_GPT_processed.csv",
        usecols=["id", "title", "times_cited"],
    )
    papers = papers.merge(meta, on="id", how="left")

    theory = pd.read_csv(DATA_DIR / "SC_theory_highlights.csv")[["id", "confidence"]].rename(
        columns={"confidence": "theory_confidence"}
    )
    citation_growth = pd.read_csv(SC_DIR / "citation_growth_over_time.csv")
    final_citations = (
        citation_growth.sort_values(["id", "year"]).groupby("id", as_index=False).tail(1)[["id", "cumulative_citations"]]
    )

    objs = papers["opinion_scores_dict"].apply(load_gpt_object)
    papers["system"] = objs.apply(lambda obj: obj.get("system", "N/A"))
    papers["model_or_method"] = objs.apply(lambda obj: obj.get("model", "N/A"))

    for col in MECHANISM_COLS:
        papers[col] = pd.to_numeric(objs.apply(lambda obj: obj.get(col, 0.0)), errors="coerce").fillna(0.0)

    papers["top_mechanism"] = papers[MECHANISM_COLS].idxmax(axis=1)
    papers.loc[papers[MECHANISM_COLS].max(axis=1) <= 0, "top_mechanism"] = "none"
    papers["family"] = papers["system"].apply(infer_family)
    papers["decade"] = (papers["year"] // 10) * 10
    papers["has_mechanism_signal"] = papers["top_mechanism"] != "none"

    master = papers.merge(theory, on="id", how="left").merge(final_citations, on="id", how="left")
    master["is_theory"] = master["theory_confidence"].notna()
    master["cumulative_citations"] = master["cumulative_citations"].fillna(master["times_cited"])
    return master


def save_plot_family_citation_heatmap(summary: pd.DataFrame) -> None:
    plot_df = summary.copy()
    plot_df["mechanism_short"] = plot_df["top_mechanism"].map(MECHANISM_LABELS)
    heat = plot_df.pivot(index="family", columns="mechanism_short", values="citation_share_pct").fillna(0.0)
    heat = heat.reindex(FAMILY_ORDER)
    heat = heat[[c for c in ["El-ph", "AFM", "Correlation", "CDW", "FM", "Nematic", "Spin liquid", "Bipolaron", "Plasmon"] if c in heat.columns]]

    plt.figure(figsize=(11, 4.8))
    sns.heatmap(heat, annot=True, fmt=".1f", cmap="YlOrRd", linewidths=0.5, cbar_kws={"label": "Citation share (%)"})
    plt.title("Dominant Mechanism Share by Superconductor Family")
    plt.xlabel("Top mechanism")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "family_mechanism_citation_share.png", dpi=220)
    plt.close()


def save_plot_family_entropy(entropy_df: pd.DataFrame) -> None:
    plt.figure(figsize=(9, 4.8))
    sns.barplot(data=entropy_df, x="family", y="entropy_bits", palette="deep")
    plt.title("Mechanism Diversity by Family")
    plt.xlabel("")
    plt.ylabel("Shannon entropy (bits)")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "family_mechanism_entropy.png", dpi=220)
    plt.close()


def save_plot_cuprate_timeline(cuprate_df: pd.DataFrame) -> None:
    order = ["AFM", "Correlation", "CDW", "Spin liquid", "El-ph", "Nematic", "Bipolaron", "FM", "Plasmon"]
    plot_df = cuprate_df.copy()
    plot_df["mechanism_short"] = plot_df["top_mechanism"].map(MECHANISM_LABELS)
    pivot = plot_df.pivot(index="decade", columns="mechanism_short", values="citation_share_pct").fillna(0.0)
    pivot = pivot[[col for col in order if col in pivot.columns]]

    plt.figure(figsize=(10, 5.5))
    pivot.plot(kind="bar", stacked=True, colormap="tab20", ax=plt.gca())
    plt.title("Cuprate Mechanism Mix by Decade")
    plt.xlabel("Decade")
    plt.ylabel("Citation-weighted share (%)")
    plt.legend(title="", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig(FIG_DIR / "cuprate_decade_mechanism_shift.png", dpi=220)
    plt.close()


def build_summaries(master: pd.DataFrame) -> dict[str, pd.DataFrame]:
    focused = master[master["family"].isin(FAMILY_ORDER) & master["has_mechanism_signal"]].copy()

    family_mechanism_counts = (
        focused.groupby(["family", "top_mechanism"], as_index=False)
        .size()
        .rename(columns={"size": "paper_count"})
        .sort_values(["family", "paper_count"], ascending=[True, False])
    )

    family_mechanism_citation = (
        focused.groupby(["family", "top_mechanism"], as_index=False)["cumulative_citations"].sum()
        .rename(columns={"cumulative_citations": "citation_total"})
    )
    family_totals = family_mechanism_citation.groupby("family")["citation_total"].transform("sum")
    family_mechanism_citation["citation_share_pct"] = 100 * family_mechanism_citation["citation_total"] / family_totals
    family_mechanism_citation = family_mechanism_citation.sort_values(["family", "citation_share_pct"], ascending=[True, False])

    entropy_rows = []
    for family, group in focused.groupby("family"):
        entropy_rows.append(
            {
                "family": family,
                "paper_count": len(group),
                "entropy_bits": shannon_entropy(group["top_mechanism"]),
                "top_mechanism": group["top_mechanism"].value_counts().idxmax(),
                "top_mechanism_share_pct": 100 * group["top_mechanism"].value_counts(normalize=True).iloc[0],
            }
        )
    family_entropy = pd.DataFrame(entropy_rows).sort_values("entropy_bits", ascending=False)

    cuprate_decade_citation = focused[focused["family"] == "cuprate"].copy()
    cuprate_decade_citation = (
        cuprate_decade_citation.groupby(["decade", "top_mechanism"], as_index=False)["times_cited"].sum()
        .rename(columns={"times_cited": "citation_total"})
    )
    decade_totals = cuprate_decade_citation.groupby("decade")["citation_total"].transform("sum")
    cuprate_decade_citation["citation_share_pct"] = 100 * cuprate_decade_citation["citation_total"] / decade_totals
    cuprate_decade_citation = cuprate_decade_citation.sort_values(["decade", "citation_share_pct"], ascending=[True, False])

    top_papers = []
    for family in FAMILY_ORDER:
        sub_family = focused[focused["family"] == family]
        for mechanism in sub_family["top_mechanism"].value_counts().head(2).index:
            top = sub_family[sub_family["top_mechanism"] == mechanism].nlargest(3, "times_cited")
            for _, row in top.iterrows():
                top_papers.append(
                    {
                        "family": family,
                        "top_mechanism": mechanism,
                        "title": row["title"],
                        "year": row["year"],
                        "times_cited": row["times_cited"],
                        "system": row["system"],
                        "is_theory": row["is_theory"],
                    }
                )
    top_papers_df = pd.DataFrame(top_papers)

    return {
        "master": master,
        "family_mechanism_counts": family_mechanism_counts,
        "family_mechanism_citation_share": family_mechanism_citation,
        "family_entropy": family_entropy,
        "cuprate_decade_citation_share": cuprate_decade_citation,
        "top_family_mechanism_papers": top_papers_df,
    }


def write_report(master: pd.DataFrame, summaries: dict[str, pd.DataFrame]) -> None:
    entropy_df = summaries["family_entropy"]
    citation_df = summaries["family_mechanism_citation_share"]
    cuprate_df = summaries["cuprate_decade_citation_share"]

    def top_share(family: str) -> tuple[str, float]:
        row = citation_df[citation_df["family"] == family].sort_values("citation_share_pct", ascending=False).iloc[0]
        return row["top_mechanism"], row["citation_share_pct"]

    elemental_mech, elemental_share = top_share("elemental")
    iron_mech, iron_share = top_share("iron-based")
    heavy_mech, heavy_share = top_share("heavy-fermion")
    kagome_mech, kagome_share = top_share("kagome")
    cuprate_entropy = entropy_df.loc[entropy_df["family"] == "cuprate", "entropy_bits"].iloc[0]
    iron_entropy = entropy_df.loc[entropy_df["family"] == "iron-based", "entropy_bits"].iloc[0]
    elemental_entropy = entropy_df.loc[entropy_df["family"] == "elemental", "entropy_bits"].iloc[0]

    cuprate_2010 = (
        cuprate_df[cuprate_df["decade"] == 2010].sort_values("citation_share_pct", ascending=False).head(3)[
            ["top_mechanism", "citation_share_pct"]
        ]
    )
    cuprate_2020 = (
        cuprate_df[cuprate_df["decade"] == 2020].sort_values("citation_share_pct", ascending=False).head(3)[
            ["top_mechanism", "citation_share_pct"]
        ]
    )

    lines = [
        "# Superconductivity story",
        "",
        "## Main finding",
        "",
        "The data separates superconductivity families by how settled their mechanism narratives are. Elemental superconductors look comparatively settled around electron-phonon coupling, iron-based and heavy-fermion systems cluster strongly around AFM fluctuation stories, while cuprates remain the most pluralistic and unstable debate arena in the corpus.",
        "",
        "## Evidence",
        "",
        f"- Elemental papers are dominated by {MECHANISM_LABELS[elemental_mech]} with {elemental_share:.1f}% of citation share and low diversity ({elemental_entropy:.2f} bits).",
        f"- Iron-based papers are dominated by {MECHANISM_LABELS[iron_mech]} with {iron_share:.1f}% citation share, stronger consensus than cuprates ({iron_entropy:.2f} bits).",
        f"- Heavy-fermion papers also center on {MECHANISM_LABELS[heavy_mech]} with {heavy_share:.1f}% citation share.",
        f"- Kagome papers already show an early concentration around {MECHANISM_LABELS[kagome_mech]} with {kagome_share:.1f}% citation share.",
        f"- Cuprates have the highest mechanism diversity in the main families at {cuprate_entropy:.2f} bits, with citation weight split across AFM fluctuation, charge density wave, and pure electronic correlation.",
        "",
        "## Cuprate shift",
        "",
        "The cuprate story also changes over time instead of converging:",
        "",
        f"- 2010s top three: {', '.join(f'{MECHANISM_LABELS[row.top_mechanism]} {row.citation_share_pct:.1f}%' for row in cuprate_2010.itertuples())}.",
        f"- 2020s top three: {', '.join(f'{MECHANISM_LABELS[row.top_mechanism]} {row.citation_share_pct:.1f}%' for row in cuprate_2020.itertuples())}.",
        "",
        "## Caveat",
        "",
        "These results depend on GPT-extracted mechanism labels from abstracts, so they are best treated as a structured map of discourse rather than a final statement of physical truth.",
    ]

    (OUT_DIR / "story_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    sns.set_theme(style="whitegrid")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    master = prepare_master_table()
    summaries = build_summaries(master)

    summaries["master"].to_csv(OUT_DIR / "master_story_table.csv", index=False)
    summaries["family_mechanism_counts"].to_csv(OUT_DIR / "family_mechanism_counts.csv", index=False)
    summaries["family_mechanism_citation_share"].to_csv(OUT_DIR / "family_mechanism_citation_share.csv", index=False)
    summaries["family_entropy"].to_csv(OUT_DIR / "family_entropy.csv", index=False)
    summaries["cuprate_decade_citation_share"].to_csv(OUT_DIR / "cuprate_decade_citation_share.csv", index=False)
    summaries["top_family_mechanism_papers"].to_csv(OUT_DIR / "top_family_mechanism_papers.csv", index=False)

    save_plot_family_citation_heatmap(summaries["family_mechanism_citation_share"])
    save_plot_family_entropy(summaries["family_entropy"])
    save_plot_cuprate_timeline(summaries["cuprate_decade_citation_share"])
    write_report(master, summaries)

    # Write family column back to SC_final_data_5k.csv
    five_k_path = SC_ANALYSIS_DIR / "SC_final_data_5k.csv"
    five_k = pd.read_csv(five_k_path)
    family_map = master.set_index("id")["family"]
    five_k["family"] = five_k["id"].map(family_map)
    five_k.to_csv(five_k_path, index=False)
    print("Added 'family' column to", five_k_path)

    print("Wrote analysis outputs to", OUT_DIR)


if __name__ == "__main__":
    main()
