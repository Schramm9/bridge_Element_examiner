Bridge Element Examiner

Element condition states:

Condition State Meaning
CS1 Good condition
CS2 Fair condition
CS3 Poor condition
CS4 Severe condition

These condition states allow deterioration trends to be modeled over time.

Feature Engineering

Key predictors used in the deterioration model include:

Bridge Age

Average Daily Traffic (ADT)

Element Condition States (CS1–CS4)

Distance to Saltwater Coastline

Bridge Element Type

Environmental exposure (coastal saltwater) is incorporated using geospatial distance calculations.

Machine Learning Model

The baseline predictive model uses:

Random Forest Classification

Target variable:

PoorConditionFlag

The model predicts the probability that a bridge element will deteriorate to a worse condition state by the next inspection cycle.

The model prioritizes high recall to ensure at-risk bridge elements are detected.

Running the Project Locally
1 Clone the repository
git clone https://github.com/<username>/bridge_Element_examiner.git
cd bridge_Element_examiner
2 Create the Conda environment
conda env create -f environment.yml
conda activate streamenv
3 Run the Streamlit dashboard
streamlit run app/dashboard.py
4 Open the dashboard

Streamlit will launch the application locally:

http://localhost:8501
Technology Stack

This project uses:

Python
Pandas
NumPy
Scikit-learn
Matplotlib
PyDeck
Streamlit
BeautifulSoup
Selenium
Conda

Future Improvements

Potential extensions to the project include:

survival analysis for infrastructure deterioration

Markov chain modeling of condition state transitions

integration of climate and corrosion exposure data

nationwide bridge analysis across all states

predictive maintenance prioritization tools

Author

Chris Schramm

Data analytics and geospatial modeling project focused on infrastructure risk prediction.

License

MIT License
