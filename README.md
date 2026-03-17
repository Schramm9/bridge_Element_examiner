Bridge Element Examiner

Machine learning and geospatial analytics pipeline for analyzing bridge element deterioration risk using FHWA National Bridge Inventory (NBI) data.

This project demonstrates an end-to-end data engineering → feature engineering → machine learning → interactive dashboard workflow applied to U.S. bridge infrastructure.

Project Impact

This project analyzes FHWA National Bridge Inventory (NBI) bridge element inspection data to identify and predict deterioration risk for bridge components in California.

The system integrates data engineering, geospatial analysis, and machine learning into a stakeholder-facing analytics dashboard.

Key Results

Dataset Construction

Processed 713,000+ bridge element observations

Covering 11,200 bridges across California

Built from multi-year FHWA inspection datasets (2016–2025)

Feature Engineering

Engineered predictive features including:

Bridge age

Average Daily Traffic (ADT)

Element condition states (CS1–CS4)

Distance to Pacific coastline (saltwater corrosion exposure)

Machine Learning Model

A baseline Random Forest deterioration model predicts whether a bridge element will deteriorate before the next inspection cycle.

Metric Value
ROC AUC 0.96
Recall 0.94
Precision 0.22

High recall ensures the model captures the majority of at-risk bridge elements.

Interactive Analytics Dashboard

A Streamlit geospatial dashboard allows users to:

visualize bridge deterioration risk across California

identify high-risk bridges in the current map view

explore environmental drivers of deterioration

analyze deterioration trends by bridge element

Example Dashboard Capabilities

The dashboard provides several analytical views of bridge infrastructure risk.

Key features include:

• Interactive bridge risk map

• Highest-risk bridges in the current map view

• Bridge element deterioration trends

• Element types with highest deterioration rates

• Machine learning predictions of deterioration probability

The interface uses Streamlit + PyDeck for interactive geospatial visualization.

System Architecture

The project implements an end-to-end data analytics pipeline.

FHWA NBI Website
│
▼
Automated Data Discovery
(Selenium + BeautifulSoup)
│
▼
Raw Data Storage
data/raw/
│
▼
XML Parsing & Cleaning
Python + Pandas
│
▼
Feature Engineering
Bridge age
Traffic load (ADT)
Condition states
Distance to coastline
│
▼
Machine Learning Model
Random Forest Classifier
│
▼
Processed Dataset
data/processed/
│
▼
Interactive Dashboard
Streamlit + PyDeck

This pipeline demonstrates capabilities in:

web scraping

data engineering

feature engineering

predictive modeling

geospatial analytics

stakeholder-facing dashboards

Project Structure
bridge_Element_examiner/

app/
dashboard.py
Streamlit dashboard application

data/
raw/
FHWA downloads

    interim/
        parsed XML data

    processed/
        modeling datasets

notebooks/
exploratory analysis

scripts/
train_baseline_deterioration_model.py
pipeline utilities

src/
reusable project modules

    from_fhwa/
        discovery and data download modules

    parsing/
        XML parsing utilities

    features/
        feature engineering code

    modeling/
        machine learning pipeline

environment.yml
pyproject.toml
README.md

The project follows a modular data science architecture, separating:

data ingestion

feature engineering

modeling

application layer

Data Source

Data originates from the Federal Highway Administration (FHWA).

Source:

FHWA National Bridge Inventory
https://www.fhwa.dot.gov/bridge/nbi/

The project uses bridge element inspection datasets provided by FHWA.

Bridge element condition states:

Condition State Meaning
CS1 Good condition
CS2 Fair condition
CS3 Poor condition
CS4 Severe condition

These condition states allow deterioration to be modeled over time.

Feature Engineering

Key predictors used in the deterioration model include:

• Bridge age
• Average Daily Traffic (ADT)
• Element condition states (CS1–CS4)
• Bridge element type
• Distance to saltwater coastline

Environmental exposure is modeled using geospatial distance calculations.

Machine Learning Model

The baseline predictive model uses:

Random Forest Classification

Target variable:
PoorConditionFlag

The model predicts the probability that a bridge element will deteriorate before the next inspection cycle.

The model prioritizes high recall to identify the largest possible share of at-risk infrastructure.

Running the Project Locally
1 Clone the repository
git clone https://github.com/<username>/bridge_Element_examiner.git
cd bridge_Element_examiner

2 Create the Conda environment
conda env create -f environment.yml
conda activate streamenv

3 Run the Streamlit dashboard
streamlit run app/dashboard.py
4 Open the application

Streamlit will launch the dashboard locally at:

http://localhost:8501

Technology Stack

Python
Pandas
NumPy
Scikit-learn
Matplotlib
Streamlit
PyDeck
BeautifulSoup
Selenium
Conda

Future Improvements

Potential extensions include:

• survival analysis for infrastructure deterioration
• Markov transition modeling of condition states
• nationwide bridge analysis across all states
• climate and corrosion exposure modeling
• predictive maintenance prioritization tools

Author

Chris Schramm

Data analytics and geospatial modeling project focused on infrastructure risk prediction.

License

MIT License
