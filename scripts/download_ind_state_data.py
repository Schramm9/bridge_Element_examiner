from pathlib import Path

from data.download_data import download_dataset
from from_fhwa.select_state import get_datasets_for_state


def main(state_abbr: str) -> None:
    project_root = Path(__file__).resolve().parents[1]
    data_root = project_root / "data" / "raw"

    datasets = get_datasets_for_state(state_abbr)
    print(f"Found {len(datasets)} datasets for {state_abbr.upper()}")

    ok = 0
    skipped = 0
    failed = 0

    pilot_years = {2025, 2020}
    datasets = [ds for ds in datasets if ds.year in pilot_years]


    for ds in datasets:
        try:
            path = download_dataset(ds, data_root=data_root, overwrite=False)
            print(f"[OK]   {ds.dataset_type} {ds.year} {ds.state_abbr} -> {path}")

        except FileExistsError:
            print(f"[SKIP] {ds.dataset_type} {ds.year} {ds.state_abbr} (already exists)")

        except Exception as e:
            print(f"[FAIL] {ds.dataset_type} {ds.year} {ds.state_abbr}: {e}")


    print("\nSummary")
    print(f"  ok:      {ok}")
    print(f"  skipped: {skipped}")
    print(f"  failed:  {failed}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/download_ind_state_data.py <STATE_ABBR>")

    main(sys.argv[1])
