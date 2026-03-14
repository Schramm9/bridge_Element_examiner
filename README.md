# bridge_Element_examiner

An examination of the data provided by the FHWA NBI for an individual state.

State: California
Year: 2024 or latest available
Dataset: Element
Target: PoorConditionFlag prediction
Coast Distance: Optional (if stable by day 7)
Project scope (CA, 2024, Element)
Confirmed paths where raw zip/xml live
Confirmed that CS1 + CS2 + CS3 + CS4 == TOTALQTY for all rows

Bridge Element Examiner

Predicting deterioration risk in California bridge elements using FHWA National Bridge Inventory data, machine learning, and geospatial analysis.

Overview

Bridge infrastructure deterioration is influenced by structural condition, traffic loading, age, and environmental exposure.

This project builds a data pipeline and machine learning model that analyzes bridge element condition data and predicts the probability that a bridge element's condition will worsen in the following inspection cycle.

The results are presented through an interactive Streamlit dashboard that allows users to explore deterioration patterns across California bridges.

Key capabilities include:

automated FHWA data ingestion

multi-year bridge element dataset construction

feature engineering

machine learning deterioration prediction

geospatial risk visualization

interactive dashboard exploration

Data Sources

This project uses publicly available datasets from the Federal Highway Administration (FHWA).

Primary sources:

Bridge Element Data
https://www.fhwa.dot.gov/bridge/nbi/element.cfm

NBI Inventory Data
https://www.fhwa.dot.gov/bridge/nbi/ascii.cfm

The dataset includes:

bridge element inspection data

condition states (CS1–CS4)

bridge characteristics

traffic counts

bridge age

geographic location

This project focuses on California bridges from 2016–2025.

Dataset scale:

~713,000 bridge element observations

~11,200 unique bridges

89 element types

Feature Engineering

Several engineered features were created to support deterioration modeling.

Examples:

Condition Metrics

PCT_CS1 – PCT_CS4

PCT_POOR

DELTA_PCT_POOR

These summarize condition distribution across inspection cycles.

Structural Features

bridge age

traffic volume (ADT)

element type

inspection year

Environmental Exposure

A geospatial feature was engineered:

Distance to Pacific coastline

DIST_TO_COAST_KM

This approximates exposure to coastal corrosion environments.

Bridge coordinates were converted from FHWA coordinate format to decimal degrees.

Machine Learning Model

A baseline deterioration model was trained to predict whether an element will worsen in the next inspection period.

Target variable:

WORSENED

Model:

Random Forest Classifier

Dataset split:

Train: ~534k rows

Test: ~178k rows

Results:

Metric Value
ROC AUC ~0.96
Recall ~0.93
Precision ~0.22
F1 Score ~0.35

The model prioritizes high recall, meaning it successfully identifies most deterioration events.

Important predictors include:

condition state proportions

bridge age

traffic volume

geographic location

environmental exposure

Dashboard

The project includes an interactive Streamlit dashboard.

Features include:

Executive summary metrics

deterioration rates

bridge counts

dataset statistics

Exploratory analysis

deterioration trends over time

deterioration vs traffic

deterioration vs bridge age

Element-level analysis

highest risk element types

condition distributions

Geospatial risk map

Interactive California map displaying predicted deterioration risk by bridge.

Risk ranking table

Shows bridges with the highest predicted deterioration risk.

Feature importance visualization

Displays the most influential predictors in the ML model.

Example Dashboard Controls

Users can filter analysis by:

year range

element type

traffic volume

bridge age

deterioration events

The map and analytics update dynamically.
