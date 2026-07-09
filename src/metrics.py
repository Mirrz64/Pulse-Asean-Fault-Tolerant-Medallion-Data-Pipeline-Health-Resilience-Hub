import pandas as pd
import numpy as np

def interpolate_country_gaps(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(['Country', 'Year']).reset_index(drop=True)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.drop('Year')
    df[numeric_cols] = df.groupby('Country')[numeric_cols].transform(
        lambda g: g.interpolate(method='linear').ffill().bfill()
    )
    return df

def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    df['immunization_avg_pct'] = (df['immunization_dpt_pct'] + df['immunization_measles_pct']) / 2
    df['life_expectancy_avg'] = (df['life_expectancy_male'] + df['life_expectancy_female']) / 2
    
    # Calculate Composite Vulnerability Index
    df['vulnerability_score'] = (
        (df['infant_mortality_rate'].fillna(0) * 0.4) +
        ((100 - df['immunization_avg_pct'].fillna(0)) * 0.3) +
        (df['crude_death_rate'].fillna(0) * 0.3)
    )
    return df