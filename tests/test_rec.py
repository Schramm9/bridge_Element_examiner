# -*- coding: utf-8 -*-
"""
Created on Sun Dec 28 18:46:05 2025

@author: Chris
"""
import pytest

from from_fhwa.state_fips_rec import StateDataset, StateRegistry


def test_state_dataset_creation():
    """
    StateDataset should store metadata exactly as provided.
    """
    dataset = StateDataset(
        state_abbr="CA",
        year=2024,
        dataset_type="bridge_element_data",
        url="https://example.com/2024CA_ElementData.zip",
    )

    assert dataset.state_abbr == "CA"
    assert dataset.year == 2024
    assert dataset.dataset_type == "bridge_element_data"
    assert dataset.url.endswith(".zip")


def test_state_registry_add_and_list():
    """
    StateRegistry should store datasets and return them.
    """
    registry = StateRegistry()

    dataset = StateDataset(
        state_abbr="CA",
        year=2024,
        dataset_type="bridge_element_data",
        url="https://example.com/2024CA_ElementData.zip",
    )

    registry.add(dataset)

    all_datasets = registry.all()
    assert len(all_datasets) == 1
    assert all_datasets[0].state_abbr == "CA"


def test_filter_by_state():
    """
    Registry should filter datasets by state abbreviation.
    """
    registry = StateRegistry()

    registry.add(
        StateDataset("CA", 2024, "bridge_element_data", "https://example.com/ca.zip")
    )
    registry.add(
        StateDataset("OR", 2024, "bridge_element_data", "https://example.com/or.zip")
    )

    ca_datasets = registry.by_state("CA")

    assert len(ca_datasets) == 1
    assert ca_datasets[0].state_abbr == "CA"


def test_filter_by_dataset_type():
    """
    Registry should filter datasets by dataset type.
    """
    registry = StateRegistry()

    registry.add(
        StateDataset("CA", 2024, "bridge_element_data", "https://example.com/ca_elem.zip")
    )
    registry.add(
        StateDataset("CA", 2024, "ascii", "https://example.com/ca_ascii.txt")
    )

    element_datasets = registry.by_type("bridge_element_data")

    assert len(element_datasets) == 1
    assert element_datasets[0].dataset_type == "bridge_element_data"


def test_registry_empty_state_returns_empty_list():
    """
    Querying a missing state should return an empty list, not error.
    """
    registry = StateRegistry()

    result = registry.by_state("TX")

    assert result == []
