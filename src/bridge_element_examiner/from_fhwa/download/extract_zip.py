# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 18:25:08 2026

@author: Chris
"""

from __future__ import annotations

from pathlib import Path
import zipfile


def extract_zip(*, zip_path: Path, extract_dir: Path | None = None, overwrite: bool = False) -> Path:
    """
    Extract a ZIP file. By default extracts next to the zip into a folder with the zip stem.

    Example:
      zip: .../2024CA_ElementData.zip
      extract_dir default: .../2024CA_ElementData/

    Returns:
      Path to extraction directory.
    """
    if not zip_path.exists():
        raise FileNotFoundError(zip_path)

    if not zipfile.is_zipfile(zip_path):
        raise RuntimeError(f"Not a valid zip: {zip_path}")

    if extract_dir is None:
        extract_dir = zip_path.parent / zip_path.stem

    extract_dir.mkdir(parents=True, exist_ok=True)

    # If already extracted and not overwriting, just return
    if not overwrite:
        # quick heuristic: if folder contains files, assume extracted
        if any(extract_dir.iterdir()):
            return extract_dir

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_dir)

    return extract_dir
