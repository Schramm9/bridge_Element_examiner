# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 18:23:49 2026

@author: Chris
"""

from __future__ import annotations

from pathlib import Path
import requests


def download_element_zip(
    *,
    year: int,
    state_abbr: str,
    project_root: Path,
    overwrite: bool = False,
    timeout: int = 120,
) -> Path:
    """
    Download FHWA NBI Element ZIP for a given year and state abbreviation.

    Saves to:
      {project_root}/data/raw/nbi/element/{year}/{year}{STATE}_ElementData.zip

    Returns:
      Path to the downloaded (or existing) zip file.
    """
    state_abbr = state_abbr.upper().strip()

    url = f"https://www.fhwa.dot.gov/bridge/nbi/element/{year}/{year}{state_abbr}_ElementData.zip"

    outdir = project_root / "data" / "raw" / "nbi" / "element" / str(year)
    outdir.mkdir(parents=True, exist_ok=True)

    zip_path = outdir / f"{year}{state_abbr}_ElementData.zip"

    if zip_path.exists() and not overwrite:
        return zip_path

    headers = {"User-Agent": "Mozilla/5.0"}

    resp = requests.get(url, stream=True, headers=headers, timeout=timeout, allow_redirects=True)
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code} for {url} (final: {resp.url})")

    # Optional but helpful debug signal if FHWA ever returns HTML:
    ctype = (resp.headers.get("Content-Type") or "").lower()
    if "text/html" in ctype:
        # Still might be a valid download in rare cases, but usually indicates an error page.
        raise RuntimeError(f"Got HTML instead of zip for {url} (final: {resp.url})")

    with open(zip_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)

    return zip_path
