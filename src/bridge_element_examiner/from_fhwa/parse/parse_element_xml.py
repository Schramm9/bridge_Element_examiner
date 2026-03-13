# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 18:27:44 2026

@author: Chris
"""

from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET
import pandas as pd


def parse_element_xml(*, xml_path: Path, year: int, state_abbr: str) -> pd.DataFrame:
    """
    Parse FHWA NBI Element XML file into a flat DataFrame.

    Expected structure (as you saw):
      <FHWAELEMENT>
        <FHWAED>
          <STATE>06</STATE>
          <STRUCNUM>01 0002</STRUCNUM>
          <EN>16</EN>
          <TOTALQTY>178</TOTALQTY>
          <CS1>172</CS1>
          <CS2>0</CS2>
          <CS3>6</CS3>
          <CS4>0</CS4>
        </FHWAED>
        ...
      </FHWAELEMENT>
    """
    if not xml_path.exists():
        raise FileNotFoundError(xml_path)

    tree = ET.parse(xml_path)
    root = tree.getroot()

    rows: list[dict] = []
    for rec in root.findall("FHWAED"):
        rows.append(
            {
                "STATE": rec.findtext("STATE"),
                "STRUCNUM": rec.findtext("STRUCNUM"),
                "ELEMENT": rec.findtext("EN"),
                "TOTALQTY": rec.findtext("TOTALQTY"),
                "CS1": rec.findtext("CS1"),
                "CS2": rec.findtext("CS2"),
                "CS3": rec.findtext("CS3"),
                "CS4": rec.findtext("CS4"),
            }
        )

    df = pd.DataFrame(rows)

    # numeric conversions
    num_cols = ["STATE", "ELEMENT", "TOTALQTY", "CS1", "CS2", "CS3", "CS4"]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    df["YEAR"] = int(year)
    df["STATE_ABBR"] = state_abbr.upper().strip()

    # integrity check: CS sum equals TOTALQTY
    diff = (df["CS1"] + df["CS2"] + df["CS3"] + df["CS4"] - df["TOTALQTY"])
    if not (diff.fillna(0) == 0).all():
        bad = diff.ne(0).sum()
        raise RuntimeError(f"Integrity check failed for {xml_path}: {bad} rows where CS sum != TOTALQTY")

    return df
