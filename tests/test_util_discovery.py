# -*- coding: utf-8 -*-
"""
Created on Wed Dec 31 19:30:34 2025

@author: Chris
"""

import pytest
from from_fhwa.discovery.utils import infer_dataset_type


def test_infer_dataset_type_element():
    url = "https://www.fhwa.dot.gov/bridge/nbi/2024/2024CA_ElementData.zip"
    assert infer_dataset_type(url) == "bridge_element_data"


def test_infer_dataset_type_ascii():
    url = "https://www.fhwa.dot.gov/bridge/nbi/2020/delimited/CA20.txt"
    assert infer_dataset_type(url) == "ascii"


def test_infer_dataset_type_unknown():
    url = "https://example.com/unknown_format.zip"
    with pytest.raises(ValueError):
        infer_dataset_type(url)
