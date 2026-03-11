# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 11:50:22 2026

@author: Chris
"""
""" 03.07.26

From FHWA Project Plan:

    Replace the blocks of code in the dashboard to make the columns resilient.

    Update parse of parse_ascii_minimal.py that will get LAT and LONG

    Make ca_ascii_min_2016_2025.py
    Then get to the "What to run now" section and provide the
        Rows:

        Unique bridges:

        Unique elements:

        Missing share: """


# %%
from scripts.session_start import project_info, PROJECT_ROOT
project_info()

from bridge_element_examiner.from_fhwa.discovery.disc_element_links import discover_element_datasets
from bridge_element_examiner.from_fhwa.pipeline.element_pipeline import (
    parse_single_state_year,
    build_element_dataset,
)
from bridge_element_examiner.analytics.element_metrics import (
    add_condition_metrics,
    summarize_by_year,
)

# %%
""" discovery """
datasets = discover_element_datasets()
years = sorted({d.year for d in datasets}, reverse=True)
ca = [d for d in datasets if d.state_abbr == "CA"]

print(f"Found {len(datasets)} datasets")
ca[:len(ca)]

#print("Cell 1")
# %%
""" parse one known year """
df = parse_single_state_year(
    state_abbr="CA",
    year=2020,
    project_root=PROJECT_ROOT,
)
df.head()
print("Parse of one known year")

# %%
""" multi-year analytics """
df_all = build_element_dataset(
    years=sorted({d.year for d in ca}),
    state_abbr="CA",
    project_root=PROJECT_ROOT,
)

df_all_m = add_condition_metrics(df_all)
elem_summary = summarize_by_year(df_all_m, group_cols=["STATE", "YEAR", "ELEMENT"])
elem_summary.query("ELEMENT == 16").sort_values("YEAR")

# %%
""" latest CA year """
if "datasets" not in globals():
    datasets = discover_element_datasets()

latest_ca_year = max(d.year for d in datasets if d.state_abbr == "CA")
latest_ca_year

# %%
""" parse latest year """
df_latest = parse_single_state_year(
    state_abbr="CA",
    year=latest_ca_year,
    project_root=PROJECT_ROOT,
)
df_latest.head()

# %%
""" quick checks """
if "df" in globals():
    _df = df
elif "df_latest" in globals():
    _df = df_latest
else:
    raise RuntimeError("Run a parse cell first to create df or df_latest.")

_df.groupby("ELEMENT")[["CS1", "CS2", "CS3", "CS4"]].sum().sort_values("CS1", ascending=False).head(10)
