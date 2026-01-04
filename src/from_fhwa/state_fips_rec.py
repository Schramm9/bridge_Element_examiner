# -*- coding: utf-8 -*-
"""
Created on Sun Dec 28 18:40:19 2025

@author: Chris
"""

# src/fhwa/state_fips_rec.py

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

BASE_DOWNLOAD_URL = "https://www.fhwa.dot.gov/bridge/nbi/"

@dataclass()
class StateDataset:
    state_abbr: str
    year: int
    dataset_type: str
    url: str

    def __post_init__(self):
        """
        Normalize and validate dataset_type.
        """

        normalized = self._normalize_dataset_type(self.dataset_type)
        self.dataset_type = normalized

    @staticmethod
    def _normalize_dataset_type(value: str) -> str:
        """
        Convert user-friendly or legacy dataset_type values into
        canonical internal values.
        """

        value = value.strip().lower()

        if value in {"element", "bridge_element_data", "bridge-element"}:
            return "bridge_element_data"

        if value in {"ascii", "asciidata"}:
            return "ascii"

        raise ValueError(
            "dataset_type must be one of: "
            "'element', 'bridge_element_data', or 'ascii' "
            f"(got '{value}')"
        )


class StateRegistry:
    def __init__(self):
        self._datasets = []

    def add(self, dataset):
        self._datasets.append(dataset)

    def all(self):
        return list(self._datasets)

    def by_state(self, state_abbr):
        return [d for d in self._datasets if d.state_abbr == state_abbr]

    def by_type(self, dataset_type):
        return [d for d in self._datasets if d.dataset_type == dataset_type]


def build_registry(zip_links: list[str]) -> StateRegistry:
    registry = StateRegistry()

    for link in zip_links:
        parts = link.split("/")
        year = int(parts[1])

        filename = parts[-1]
        state = filename[4:6]  # "2024CA_ElementData.zip"

        registry.add(
            state=state,
            year=year,
            relative_path=link
        )

    return registry
