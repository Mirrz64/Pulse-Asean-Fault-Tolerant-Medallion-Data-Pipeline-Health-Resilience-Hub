import streamlit as st
import plotly.express as px

def render_scatter_and_bar(filtered_df):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💡 Immunization vs. Infant Mortality")
        fig_scatter = px.scatter(
            filtered_df,
            x='immunization_avg_pct',
            y='infant_mortality_rate',
            size='capital_health_expenditure_mUSD',
            color='Country',
            hover_name='Country',
            labels={'immunization_avg_pct': 'Immunization Rate (%)', 'infant_mortality_rate': 'Infant Mortality Rate (per 1k)'},
            title="Protection Coverage vs Mortality Risk"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col2:
        st.subheader("⚠️ Health Vulnerability Index")
        fig_bar = px.bar(
            filtered_df.sort_values('vulnerability_score', ascending=False),
            x='Country',
            y='vulnerability_score',
            color='vulnerability_score',
            color_continuous_scale='Reds',
            title="Regional Vulnerability Ranking"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

def render_trend_line(df, selected_countries):
    st.subheader("📈 Historical Trajectory (2000–2016)")
    metric_choice = st.selectbox(
        "Select Metric to Analyze Over Time",
        ['capital_health_expenditure_mUSD', 'infant_mortality_rate', 'immunization_avg_pct', 'life_expectancy_avg']
    )

    trend_df = df[df['Country'].isin(selected_countries)]
    fig_trend = px.line(
        trend_df,
        x='Year',
        y=metric_choice,
        color='Country',
        title=f"Historical Progression: {metric_choice.replace('_', ' ').title()}"
    )
    st.plotly_chart(fig_trend, use_container_width=True)