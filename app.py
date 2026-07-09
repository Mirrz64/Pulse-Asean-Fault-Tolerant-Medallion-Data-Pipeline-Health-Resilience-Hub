import streamlit as st
import pandas as pd
from components.kpi_cards import render_kpis
from components.charts import render_scatter_and_bar, render_trend_line

st.set_page_config(page_title="PulseASEAN Dashboard", layout="wide")

st.title("🏥 PulseASEAN: Health Resilience Hub")
st.markdown("**ASEAN Digital Health & Climate Resilience Initiative (ADHCRI)**")

@st.cache_data
def load_data():
    return pd.read_csv('asean_health_master.csv')

df = load_data()

# Sidebar Controls
st.sidebar.header("Control Panel")
selected_countries = st.sidebar.multiselect("Select ASEAN Member States", options=df['Country'].unique(), default=df['Country'].unique())
selected_year = st.sidebar.slider("Select Assessment Year", min_value=int(df['Year'].min()), max_value=int(df['Year'].max()), value=2014)

filtered_df = df[(df['Country'].isin(selected_countries)) & (df['Year'] == selected_year)]

# Render Modular UI
render_kpis(filtered_df, selected_year)
st.markdown("---")
render_scatter_and_bar(filtered_df)
render_trend_line(df, selected_countries)