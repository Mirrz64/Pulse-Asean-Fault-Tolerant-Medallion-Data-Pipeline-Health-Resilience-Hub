import os
import pandas as pd
from src.loaders import load_raw_datasets, melt_standard
from src.metrics import interpolate_country_gaps, add_derived_features, generate_star_schema
from src.utils import clean_country_names, clean_numeric_value, enforce_schema_and_validate

def run_pipeline():
    print("🚀 Initializing Track C Resilient Data Ingestion Pipeline...")
    dfs = load_raw_datasets('dataset')
    
    # Track C: Dead Letter Queue accumulator
    dlq_accumulator = []

    # Helper to validate and catch malformed rows per dataset
    def process_and_validate(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
        valid_df, dlq_df = enforce_schema_and_validate(df, source_name=source_name)
        if not dlq_df.empty:
            dlq_accumulator.append(dlq_df)
        return valid_df

    # TIER 1: BRONZE LAYER - Shape Metrics & Validate Schemas
    std_years = [str(y) for y in range(2004, 2015)]
    exp_years = [str(y) for y in range(2000, 2016)]
    
    m_birth = process_and_validate(melt_standard(dfs['birth'], 'crude_birth_rate', std_years), 'birth')
    m_death = process_and_validate(melt_standard(dfs['death'], 'crude_death_rate', std_years), 'death')
    m_infant = process_and_validate(melt_standard(dfs['infant'], 'infant_mortality_rate', std_years), 'infant')
    m_exp = process_and_validate(melt_standard(dfs['gov_exp'], 'capital_health_expenditure_mUSD', exp_years), 'gov_exp')
    
    # DPT Immunization Parsing
    dpt_cols = [c for c in dfs['dpt'].columns if 'DPT' in c]
    m_dpt = dfs['dpt'].melt(id_vars=['Country'], value_vars=dpt_cols, var_name='Year', value_name='immunization_dpt_pct')
    m_dpt['Country'] = m_dpt['Country'].apply(clean_country_names)
    m_dpt['Year'] = m_dpt['Year'].astype(str).str.extract(r'(\d{4})')[0].astype(int)
    m_dpt['immunization_dpt_pct'] = m_dpt['immunization_dpt_pct'].apply(clean_numeric_value)
    m_dpt = process_and_validate(m_dpt, 'dpt')

    # Measles Immunization Parsing
    measles_cols = [c for c in dfs['measles'].columns if 'Measles' in c]
    m_measles = dfs['measles'].melt(id_vars=['Country'], value_vars=measles_cols, var_name='Year', value_name='immunization_measles_pct')
    m_measles['Country'] = m_measles['Country'].apply(clean_country_names)
    m_measles['Year'] = m_measles['Year'].astype(str).str.extract(r'(\d{4})')[0].astype(int)
    m_measles['immunization_measles_pct'] = m_measles['immunization_measles_pct'].apply(clean_numeric_value)
    m_measles = process_and_validate(m_measles, 'measles')

    # HIV Datasets
    hiv_years = ['2000', '2005', '2010', '2016']
    m_hiv_prev = process_and_validate(melt_standard(dfs['hiv_prev'], 'hiv_prevalence_pct', hiv_years), 'hiv_prev')
    m_hiv_deaths = process_and_validate(melt_standard(dfs['hiv_deaths'], 'hiv_deaths_annual', hiv_years), 'hiv_deaths')

    # Life Expectancy Datasets
    le_m_cols = [c for c in dfs['life_exp'].columns if 'M' in c and c != 'Reference year(s)']
    le_f_cols = [c for c in dfs['life_exp'].columns if 'F' in c]

    m_le_m = dfs['life_exp'].melt(id_vars=['Country'], value_vars=le_m_cols, var_name='Year', value_name='life_expectancy_male')
    m_le_m['Country'] = m_le_m['Country'].apply(clean_country_names)
    m_le_m['Year'] = m_le_m['Year'].astype(str).str.extract(r'(\d{4})')[0].astype(int)
    m_le_m['life_expectancy_male'] = m_le_m['life_expectancy_male'].apply(clean_numeric_value)
    m_le_m = process_and_validate(m_le_m, 'life_exp_male')

    m_le_f = dfs['life_exp'].melt(id_vars=['Country'], value_vars=le_f_cols, var_name='Year', value_name='life_expectancy_female')
    m_le_f['Country'] = m_le_f['Country'].apply(clean_country_names)
    m_le_f['Year'] = m_le_f['Year'].astype(str).str.extract(r'(\d{4})')[0].astype(int)
    m_le_f['life_expectancy_female'] = m_le_f['life_expectancy_female'].apply(clean_numeric_value)
    m_le_f = process_and_validate(m_le_f, 'life_exp_female')

    # Export Dead Letter Queue (DLQ) if malformed records were caught
    if dlq_accumulator:
        os.makedirs("dlq_logs", exist_ok=True)
        dlq_summary = pd.concat(dlq_accumulator, ignore_index=True)
        dlq_summary.to_csv("dlq_logs/dlq_quarantine_log.csv", index=False)
        print(f"🚨 Isolated {len(dlq_summary)} malformed records to 'dlq_logs/dlq_quarantine_log.csv'.")

    # TIER 2: SILVER LAYER - Multi-index Master Merge & Interpolation    
    print("🔄 Merging datasets into multi-index grid...")
    countries = sorted(m_birth['Country'].unique())
    years = list(range(2000, 2017))
    master_grid = pd.MultiIndex.from_product([countries, years], names=['Country', 'Year']).to_frame().reset_index(drop=True)

    dfs_list = [m_birth, m_death, m_infant, m_exp, m_dpt, m_measles, m_hiv_prev, m_hiv_deaths, m_le_m, m_le_f]
    master = master_grid
    
    for df in dfs_list:
        # Strip internal tracking columns for clean master merging
        merge_cols = [c for c in df.columns if c not in ['processed_timestamp', 'source_origin']]
        master = pd.merge(master, df[merge_cols], on=['Country', 'Year'], how='left')

    master = master.loc[:, ~master.columns.duplicated()]
    
    print("📊 Applying linear gap interpolation...")
    master = interpolate_country_gaps(master)

    # TIER 3: GOLD LAYER - Derived Features & Star Schema Warehouse Generation
    print("💡 Computing derived vulnerability metrics...")
    master = add_derived_features(master)

    print("🏛️ Generating Star Schema Data Mart...")
    fact_health, dim_countries, dim_time = generate_star_schema(master)

    # Save to Star Schema analytical warehouse directory
    warehouse_dir = "warehouse"
    os.makedirs(warehouse_dir, exist_ok=True)
    
    fact_health.to_csv(f"{warehouse_dir}/fact_health_metrics.csv", index=False)
    dim_countries.to_csv(f"{warehouse_dir}/dim_countries.csv", index=False)
    dim_time.to_csv(f"{warehouse_dir}/dim_time.csv", index=False)

    # Primary Master Export
    master.to_csv('asean_health_master.csv', index=False)
    
    print("\n✅ TRACK C PIPELINE COMPLETE!")
    print(f"   • Primary Master: asean_health_master.csv ({len(master)} rows)")
    print(f"   • Fact Table:     {warehouse_dir}/fact_health_metrics.csv")
    print(f"   • Dim Country:    {warehouse_dir}/dim_countries.csv")
    print(f"   • Dim Time:       {warehouse_dir}/dim_time.csv")

if __name__ == '__main__':
    run_pipeline()