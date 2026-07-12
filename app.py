import pandas as pd
import streamlit as st

from components.kpi_cards import render_kpis
from components.charts import render_scatter_and_bar, render_trend_line


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PulseASEAN Dashboard",
    page_icon="🏥",
    layout="wide",
)


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Load the processed ASEAN health master dataset.
    """
    return pd.read_csv("asean_health_master.csv")


df = load_data()


# ============================================================
# VALIDATE REQUIRED COLUMNS
# ============================================================

required_columns = {
    "Country",
    "Year",
    "health_risk_score",
    "risk_level",
    "primary_risk_driver",
    "recommended_action",
}

missing_columns = required_columns.difference(df.columns)

if missing_columns:
    st.error(
        "The dataset is missing required risk-analysis columns: "
        f"{sorted(missing_columns)}"
    )

    st.info(
        "Run `python data_pipeline.py` again before launching "
        "the Streamlit dashboard."
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.title("🏥 PulseASEAN: Health Resilience Hub")

st.markdown(
    "**ASEAN Digital Health & Climate Resilience Initiative "
    "(ADHCRI)**"
)

st.caption(
    "A fault-tolerant public-health intelligence platform for "
    "regional vulnerability assessment, climate-disruption "
    "scenario planning, and explainable intervention alerts."
)


# ============================================================
# SIDEBAR CONTROLS
# ============================================================

st.sidebar.header("Control Panel")

selected_countries = st.sidebar.multiselect(
    "Select ASEAN Member States",
    options=sorted(df["Country"].dropna().unique()),
    default=sorted(df["Country"].dropna().unique()),
)

selected_year = st.sidebar.slider(
    "Select Assessment Year",
    min_value=int(df["Year"].min()),
    max_value=int(df["Year"].max()),
    value=2014,
)

st.sidebar.markdown("---")

st.sidebar.subheader("Climate Disruption Scenario")

climate_scenario = st.sidebar.selectbox(
    "Select scenario",
    options=[
        "Normal Conditions",
        "Flood Disruption",
        "Extreme Heat",
        "Vector-Borne Disease Surge",
        "Power and Connectivity Outage",
    ],
)

scenario_multipliers = {
    "Normal Conditions": 1.00,
    "Flood Disruption": 1.20,
    "Extreme Heat": 1.10,
    "Vector-Borne Disease Surge": 1.25,
    "Power and Connectivity Outage": 1.15,
}

scenario_descriptions = {
    "Normal Conditions": (
        "Baseline public-health conditions without an additional "
        "climate or infrastructure disruption."
    ),
    "Flood Disruption": (
        "Models increased service disruption, displacement, waterborne "
        "disease exposure, and reduced healthcare accessibility."
    ),
    "Extreme Heat": (
        "Models added pressure from heat stress, dehydration, and "
        "increased demand on vulnerable healthcare facilities."
    ),
    "Vector-Borne Disease Surge": (
        "Models elevated regional exposure to dengue, malaria, and "
        "other climate-sensitive vector-borne diseases."
    ),
    "Power and Connectivity Outage": (
        "Models interruption to digital health reporting, cold-chain "
        "systems, clinical operations, and emergency coordination."
    ),
}

st.sidebar.caption(
    scenario_descriptions[climate_scenario]
)


# ============================================================
# FILTER DATA
# ============================================================

filtered_df = df[
    (df["Country"].isin(selected_countries))
    & (df["Year"] == selected_year)
].copy()

if filtered_df.empty:
    st.warning(
        "No data is available for the selected countries and year."
    )
    st.stop()


# ============================================================
# APPLY CLIMATE SCENARIO
# ============================================================

scenario_multiplier = scenario_multipliers[climate_scenario]

filtered_df["scenario_risk_score"] = (
    filtered_df["health_risk_score"] * scenario_multiplier
).clip(upper=100).round(1)


def classify_scenario_risk(score: float) -> str:
    """
    Convert a numeric scenario-adjusted score into a risk category.
    """
    if score <= 25:
        return "Low"

    if score <= 50:
        return "Moderate"

    if score <= 75:
        return "High"

    return "Critical"


filtered_df["scenario_risk_level"] = filtered_df[
    "scenario_risk_score"
].apply(classify_scenario_risk)


# ============================================================
# ORIGINAL REGIONAL KPI SECTION
# ============================================================

render_kpis(filtered_df, selected_year)

st.markdown("---")


# ============================================================
# NEW REGIONAL RISK SUMMARY
# ============================================================

st.subheader("🚨 Regional Health Resilience Alerts")

highest_risk_row = filtered_df.sort_values(
    "scenario_risk_score",
    ascending=False,
).iloc[0]

average_risk_score = filtered_df[
    "scenario_risk_score"
].mean()

high_and_critical_count = filtered_df[
    "scenario_risk_level"
].isin(["High", "Critical"]).sum()

critical_count = (
    filtered_df["scenario_risk_level"] == "Critical"
).sum()

metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.metric(
        label="Highest-Risk Country",
        value=highest_risk_row["Country"],
    )

with metric_col2:
    st.metric(
        label="Highest Risk Score",
        value=f'{highest_risk_row["scenario_risk_score"]:.1f}/100',
    )

with metric_col3:
    st.metric(
        label="Regional Average Risk",
        value=f"{average_risk_score:.1f}/100",
    )

with metric_col4:
    st.metric(
        label="High/Critical Countries",
        value=int(high_and_critical_count),
        delta=f"{int(critical_count)} critical",
        delta_color="inverse",
    )


# ============================================================
# SCENARIO NOTICE
# ============================================================

if climate_scenario == "Normal Conditions":
    st.info(
        "Displaying baseline health-resilience risk using infant "
        "mortality, immunization coverage, and life expectancy."
    )
else:
    percentage_increase = int(
        (scenario_multiplier - 1) * 100
    )

    st.warning(
        f"Scenario active: **{climate_scenario}**. "
        f"Baseline vulnerability scores are increased by "
        f"**{percentage_increase}%** for prototype scenario planning."
    )


# ============================================================
# HIGHEST-RISK COUNTRY EXPLANATION
# ============================================================

st.markdown(
    f"""
