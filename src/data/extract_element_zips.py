# -*- coding: utf-8 -*-
"""
Created on Mon Jan 19 16:43:22 2026

@author: Chris
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile


@dataclass(frozen=True)
class ExtractResult:
    zip_path: Path
    extracted_dir: Path
    extracted_files: list[Path]
    skipped: bool


def extract_element_zip(
    zip_path: Path,
    *,
    out_dir: Path,
    overwrite: bool = False,
) -> ExtractResult:
    """
    Extract a single element ZIP into out_dir.

    Idempotent behavior:
    - If out_dir exists and contains files, we skip unless overwrite=True.
    """
    zip_path = Path(zip_path)
    out_dir = Path(out_dir)

    if not zip_path.exists():
        raise FileNotFoundError(zip_path)

    out_dir.mkdir(parents=True, exist_ok=True)

    existing = list(out_dir.rglob("*"))
    if existing and not overwrite:
        # Already extracted (best-effort check)
        extracted_files = [p for p in existing if p.is_file()]
        return ExtractResult(zip_path, out_dir, extracted_files, skipped=True)

    # If overwrite, clear directory contents (simple + safe)
    if existing and overwrite:
        for p in sorted(existing, reverse=True):
            if p.is_file():
                p.unlink()
            elif p.is_dir():
                try:
                    p.rmdir()
                except OSError:
                    # Directory not empty; it'll be handled as we delete files
                    pass

    extracted_files: list[Path] = []
    with ZipFile(zip_path, "r") as zf:
        zf.extractall(out_dir)
        # record extracted file paths
        for name in zf.namelist():
            p = out_dir / name
            if p.exists() and p.is_file():
                extracted_files.append(p)

    return ExtractResult(zip_path, out_dir, extracted_files, skipped=False)


def iter_element_zip_paths(
    *,
    data_root: Path,
    state_abbr: str | None = None,
    years: set[int] | None = None,
) -> list[Path]:
    """
    Find element ZIPs in:
      data_root/bridge_element_data/<year>/<state>/*.zip
    """
    data_root = Path(data_root)
    base = data_root / "bridge_element_data"
    if not base.exists():
        return []

    zip_paths: list[Path] = []
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
            state_dir = year_dir / state_abbr.upper()
            if state_dir.exists():
                zip_paths.extend(sorted(state_dir.glob("*.zip")))
        else:
            for st_dir in year_dir.iterdir():
                if st_dir.is_dir():
                    zip_paths.extend(sorted(st_dir.glob("*.zip")))

    return sorted(zip_paths)


def extract_all_element_zips(
    *,
    data_root: Path,
    interim_root: Path,
    state_abbr: str | None = None,
    years: set[int] | None = None,
    overwrite: bool = False,
) -> list[ExtractResult]:
    """
    Extract all element ZIPs (optionally filtered by state and years)
    into:
      interim_root/element_xml/<year>/<state>/
    """
    data_root = Path(data_root)
    interim_root = Path(interim_root)

    results: list[ExtractResult] = []

    zip_paths = iter_element_zip_paths(data_root=data_root, state_abbr=state_abbr, years=years)
    for zp in zip_paths:
        # infer <year>/<state> from path .../bridge_element_data/<year>/<state>/<file>.zip
        year = zp.parents[2].name
        st = zp.parents[1].name

        out_dir = interim_root / "element_xml" / year / st / zp.stem
        res = extract_element_zip(zp, out_dir=out_dir, overwrite=overwrite)
        results.append(res)

    return results
