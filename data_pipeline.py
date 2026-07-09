import pandas as pd
from src.loaders import load_raw_datasets, melt_standard
from src.metrics import interpolate_country_gaps, add_derived_features
from src.utils import clean_country_names, clean_numeric_value

def run_pipeline():
    dfs = load_raw_datasets('dataset')
    
    # Reshape Metrics
    std_years = [str(y) for y in range(2004, 2015)]
    exp_years = [str(y) for y in range(2000, 2016)]
    
    m_birth = melt_standard(dfs['birth'], 'crude_birth_rate', std_years)
    m_death = melt_standard(dfs['death'], 'crude_death_rate', std_years)
    m_infant = melt_standard(dfs['infant'], 'infant_mortality_rate', std_years)
    m_exp = melt_standard(dfs['gov_exp'], 'capital_health_expenditure_mUSD', exp_years)
    
    dpt_cols = [c for c in dfs['dpt'].columns if 'DPT' in c]
    m_dpt = dfs['dpt'].melt(id_vars=['Country'], value_vars=dpt_cols, var_name='Year', value_name='immunization_dpt_pct')
    m_dpt['Country'] = m_dpt['Country'].apply(clean_country_names)
    m_dpt['Year'] = m_dpt['Year'].astype(str).str.extract(r'(\d{4})')[0].astype(int)
    m_dpt['immunization_dpt_pct'] = m_dpt['immunization_dpt_pct'].apply(clean_numeric_value)

    measles_cols = [c for c in dfs['measles'].columns if 'Measles' in c]
    m_measles = dfs['measles'].melt(id_vars=['Country'], value_vars=measles_cols, var_name='Year', value_name='immunization_measles_pct')
    m_measles['Country'] = m_measles['Country'].apply(clean_country_names)
    m_measles['Year'] = m_measles['Year'].astype(str).str.extract(r'(\d{4})')[0].astype(int)
    m_measles['immunization_measles_pct'] = m_measles['immunization_measles_pct'].apply(clean_numeric_value)

    hiv_years = ['2000', '2005', '2010', '2016']
    m_hiv_prev = melt_standard(dfs['hiv_prev'], 'hiv_prevalence_pct', hiv_years)
    m_hiv_deaths = melt_standard(dfs['hiv_deaths'], 'hiv_deaths_annual', hiv_years)

    le_m_cols = [c for c in dfs['life_exp'].columns if 'M' in c and c != 'Reference year(s)']
    le_f_cols = [c for c in dfs['life_exp'].columns if 'F' in c]

    m_le_m = dfs['life_exp'].melt(id_vars=['Country'], value_vars=le_m_cols, var_name='Year', value_name='life_expectancy_male')
    m_le_m['Country'] = m_le_m['Country'].apply(clean_country_names)
    m_le_m['Year'] = m_le_m['Year'].astype(str).str.extract(r'(\d{4})')[0].astype(int)
    m_le_m['life_expectancy_male'] = m_le_m['life_expectancy_male'].apply(clean_numeric_value)

    m_le_f = dfs['life_exp'].melt(id_vars=['Country'], value_vars=le_f_cols, var_name='Year', value_name='life_expectancy_female')
    m_le_f['Country'] = m_le_f['Country'].apply(clean_country_names)
    m_le_f['Year'] = m_le_f['Year'].astype(str).str.extract(r'(\d{4})')[0].astype(int)
    m_le_f['life_expectancy_female'] = m_le_f['life_expectancy_female'].apply(clean_numeric_value)

    # Multi-index Master Merge
    countries = sorted(m_birth['Country'].unique())
    years = list(range(2000, 2017))
    master_grid = pd.MultiIndex.from_product([countries, years], names=['Country', 'Year']).to_frame().reset_index(drop=True)

    dfs_list = [m_birth, m_death, m_infant, m_exp, m_dpt, m_measles, m_hiv_prev, m_hiv_deaths, m_le_m, m_le_f]
    master = master_grid
    for df in dfs_list:
        master = pd.merge(master, df, on=['Country', 'Year'], how='left')

    master = master.loc[:, ~master.columns.duplicated()]
    master = interpolate_country_gaps(master)
    master = add_derived_features(master)

    master.to_csv('asean_health_master.csv', index=False)
    print("✅ Success: Pipeline executed via modular package!")

if __name__ == '__main__':
    run_pipeline()