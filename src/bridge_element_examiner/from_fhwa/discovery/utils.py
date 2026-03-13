# -*- coding: utf-8 -*-
"""
Created on Wed Dec 31 18:10:02 2025

@author: Chris
"""


from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

BASE_DOWNLOAD_URL = "https://www.fhwa.dot.gov/bridge/nbi/"

def infer_dataset_type(url: str) -> str:
    url_lower = url.lower()

    if "element" in url_lower:
        return "bridge_element_data"

    if "ascii" in url_lower or "delimited" in url_lower:
        return "ascii"

    raise ValueError(f"Unknown dataset type in URL: {url}")
