from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable
from urllib.parse import urlparse
import logging

import requests

logger = logging.getLogger(__name__)


# ---- Types ---------------------------------------------------------------

@runtime_checkable
class DatasetLike(Protocol):
    state_abbr: str
    year: int
    dataset_type: str
    url: str


# ---- Helpers -------------------------------------------------------------

def _safe_filename_from_url(url: str) -> str:
    """
    Extract a filename from the URL path. Falls back to 'download.bin' if empty.
    """
    path = urlparse(url).path
    name = Path(path).name
    return name if name else "download.bin"


def _normalize_dataset_type(dataset_type: str) -> str:
    """
    Normalize dataset_type labels so the rest of the code stays consistent.

    Accepts:
      - "element", "bridge_element_data" -> "bridge_element_data"
      - "ascii" -> "ascii"
    """
    dt = (dataset_type or "").strip().lower()

    if dt in {"bridge_element_data", "element", "elements"}:
        return "bridge_element_data"
    if dt in {"ascii"}:
        return "ascii"

    raise ValueError(f"Unknown dataset_type: {dataset_type!r}")


# ---- Public API ----------------------------------------------------------

def download_dataset(
    dataset: DatasetLike,
    *,
    data_root: Path,
    overwrite: bool = False,
    timeout: int = 30,
    chunk_size: int = 1024 * 64,
) -> Path:
    """
    Download the dataset described by `dataset` into a deterministic location.

    Parameters
    ----------
    dataset:
        Object with attributes (state_abbr, year, dataset_type, url).
        Typically your StateDataset from src/from_fhwa/state_fips_rec.py.
    data_root:
        Root directory where downloads are placed (in tests: tmp_path).
    overwrite:
        If False, raises FileExistsError when target file already exists.
    timeout:
        Requests timeout in seconds.
    chunk_size:
        Chunk size for streaming downloads.

    Returns
    -------
    Path
        Path to the downloaded file on disk.
    """
    # Basic structural validation (duck-typing)
    for attr in ("state_abbr", "year", "dataset_type", "url"):
        if not hasattr(dataset, attr):
            raise TypeError(f"dataset must have attribute {attr!r}")

    state_abbr = str(dataset.state_abbr).strip().upper()
    year = int(dataset.year)
    dataset_type = _normalize_dataset_type(str(dataset.dataset_type))
    url = str(dataset.url).strip()

    if len(state_abbr) != 2:
        raise ValueError(f"state_abbr must be 2 letters, got {state_abbr!r}")

    if not isinstance(data_root, Path):
        raise TypeError("data_root must be a pathlib.Path")

    if year < 1990:
        # adjust later if you want; this is just a sanity floor
        raise ValueError(f"year looks invalid: {year}")

    if not url.startswith("http"):
        raise ValueError(f"url must be http(s), got {url!r}")

    # Deterministic destination path:
    # data_root / <dataset_type> / <year> / <state_abbr> / <filename>
    filename = _safe_filename_from_url(url)
    dest_dir = data_root / dataset_type / str(year) / state_abbr
    dest_dir.mkdir(parents=True, exist_ok=True)

    destination = dest_dir / filename
    tmp_path = destination.with_suffix(destination.suffix + ".tmp")

    if destination.exists() and not overwrite:
        raise FileExistsError(f"File already exists: {destination}")

    logger.info("Downloading %s %s %s from %s", dataset_type, year, state_abbr, url)

    try:
        with requests.get(url, stream=True, timeout=timeout) as resp:
            resp.raise_for_status()
            with open(tmp_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=chunk_size):
                    if chunk:  # filter keep-alive chunks
                        f.write(chunk)
    except requests.RequestException as exc:
        # cleanup temp file if partially written
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except OSError:
            pass
        raise RuntimeError(f"Failed to download dataset from {url}") from exc

    if not tmp_path.exists() or tmp_path.stat().st_size == 0:
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except OSError:
            pass
        raise RuntimeError("Downloaded file is empty")

    # Atomic replace into final destination
    tmp_path.replace(destination)

    logger.info("Saved to %s", destination)
    return destination
