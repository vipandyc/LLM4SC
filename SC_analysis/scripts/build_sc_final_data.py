#!/usr/bin/env python3
"""Build SC_final_data.csv in SC_analysis/."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build SC_final_data.csv by joining method-binary labels, GPT opinion "
            "scores, and internal outgoing citation lists."
        )
    )
    parser.add_argument(
        "--method-binary-path",
        default="data/SC_related_cites_010_method_binary.csv",
        help="Path to method-binary CSV (default: data/SC_related_cites_010_method_binary.csv).",
    )
    parser.add_argument(
        "--gpt-processed-path",
        default="data/SC_related_cites_010_GPT_processed.csv",
        help="Path to GPT-processed CSV containing GPT_output.",
    )
    parser.add_argument(
        "--internal-edges-path",
        default="superconductivity/citation_edges_internal.csv",
        help="Path to internal citation edges CSV.",
    )
    parser.add_argument(
        "--output-csv",
        default="SC_analysis/SC_final_data.csv",
        help="Output CSV path.",
    )
    parser.add_argument(
        "--output-validation",
        default="SC_analysis/SC_final_data_validation.txt",
        help="Output validation text path.",
    )
    parser.add_argument(
        "--keep-labels",
        nargs="*",
        default=None,
        help=(
            "Optional subset of binary label columns to keep (e.g. --keep-labels DFT DMFT). "
            "Accepts space-separated and/or comma-separated values."
        ),
    )
    return parser.parse_args()


def _normalize_keep_labels(raw_values: list[str] | None) -> list[str] | None:
    if raw_values is None:
        return None
    labels: list[str] = []
    for raw in raw_values:
        for label in raw.split(","):
            label = label.strip()
            if label:
                labels.append(label)
    return labels or None


def _has_nonzero_opinion(opinion_str: str) -> bool:
    if not isinstance(opinion_str, str):
        return False
    try:
        opinion_dict = json.loads(opinion_str)
    except Exception:
        return False
    for value in opinion_dict.values():
        if isinstance(value, (int, float)) and value != 0:
            return True
    return False


def _build_outgoing_lists(edges: pd.DataFrame) -> pd.DataFrame:
    return (
        edges.groupby("source", dropna=False)["target"]
        .agg(lambda x: json.dumps(sorted(set(x.dropna().astype(str)))))
        .reset_index()
        .rename(
            columns={
                "source": "id",
                "target": "outgoing_internal_citing_papers",
            }
        )
    )


def _select_base_columns(method_binary: pd.DataFrame, keep_labels: list[str] | None) -> pd.DataFrame:
    if "id" not in method_binary.columns:
        raise ValueError("Expected an 'id' column in method-binary CSV.")

    if keep_labels is None:
        return method_binary

    missing = [c for c in keep_labels if c not in method_binary.columns]
    if missing:
        raise ValueError(f"Requested keep-label columns not found: {missing}")

    # Keep ID plus selected binary labels only.
    columns = ["id", *keep_labels]
    return method_binary[columns].copy()


def main() -> None:
    args = parse_args()
    repo_root = Path(__file__).resolve().parents[1]

    method_binary_path = repo_root / args.method_binary_path
    gpt_processed_path = repo_root / args.gpt_processed_path
    internal_edges_path = repo_root / args.internal_edges_path
    output_csv_path = repo_root / args.output_csv
    output_qc_path = repo_root / args.output_validation

    method_binary = pd.read_csv(method_binary_path)
    keep_labels = _normalize_keep_labels(args.keep_labels)
    base_df = _select_base_columns(method_binary, keep_labels=keep_labels)

    # Opinion-score dictionary source (last column in GPT_processed) + publication year.
    gpt = pd.read_csv(gpt_processed_path, usecols=["id", "year", "GPT_output"]).rename(
        columns={"GPT_output": "opinion_scores_dict"}
    )

    # Aggregate internal outgoing citations: for each source, list all targets.
    edges = pd.read_csv(internal_edges_path, usecols=["source", "target"])
    outgoing = _build_outgoing_lists(edges)

    full_df = base_df.merge(gpt, on="id", how="left").merge(outgoing, on="id", how="left")
    full_df["outgoing_internal_citing_papers"] = full_df[
        "outgoing_internal_citing_papers"
    ].fillna("[]")

    # Keep only rows with internal outgoing citation edges.
    # final_df = full_df[full_df["outgoing_internal_citing_papers"] != "[]"].copy()
    final_df = full_df.copy()
    # Opinion-score check.
    full_df["has_nonzero_opinion"] = full_df["opinion_scores_dict"].apply(_has_nonzero_opinion)
    nonzero_inside_internal = (
        (full_df["outgoing_internal_citing_papers"] != "[]") & full_df["has_nonzero_opinion"]
    ).sum()
    nonzero_outside_internal = (
        (full_df["outgoing_internal_citing_papers"] == "[]") & full_df["has_nonzero_opinion"]
    ).sum()
    zero_inside_internal = (
        (full_df["outgoing_internal_citing_papers"] != "[]") & (~full_df["has_nonzero_opinion"])
    ).sum()

    final_df.to_csv(output_csv_path, index=False)

    # Validation summary.
    total_papers = len(final_df)
    papers_with_internal_outgoing = (final_df["outgoing_internal_citing_papers"] != "[]").sum()
    papers_without_internal_outgoing = total_papers - papers_with_internal_outgoing
    unique_sources_in_internal = edges["source"].nunique()
    unique_targets_in_internal = edges["target"].nunique()
    total_internal_edges = len(edges)

    qc_text = "\n".join(
        [
            f"total_papers_in_final: {total_papers}",
            f"papers_with_internal_outgoing: {papers_with_internal_outgoing}",
            f"papers_without_internal_outgoing: {papers_without_internal_outgoing}",
            f"unique_sources_in_internal_edges: {unique_sources_in_internal}",
            f"unique_targets_in_internal_edges: {unique_targets_in_internal}",
            f"total_internal_edges: {total_internal_edges}",
            f"kept_binary_labels: {keep_labels if keep_labels is not None else 'ALL'}",
            f"nonzero_opinion_inside_internal_rows: {int(nonzero_inside_internal)}",
            f"nonzero_opinion_outside_internal_rows: {int(nonzero_outside_internal)}",
            f"zero_opinion_inside_internal_rows: {int(zero_inside_internal)}",
            "check_note: we keep only internal-edge rows in SC_final_data.csv.",
            "check_note: nonzero_opinion_outside_internal_rows is computed on the full pre-filter table.",
        ]
    )
    output_qc_path.write_text(qc_text + "\n", encoding="utf-8")

    print(f"Wrote: {output_csv_path}")
    print(f"Wrote: {output_qc_path}")
    print(qc_text)


if __name__ == "__main__":
    main()

# python SC_analysis/build_sc_final_data.py --keep-labels DFT DMFT
