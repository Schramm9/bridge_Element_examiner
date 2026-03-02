# -*- coding: utf-8 -*-
"""
Created on Sun Feb 22 15:02:03 2026

@author: Chris
"""

from pathlib import Path
import xml.etree.ElementTree as ET
from collections import Counter

def local(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag

xml = Path(r"data/interim/element_xml/bridge_element_data/2020/2020CA_ElementData/2020CA_ElementData.xml")

root = ET.parse(xml).getroot()
counts = Counter(local(e.tag) for e in root.iter())

print("Unique tags:", len(counts))
print("Top 60 tags:")
for tag, n in counts.most_common(60):
    print(f"{tag:30s} {n}")
