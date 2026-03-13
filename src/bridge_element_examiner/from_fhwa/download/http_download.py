# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 12:37:05 2026

@author: Chris
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

import requests

log = logging.getLogger("fhwa")


def download_to_path(
    *,
    url: str,
    outpath: Path,
    overwrite: bool = False,
    timeout: int = 120,
    max_tries: int = 6,
    chunk_size: int = 1024 * 1024,
) -> Path:
    """
    Robust downloader:
    - streams to disk
    - retries on connection errors
    - writes to outpath.tmp then atomically replaces outpath
    - supports simple resume if server honors Range (best-effort)
    """
    outpath.parent.mkdir(parents=True, exist_ok=True)

    if outpath.exists() and not overwrite:
        return outpath

    tmp = outpath.with_suffix(outpath.suffix + ".tmp")

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    for attempt in range(1, max_tries + 1):
        try:
            existing = tmp.stat().st_size if tmp.exists() else 0
            headers = {}
            if existing > 0:
                headers["Range"] = f"bytes={existing}-"

            log.info(f"GET {url} -> {outpath.name} (attempt {attempt}/{max_tries}, resume={existing>0})")

            with session.get(url, stream=True, timeout=timeout, headers=headers, allow_redirects=True) as r:
                r.raise_for_status()

                # If we tried Range but server replied with 200, it ignored resume; restart tmp.
                if existing > 0 and r.status_code == 200 and "Range" in headers:
                    tmp.unlink(missing_ok=True)
                    existing = 0

                mode = "ab" if existing > 0 else "wb"
                with open(tmp, mode) as f:
                    for chunk in r.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)

            # Atomic replace
            tmp.replace(outpath)
            return outpath

        except Exception as e:
            log.warning(f"Download failed: {type(e).__name__}: {e}")
            time.sleep(2 * attempt)

    raise RuntimeError(f"Failed to download after {max_tries} tries: {url}")
