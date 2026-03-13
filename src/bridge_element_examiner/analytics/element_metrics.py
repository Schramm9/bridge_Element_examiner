# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 11:50:07 2026

@author: Chris
"""

from __future__ import annotations

import pandas as pd


ROW_LEVEL_COLS = [
    "STATE",
    "YEAR",
    "STRUCNUM",
    "ELEMENT",
    "TOTALQTY",
    "CS1",
    "CS2",
    "CS3",
    "CS4",
]

AGG_LEVEL_COLS = [
    "STATE",
    "YEAR",
    "ELEMENT",
    "TOTALQTY",
    "CS1",
    "CS2",
    "CS3",
    "CS4",
]


def validate_element_df(df: pd.DataFrame, *, require_strucnum: bool = True) -> None:
    required = ROW_LEVEL_COLS if require_strucnum else AGG_LEVEL_COLS

    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Basic sanity
    for c in ["TOTALQTY", "CS1", "CS2", "CS3", "CS4"]:
        if (df[c] < 0).any():
            raise ValueError(f"Column {c} has negative values.")

    cs_sum = df["CS1"] + df["CS2"] + df["CS3"] + df["CS4"]
    if (cs_sum > df["TOTALQTY"]).any():
        raise ValueError("CS1+CS2+CS3+CS4 exceeds TOTALQTY for some rows.")


def add_condition_metrics(
    df: pd.DataFrame,
    *,
    weights: tuple[float, float, float, float] = (4.0, 3.0, 2.0, 1.0),
) -> pd.DataFrame:
    """
    Adds:
      - CI: Condition Index on 1..4 scale (4 best)
      - GOOD_PCT: share in CS1
      - POOR_PCT: share in CS3+CS4
      - FAIR_PCT: share in CS2
      - BAD_QTY: CS3+CS4 (absolute)
    """
    validate_element_df(df, require_strucnum=("STRUCNUM" in df.columns))

    w1, w2, w3, w4 = weights
    out = df.copy()

    total = out["TOTALQTY"].replace({0: pd.NA})

    out["GOOD_PCT"] = out["CS1"] / total
    out["FAIR_PCT"] = out["CS2"] / total
    out["POOR_PCT"] = (out["CS3"] + out["CS4"]) / total
    out["BAD_QTY"] = out["CS3"] + out["CS4"]

    # Weighted average condition on 1..4 scale
    out["CI"] = (w1 * out["CS1"] + w2 * out["CS2"] + w3 * out["CS3"] + w4 * out["CS4"]) / total

    return out


def summarize_by_year(
    df: pd.DataFrame,
    *,
    group_cols: list[str] | None = None,
) -> pd.DataFrame:
    """
    Aggregates to year-level (optionally by state / element).
    Returns a tidy summary including CI and pct shares.
    """
    validate_element_df(df, require_strucnum=True)  # input is row-level
    if group_cols is None:
        group_cols = ["STATE", "YEAR"]

    g = df.groupby(group_cols, dropna=False, as_index=False).agg(
        TOTALQTY=("TOTALQTY", "sum"),
        CS1=("CS1", "sum"),
        CS2=("CS2", "sum"),
        CS3=("CS3", "sum"),
        CS4=("CS4", "sum"),
    )
    g = add_condition_metrics(g)
    return g


def add_year_over_year_change(
    df: pd.DataFrame,
    *,
    by: list[str] = ["STATE", "ELEMENT", "STRUCNUM"],
) -> pd.DataFrame:
    """
    Adds YoY deltas for CI / GOOD_PCT / POOR_PCT, computed within groups.
    Expects multiple years per group.
    """
    needed = set(by + ["YEAR"])
    if not needed.issubset(df.columns):
        raise ValueError(f"add_year_over_year_change requires columns: {sorted(needed)}")

    out = df.sort_values(by + ["YEAR"]).copy()
    if "CI" not in out.columns or "GOOD_PCT" not in out.columns or "POOR_PCT" not in out.columns:
        out = add_condition_metrics(out)

    out["CI_DY"] = out.groupby(by)["CI"].diff()
    out["GOOD_PCT_DY"] = out.groupby(by)["GOOD_PCT"].diff()
    out["POOR_PCT_DY"] = out.groupby(by)["POOR_PCT"].diff()
    return out


def transition_matrix(
    df: pd.DataFrame,
    *,
    by: list[str] = ["STATE", "ELEMENT", "STRUCNUM"],
    state_col: str = "DOM_STATE",
) -> pd.DataFrame:
    """
    Builds a simple Markov-style transition matrix year-to-year using a derived dominant state.

    Adds DOM_STATE per row = argmax(CS1..CS4).
    Then counts transitions from DOM_STATE(t) -> DOM_STATE(t+1).
    """
    validate_element_df(df, require_strucnum=("STRUCNUM" in df.columns))
    out = df.sort_values(by + ["YEAR"]).copy()

    # dominant state (ties broken by first max encountered)
    cs_cols = ["CS1", "CS2", "CS3", "CS4"]
    out[state_col] = out[cs_cols].idxmax(axis=1)  # "CS1".."CS4"

    out["NEXT_STATE"] = out.groupby(by)[state_col].shift(-1)
    pairs = out.dropna(subset=["NEXT_STATE"])

    mat = (
        pairs.groupby([state_col, "NEXT_STATE"])
        .size()
        .unstack(fill_value=0)
        .sort_index()
    )

    # Convert to probabilities row-wise
    probs = mat.div(mat.sum(axis=1).replace({0: pd.NA}), axis=0)
    probs.index.name = "FROM"
    probs.columns.name = "TO"
    return probs
