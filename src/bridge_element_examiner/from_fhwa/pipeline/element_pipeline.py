# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 18:28:32 2026

@author: Chris
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd

from ..download.download_element_zip import download_element_zip
from ..download.extract_zip import extract_zip
from ..parse.parse_element_xml import parse_element_xml

def build_element_dataset(
    *,
    years: list[int],
    state_abbr: str,
    project_root: Path,
    overwrite_download: bool = False,
    overwrite_extract: bool = False,
) -> pd.DataFrame:
    """
    End-to-end: download -> extract -> parse -> concat for multiple years (single state).
    """
    frames: list[pd.DataFrame] = []

    for year in years:
        zip_path = download_element_zip(
            year=year,
            state_abbr=state_abbr,
            project_root=project_root,
            overwrite=overwrite_download,
        )
        extract_dir = extract_zip(zip_path=zip_path, overwrite=overwrite_extract)

        xml_path = extract_dir / f"{year}{state_abbr.upper()}_ElementData.xml"
        if not xml_path.exists():
            # fallback: pick the largest xml if filename differs
            xml_files = list(extract_dir.rglob("*.xml"))
            if not xml_files:
                raise RuntimeError(f"No XML found in {extract_dir}")
            xml_path = sorted(xml_files, key=lambda p: p.stat().st_size, reverse=True)[0]

        df_year = parse_element_xml(xml_path=xml_path, year=year, state_abbr=state_abbr)
        frames.append(df_year)

    df_all = pd.concat(frames, ignore_index=True)

    # Optional ratios (handy later)
    df_all["PCT_CS1"] = df_all["CS1"] / df_all["TOTALQTY"]
    df_all["PCT_CS2"] = df_all["CS2"] / df_all["TOTALQTY"]
    df_all["PCT_CS3"] = df_all["CS3"] / df_all["TOTALQTY"]
    df_all["PCT_CS4"] = df_all["CS4"] / df_all["TOTALQTY"]

    return df_all

def parse_single_state_year(
    *,
    state_abbr: str,
    year: int,
    project_root: Path,
    overwrite_download: bool = False,
    overwrite_extract: bool = False,
) -> pd.DataFrame:
    """
    Convenience wrapper for one state + one year:
    download -> extract -> parse -> dataframe
    """
    return build_element_dataset(
        years=[year],
        state_abbr=state_abbr,
        project_root=project_root,
        overwrite_download=overwrite_download,
        overwrite_extract=overwrite_extract,
    )
