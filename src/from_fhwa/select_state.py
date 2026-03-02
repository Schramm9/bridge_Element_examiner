from __future__ import annotations
#selection.py == select_state.py

# -*- coding: utf-8 -*-
"""
Created on Sun Jan 18 18:21:04 2026

@author: Chris
"""

from pathlib import Path

from typing import Iterable

from from_fhwa.discovery.disc_element_links import discover_element_datasets
from from_fhwa.discovery.disc_ascii_links import discover_ascii_datasets
from from_fhwa.state_fips_rec import StateDataset


def get_datasets_for_state(state_abbr: str) -> list[StateDataset]:
    state_abbr = state_abbr.upper()

    project_root = Path(__file__).resolve().parents[2]  # src/from_fhwa/ -> project root
    cache_dir = project_root / "data" / "cache" / "fhwa_discovery"
    element_cache = cache_dir / "element.json"
    ascii_cache = cache_dir / "ascii.json"

    element = [ds for ds in discover_element_datasets(cache_path=element_cache) if ds.state_abbr == state_abbr]
    ascii_ = [ds for ds in discover_ascii_datasets(cache_path=ascii_cache) if ds.state_abbr == state_abbr]

    return sorted(element + ascii_, key=lambda d: (d.dataset_type, d.year))
