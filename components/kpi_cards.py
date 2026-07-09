import streamlit as st

def render_kpis(filtered_df, selected_year):
    st.subheader(f"📊 Regional Status Indicators ({selected_year})")
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Avg Infant Mortality", f"{filtered_df['infant_mortality_rate'].mean():.1f} / 1k")
    c2.metric("Avg Life Expectancy", f"{filtered_df['life_expectancy_avg'].mean():.1f} Yrs")
    c3.metric("Avg Immunization Rate", f"{filtered_df['immunization_avg_pct'].mean():.1f}%")
    c4.metric("Total Capital Health Exp.", f"${filtered_df['capital_health_expenditure_mUSD'].sum():,.1f} M")