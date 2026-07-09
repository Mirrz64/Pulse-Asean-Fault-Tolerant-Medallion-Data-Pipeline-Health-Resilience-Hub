import os
import pandas as pd
from .utils import clean_country_names, clean_numeric_value

def load_raw_datasets(data_dir: str = 'dataset') -> dict:
    files = {
        'birth': 'crude_birth_ratio.csv',
        'death': 'crude_death_ratio.csv',
        'infant': 'Infant_mortality_rate.csv',
        'gov_exp': 'goverment_expence_in_health.csv',
        'dpt': 'immunization_DPT.csv',
        'measles': 'immunization_measless.csv',
        'hiv_prev': 'HIV_Prevalence.csv',
        'hiv_deaths': 'death_by_HIV_ AIDS.csv',
        'life_exp': 'life_expentancy_rate.csv'
    }
    dfs = {}
    for key, filename in files.items():
        path = os.path.join(data_dir, filename)
        df = pd.read_csv(path)
        if 'Countries and areas' in df.columns:
            df.rename(columns={'Countries and areas': 'Country'}, inplace=True)
        elif 'Countries' in df.columns:
            df.rename(columns={'Countries': 'Country'}, inplace=True)
        dfs[key] = df
    return dfs

def melt_standard(df: pd.DataFrame, metric_name: str, year_cols: list) -> pd.DataFrame:
    df['Country'] = df['Country'].apply(clean_country_names)
    df = df.dropna(subset=['Country'])
    melted = df.melt(id_vars=['Country'], value_vars=year_cols, var_name='Year', value_name=metric_name)
    melted['Year'] = melted['Year'].astype(str).str.extract(r'(\d{4})')[0].astype(int)
    melted[metric_name] = melted[metric_name].apply(clean_numeric_value)
    return melted