# -*- coding: utf-8 -*-
"""
Created on Tue Dec 23 20:42:10 2025

@author: Chris
"""
from pathlib import Path
import requests

def download_dataset(dataset, target_dir: Path) -> Path:
    """
    Download a dataset to the target directory.

    Parameters
    ----------
    dataset : StateDataset
        Dataset metadata containing a download URL.
    target_dir : Path
        Directory where the file will be saved.

    Returns
    -------
    Path
        Path to the downloaded file.
    """
    target_dir.mkdir(parents=True, exist_ok=True)

    # Preserve original filename from URL
    filename = dataset.url.split("/")[-1]
    target_path = target_dir / filename

    response = requests.get(dataset.url, stream=True)
    response.raise_for_status()

    with open(target_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    return target_path
