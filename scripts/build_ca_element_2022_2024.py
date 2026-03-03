# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 18:29:09 2026

@author: Chris
"""

from pathlib import Path
import sys

# Add project root to Python path so `import src...` works in Spyder
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.from_fhwa.pipeline.element_pipeline import build_element_dataset

PROJECT_ROOT = Path(r"C:\Users\Chris\CodingBootcamp\Homework\bridge_element_examiner")

YEARS = [2022, 2023, 2024]
STATE_ABBR = "CA"

df_all = build_element_dataset(
    years=YEARS,
    state_abbr=STATE_ABBR,
    project_root=PROJECT_ROOT,
    overwrite_download=False,
    overwrite_extract=False,
)

# Quick checks
print("Rows:", df_all.shape[0])
print("Unique bridges:", df_all["STRUCNUM"].nunique())
print("Unique elements:", df_all["ELEMENT"].nunique())
print("Years:", sorted(df_all["YEAR"].unique().tolist()))

# Save processed
out_processed = PROJECT_ROOT / "data" / "processed"
out_processed.mkdir(parents=True, exist_ok=True)

csv_path = out_processed / f"{STATE_ABBR.lower()}_element_{min(YEARS)}_{max(YEARS)}.csv"
df_all.to_csv(csv_path, index=False)

print("Saved:", csv_path)
print("Size bytes:", csv_path.stat().st_size)
