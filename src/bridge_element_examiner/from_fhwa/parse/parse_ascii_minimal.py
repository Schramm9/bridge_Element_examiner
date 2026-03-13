from __future__ import annotations

# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 14:12:31 2026

@author: Chris
"""

"""
Minimal FHWA ASCII parser for California bridge inventory fields needed for modeling.
"""



from pathlib import Path
import pandas as pd


# FHWA NBI fixed-width positions (1-indexed in spec, 0-indexed/end-exclusive here):
# STRUCNUM   4-18
# LAT        130-137
# LONG       138-146
# YEARBUILT  157-160
# ADT        165-170
_COLSPECS = [
    (3, 18),     # STRUCNUM
    (129, 137),  # LAT
    (137, 146),  # LONG
    (156, 160),  # YEARBUILT
    (164, 170),  # ADT
]

_NAMES = ["STRUCNUM", "LAT", "LONG", "YEARBUILT", "ADT"]


def parse_ascii_minimal(
    *,
    ascii_path: Path,
    year: int,
    state_abbr: str,
) -> pd.DataFrame:
    """
    Parse a FHWA NBI ASCII fixed-width (no-delimiter) state file.

    Returns:
        STATE_ABBR, YEAR, STRUCNUM, LAT, LONG, YEARBUILT, ADT
    """
    if not ascii_path.exists():
        raise FileNotFoundError(ascii_path)

    df = pd.read_fwf(
        ascii_path,
        colspecs=_COLSPECS,
        names=_NAMES,
        dtype=str,
        header=None,
    )

    df["STRUCNUM"] = df["STRUCNUM"].astype(str).str.strip()

    # Numeric conversions
    df["YEARBUILT"] = pd.to_numeric(
        df["YEARBUILT"].astype(str).str.strip(),
        errors="coerce",
    ).astype("Int64")

    df["ADT"] = pd.to_numeric(
        df["ADT"].astype(str).str.strip(),
        errors="coerce",
    ).astype("Int64")

    # NBI lat/long are encoded numerically in the fixed-width record.
    # Keep raw numeric versions first; convert later if needed.
    df["LAT"] = pd.to_numeric(
        df["LAT"].astype(str).str.strip(),
        errors="coerce",
    )

    df["LONG"] = pd.to_numeric(
        df["LONG"].astype(str).str.strip(),
        errors="coerce",
    )

    df["YEAR"] = int(year)
    df["STATE_ABBR"] = state_abbr.upper().strip()

    df = df[df["STRUCNUM"].notna() & (df["STRUCNUM"] != "")].copy()

    return df[["STATE_ABBR", "YEAR", "STRUCNUM", "LAT", "LONG", "YEARBUILT", "ADT"]]
