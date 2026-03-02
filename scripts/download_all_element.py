# -*- coding: utf-8 -*-
"""
Created on Wed Jan 14 22:27:49 2026

@author: Chris
"""

"""
Bulk-download all discovered FHWA NBI element datasets.

Usage:
    python scripts/download_all_element.py

Behavior:
- Discovers what exists (no hardcoded years/states)
- Downloads each dataset via download_dataset()
- Skips existing files safely (download_dataset should already do this)
- Won't crash if some combos don't exist (discovery prevents requesting missing combos)
"""


from pathlib import Path

from data.download_data import download_dataset
from from_fhwa.discovery.disc_element_links import discover_element_datasets



def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    data_root = project_root / "data" / "raw"

    datasets = discover_element_datasets()
    print(f"Discovered {len(datasets)} element datasets.")

    downloaded = 0
    skipped = 0
    failed = 0

    for ds in datasets:
        try:
            # download_dataset should:
            # - build deterministic output path under data_root
            # - skip if already present
            # - return something like a Path or status (your implementation may vary)
            result = download_dataset(ds, data_root=data_root)

            # If your download_dataset returns a Path, we can infer “skip” vs “download”
            # only if it also signals it. If not, keep it simple:
            downloaded += 1
            print(f"[OK] {ds.year} {ds.state_abbr} -> {result}")

        except FileExistsError:
            skipped += 1
            print(f"[SKIP] {ds.year} {ds.state_abbr} (already exists)")

        except Exception as e:
            failed += 1
            print(f"[FAIL] {ds.year} {ds.state_abbr}: {e}")

    print("\nSummary")
    print(f"  downloaded: {downloaded}")
    print(f"  skipped:    {skipped}")
    print(f"  failed:     {failed}")


if __name__ == "__main__":
    main()
