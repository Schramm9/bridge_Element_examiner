# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 12:39:32 2026

@author: Chris
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ..download.download_element_zip import download_element_zip
from ..download.download_ascii_txt import download_ascii_txt

log = logging.getLogger("fhwa")


USPS_STATES_AND_TERR = [
    "AL","AK","AZ","AR","CA","CO","CT","DE","DC","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME",
    "MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI",
    "SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY",
    "PR","VI","GU","AS","MP",
]


def bulk_download_element_and_ascii(
    *,
    project_root: Path,
    years: list[int],
    states: list[str] | None = None,
    overwrite: bool = False,
    max_workers: int = 4,
) -> None:
    """
    Downloads element zips and ascii txts for every (year, state) pair.
    Skips existing files unless overwrite=True.
    """
    if states is None:
        states = USPS_STATES_AND_TERR

    tasks = []
    for y in years:
        for st in states:
            tasks.append((y, st))

    log.info(f"Bulk download plan: {len(tasks)} (year,state) pairs")

    def _one(y: int, st: str) -> tuple[int, str, str]:
        # ASCII almost always exists; download first
        download_ascii_txt(year=y, state_abbr=st, project_root=project_root, overwrite=overwrite)

        # Element ZIP is optional; skip 404s
        try:
            download_element_zip(year=y, state_abbr=st, project_root=project_root, overwrite=overwrite)
            return (y, st, "ok")
        except RuntimeError as e:
            if "HTTP 404" in str(e):
                log.warning(f"Element missing (skip): {st} {y}")
                return (y, st, "element_missing")
            raise
