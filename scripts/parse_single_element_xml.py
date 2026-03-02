# -*- coding: utf-8 -*-
"""
Created on Sat Feb  7 12:11:11 2026

@author: Chris
"""

from pathlib import Path
from data.parse_element_xml import parse_element_xml_file

xml = next(Path("data/interim/element_xml").rglob("*.xml"))
print("Parsing:", xml)

df = parse_element_xml_file(xml, state_abbr="CA", year=2020)
print(df.head(20))
print("Rows:", len(df))
