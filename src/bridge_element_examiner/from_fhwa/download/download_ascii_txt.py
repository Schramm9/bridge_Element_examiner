# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 12:38:41 2026

@author: Chris
"""

from __future__ import annotations

from pathlib import Path
import logging

from .http_download import download_to_path

log = logging.getLogger("fhwa")


def download_ascii_txt(
    *,
    year: int,
    state_abbr: str,
    project_root: Path,
    delimited: bool = False,
    overwrite: bool = False,
) -> Path:
    """
    Download FHWA NBI ASCII fixed-width (no-delimiter) state file.

    Example CA 2024: https://www.fhwa.dot.gov/bridge/nbi/2024/CA24.txt
    """
    state_abbr = state_abbr.upper().strip()
    yy = str(year)[-2:]
    fname = f"{state_abbr}{yy}.txt"

    if delimited:
        url = f"https://www.fhwa.dot.gov/bridge/nbi/{year}/delimited/{fname}"
    else:
        url = f"https://www.fhwa.dot.gov/bridge/nbi/{year}/{fname}"

    outdir = project_root / "data" / "raw" / "ascii" / str(year) / state_abbr
    outpath = outdir / fname

    return download_to_path(url=url, outpath=outpath, overwrite=overwrite)
