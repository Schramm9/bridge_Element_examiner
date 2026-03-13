# -*- coding: utf-8 -*-
"""
Created on Tue Dec 23 20:42:10 2025

@author: Chris
"""
from pathlib import Path

def download_dataset(
    *,
    state: str,
    year: int,
    output_dir: Path,
    overwrite: bool = False,
) -> Path:
    """
    Download FHWA bridge dataset for a given state and year.

    Parameters
    ----------
    state : str
        Two-letter state code (e.g. 'CA')
    year : int
        Dataset year (e.g. 2023)
    output_dir : Path
        Directory where file will be saved
    overwrite : bool
        Whether to overwrite existing files

    Returns
    -------
    Path
        Path to downloaded file

    Raises
    ------
    ValueError
        Invalid state or year
    RuntimeError
        Download failed or dataset missing
    """
