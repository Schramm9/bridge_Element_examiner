# -*- coding: utf-8 -*-
"""
Created on Mon Jan 19 16:44:52 2026

@author: Chris
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import xml.etree.ElementTree as ET


def _local(tag: str) -> str:
    """Strip XML namespace: '{ns}TAG' -> 'TAG'."""
    return tag.split("}")[-1] if "}" in tag else tag


def _find_first_text(root: ET.Element, wanted: set[str]) -> str | None:
    """Find first element whose local tag matches wanted and return stripped text."""
    for el in root.iter():
        if _local(el.tag) in wanted:
            if el.text is not None:
                t = el.text.strip()
                if t != "":
                    return t
    return None


def _iter_records_by_container(root: ET.Element) -> Iterable[ET.Element]:
    """
    Yield candidate 'record' containers.

    FHWA element XML often has repeating containers per element observation.
    We try common container names but also fall back to heuristics.
    """
    # Common container tag guesses; adjust once you inspect one XML file.
    candidate_tags = {"FHWAED"}
    for el in root.iter():
        if _local(el.tag) in candidate_tags:
            yield el

    # Fallback: if nothing matched, return root (so parser still returns something)
    # NOTE: Caller will handle whether it produced rows or not.
    # (We don't "yield root" here to avoid duplicating if we matched candidates.)
    return


def _get_child_text(container: ET.Element, tag_names: set[str]) -> str | None:
    for el in container.iter():
        if _local(el.tag) in tag_names:
            if el.text is not None:
                t = el.text.strip()
                if t != "":
                    return t
    return None


def parse_element_xml_file(xml_path: Path, *, state_abbr: str, year: int) -> pd.DataFrame:
    xml_path = Path(xml_path)
    root = ET.parse(xml_path).getroot()

    # fallback if a record is missing STRUCNUM (rare)
    fallback_strucnum = _find_first_text(root, {"STRUCNUM", "STRUCTURE_NUMBER", "STRUCTURENO", "STRUCTURE_NO"})

    rows: list[dict[str, Any]] = []
    containers = list(_iter_records_by_container(root))

    if containers:
        for rec in containers:
            rec_state = _get_child_text(rec, {"STATE"}) or state_abbr
            rec_strucnum = _get_child_text(rec, {"STRUCNUM"}) or fallback_strucnum

            element_id = _get_child_text(rec, {"EN", "ELEMENT", "ELEMENTNO", "ELEMENT_NO", "ELEMNO"})
            totalqty = _get_child_text(rec, {"TOTALQTY"})
            cs1 = _get_child_text(rec, {"CS1", "CONDSTATE1", "CONDITIONSTATE1"})
            cs2 = _get_child_text(rec, {"CS2", "CONDSTATE2", "CONDITIONSTATE2"})
            cs3 = _get_child_text(rec, {"CS3", "CONDSTATE3", "CONDITIONSTATE3"})
            cs4 = _get_child_text(rec, {"CS4", "CONDSTATE4", "CONDITIONSTATE4"})

            if any(v is not None for v in (rec_strucnum, element_id, cs1, cs2, cs3, cs4)):
                rows.append(
                    {
                        "STATE_ABBR": state_abbr,
                        "STATE_CODE": rec_state, # "06" in this case
                        "YEAR": year,
                        "STRUCNUM": rec_strucnum,
                        "ELEMENT": element_id,
                        "TOTALQTY": totalqty,
                        "CS1": cs1,
                        "CS2": cs2,
                        "CS3": cs3,
                        "CS4": cs4,
                        "SOURCE_XML": str(xml_path),
                    }
                )

    if not rows:
        rows.append(
            {
                "STATE": state_abbr,
                "YEAR": year,
                "STRUCNUM": fallback_strucnum,
                "ELEMENT": None,
                "TOTALQTY": None,
                "CS1": None,
                "CS2": None,
                "CS3": None,
                "CS4": None,
                "SOURCE_XML": str(xml_path),
            }
        )

    df = pd.DataFrame(rows)

    # Coerce numeric columns (optional, but helpful)
    for col in ("TOTALQTY", "CS1", "CS2", "CS3", "CS4"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def iter_extracted_xml_paths(
    *,
    interim_root: Path,
    state_abbr: str | None = None,
    years: set[int] | None = None,
) -> list[Path]:
    """
    Find extracted XML files under:
      interim_root/element_xml/<year>/<state>/**.xml
    """
    interim_root = Path(interim_root)
    base = interim_root / "element_xml"
    if not base.exists():
        return []

    xmls: list[Path] = []

    for year_dir in base.iterdir():
        if not year_dir.is_dir():
            continue
        if years is not None:
            try:
                y = int(year_dir.name)
            except ValueError:
                continue
            if y not in years:
                continue

        if state_abbr:
            st_dir = year_dir / state_abbr.upper()
            if st_dir.exists():
                xmls.extend(sorted(st_dir.rglob("*.xml")))
        else:
            xmls.extend(sorted(year_dir.rglob("*.xml")))

    return sorted(xmls)


def parse_element_xml_batch(
    *,
    interim_root: Path,
    state_abbr: str,
    years: set[int] | None = None,
) -> pd.DataFrame:
    """
    Parse many XML files for one state (optionally filtered by years).
    """
    interim_root = Path(interim_root)
    xml_paths = iter_extracted_xml_paths(interim_root=interim_root, state_abbr=state_abbr, years=years)

    frames: list[pd.DataFrame] = []
    for xp in xml_paths:
        # infer <year>/<state> from .../element_xml/<year>/<state>/...
        year = int(xp.parts[-(len(xp.parts) - xp.parts.index("element_xml") - 1)])  # a bit brittle
        # safer inference:
        # element_xml/<year>/<state>/...
        # Find 'element_xml' index:
        parts = list(xp.parts)
        idx = parts.index("element_xml")
        year = int(parts[idx + 1])
        st = parts[idx + 2]

        frames.append(parse_element_xml_file(xp, state_abbr=st, year=year))

    if not frames:
        return pd.DataFrame(columns=["STATE", "YEAR", "STRUCNUM", "ELEMENT", "CS1", "CS2", "CS3", "CS4", "SOURCE_XML"])

    return pd.concat(frames, ignore_index=True)