### Priority Intervention

**{highest_risk_row["Country"]}** has the highest scenario-adjusted
risk score for **{selected_year}**.

- **Risk level:** {highest_risk_row["scenario_risk_level"]}
- **Risk score:** {highest_risk_row["scenario_risk_score"]}/100
- **Primary driver:** {highest_risk_row["primary_risk_driver"]}
- **Recommended action:** {highest_risk_row["recommended_action"]}
"""
)


# ============================================================
# EXPLAINABLE ALERT TABLE
# ============================================================

alert_table = filtered_df[
    [
        "Country",
        "health_risk_score",
        "scenario_risk_score",
        "scenario_risk_level",
        "primary_risk_driver",
        "recommended_action",
    ]
].copy()

alert_table = alert_table.rename(
    columns={
        "health_risk_score": "Baseline Risk",
        "scenario_risk_score": "Scenario Risk",
        "scenario_risk_level": "Risk Level",
        "primary_risk_driver": "Primary Risk Driver",
        "recommended_action": "Recommended Intervention",
    }
)

alert_table = alert_table.sort_values(
    "Scenario Risk",
    ascending=False,
)

st.dataframe(
    alert_table,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Baseline Risk": st.column_config.NumberColumn(
            format="%.1f",
        ),
        "Scenario Risk": st.column_config.ProgressColumn(
            min_value=0,
            max_value=100,
            format="%.1f",
        ),
    },
)

st.caption(
    "The Health Resilience Risk Score is a prototype policy-prioritization "
    "indicator and is not a clinical diagnostic tool."
)

st.markdown("---")


# ============================================================
# ORIGINAL VISUALIZATIONS
# ============================================================

render_scatter_and_bar(filtered_df)

render_trend_line(df, selected_countries)


# ============================================================
# METHODOLOGY
# ============================================================

st.markdown("---")

with st.expander("About the Risk Methodology"):
    st.markdown(
        """
The baseline Health Resilience Risk Score combines three comparable
regional public-health indicators:

- **Infant mortality risk — 45%**
- **Low immunization coverage risk — 30%**
- **Low life expectancy risk — 25%**

Each indicator is normalized to a scale between 0 and 1 before the
weights are applied.

Climate scenarios apply transparent prototype multipliers to the
baseline score:

- Flood disruption: **1.20×**
- Extreme heat: **1.10×**
- Vector-borne disease surge: **1.25×**
- Power and connectivity outage: **1.15×**

These multipliers demonstrate scenario-planning functionality. They
are not clinical forecasts and should be replaced with validated
climate, epidemiological, and geospatial models in a production system.
"""
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "PulseASEAN prototype | Supporting SDG 3, SDG 10, and SDG 17"
)