# 🏥 PulseASEAN: Health Resilience Hub

**Pod Vega — 10Alytics Global Hackathon 2026**

PulseASEAN is a fault-tolerant public-health intelligence platform designed to help ASEAN policymakers identify vulnerable countries, understand major health-risk drivers, simulate climate-related disruptions, and prioritize interventions.

The solution combines a resilient data pipeline, explainable health-risk scoring, climate scenario analysis, and an interactive Streamlit dashboard.

---

## The Problem

ASEAN’s health systems face several connected challenges:

- Fragmented health data across countries and institutions
- Unequal healthcare access and funding
- Climate-driven disease and infrastructure disruption
- Limited visibility into vulnerable populations
- Unreliable power and internet connectivity in underserved areas
- Difficulty coordinating regional public-health responses

These challenges can delay disease detection, weaken emergency response, and make it harder to allocate limited healthcare resources effectively.

---

## Our Solution

PulseASEAN transforms historical ASEAN health indicators into actionable regional intelligence.

The platform:

- Validates and processes health data through a medallion-style pipeline
- Interpolates missing country-level time-series values
- Quarantines invalid records through a Dead Letter Queue
- Generates an analytical star schema
- Calculates an explainable Health Resilience Risk Score
- Identifies each country’s primary risk driver
- Recommends targeted public-health interventions
- Simulates climate and infrastructure disruption scenarios
- Visualizes regional health patterns and historical trends

---

## Key Features

### Fault-Tolerant Data Pipeline

The pipeline validates incoming records and prevents malformed data from stopping the workflow. Invalid records are redirected to a Dead Letter Queue for further review.

### Explainable Health Resilience Risk Score

The score combines:

| Indicator | Weight |
|---|---:|
| Infant mortality risk | 45% |
| Low immunization coverage risk | 30% |
| Low life expectancy risk | 25% |

Each indicator is normalized before weighting.

Risk levels are classified as Low, Moderate, High, or Critical. The model also provides a primary risk driver, recommended intervention, and country-level ranking.

### Climate Disruption Scenarios

Users can simulate:

- Normal Conditions
- Flood Disruption
- Extreme Heat
- Vector-Borne Disease Surge
- Power and Connectivity Outage

These scenarios apply transparent prototype multipliers to the baseline risk score for planning and demonstration purposes.

### Interactive Dashboard

The Streamlit dashboard includes:

- Regional health indicators
- Country and year filters
- Climate scenario controls
- Highest-risk country
- Regional average risk
- Priority intervention recommendations
- Country-level alert table
- Immunization versus infant mortality analysis
- Historical health trajectories
- Risk methodology and limitations

---

## Dashboard Preview

### Regional Health Resilience Overview

![Regional Health Resilience Overview](screenshots/dashboard-overview.png)

### Country-Level Alerts and Interventions

![Country-Level Alerts](screenshots/risk-alerts.png)

### Regional Vulnerability Analysis

![Regional Vulnerability Analysis](screenshots/vulnerability-analysis.png)

### Historical Health Trajectory

![Historical Health Trajectory](screenshots/historical-trajectory.png)

---

## Architecture

```text
Raw ASEAN Health Data
        │
        ▼
Bronze Layer
Data ingestion and schema validation
        │
        ├── Invalid records → Dead Letter Queue
        │
        ▼
Silver Layer
Cleaning and country-level interpolation
        │
        ▼
Gold Layer
Derived indicators and health-risk scoring
        │
        ▼
Star Schema Warehouse
Fact and dimension tables
        │
        ▼
Streamlit Dashboard
Risk alerts, scenarios, trends, and interventions
```

---

## Technologies Used

- Python
- Pandas
- NumPy
- Streamlit
- Plotly
- Git and GitHub
- Medallion data architecture
- Star-schema data modelling

---

## Running the Project

Clone the repository:

```bash
git clone https://github.com/Mirrz64/Pulse-Asean-Fault-Tolerant-Medallion-Data-Pipeline-Health-Resilience-Hub.git
```

Move into the project folder:

```bash
cd Pulse-Asean-Fault-Tolerant-Medallion-Data-Pipeline-Health-Resilience-Hub
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the data pipeline:

```bash
python data_pipeline.py
```

Start the dashboard:

```bash
streamlit run app.py
```

The application will normally open at:

```text
http://localhost:8501
```

---

## SDG Alignment

### SDG 3 — Good Health and Well-Being

- Improved health-risk monitoring
- Better intervention prioritization
- Support for immunization and maternal-health planning

### SDG 10 — Reduced Inequalities

- Identification of countries and communities with higher health vulnerability
- More equitable resource-allocation decisions

### SDG 17 — Partnerships for the Goals

- Regional health-data collaboration
- Cross-border public-health coordination
- Shared analytical standards

---

## Limitations

- The project uses historical health indicators rather than real-time clinical data.
- Climate scenarios use prototype multipliers and are not clinical forecasts.
- The Health Resilience Risk Score is a policy-prioritization tool, not a medical diagnostic model.
- The current prototype does not yet include live climate, geospatial, hospital, or outbreak-surveillance feeds.

---

## Future Improvements

- Integrate live climate and weather data
- Add dengue, malaria, TB, and outbreak-surveillance feeds
- Introduce geospatial hotspot detection
- Add machine-learning outbreak forecasting
- Support FHIR-based health-data interoperability
- Implement role-based access control and audit logging
- Add encrypted offline synchronization for rural health facilities

---

## Team

### Pod Vega

- **Miracle Osabuogbe**
- **Mohammed Usman**

Developed for the **10Alytics Global Hackathon 2026** under the theme:

**Sustainable Development Through Artificial Intelligence and Innovation**

---

## Disclaimer

PulseASEAN is a hackathon prototype intended for public-health analytics and policy-planning demonstrations. It is not a clinical diagnostic system.
