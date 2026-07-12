import pandas as pd
import numpy as np

# 1. Pipeline Transformations & Calculations

def interpolate_country_gaps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies linear interpolation across historical year series per country 
    to handle missing data points smoothly (Silver Layer transformation).
    """
    df_copy = df.copy()
    
    # Sort for time-series operations
    df_copy = df_copy.sort_values(by=['Country', 'Year'])
    
    # Identify numerical feature columns to interpolate
    numeric_cols = df_copy.select_dtypes(include=[np.number]).columns
    numeric_cols = [col for col in numeric_cols if col != 'Year']
    
    # Group by Country and interpolate linearly over time
    for col in numeric_cols:
        df_copy[col] = (
            df_copy.groupby('Country')[col]
            .transform(lambda group: group.interpolate(method='linear', limit_direction='both'))
        )
        
    return df_copy

# Alias for backward compatibility if needed
calculate_interpolated_metrics = interpolate_country_gaps


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates composite metrics including average life expectancy 
    and the Health Vulnerability Index.
    """
    df_copy = df.copy()
    
    # 1. Average Life Expectancy (Fixes the KeyError in app.py)
    le_cols = [c for c in ['life_expectancy_male', 'life_expectancy_female'] if c in df_copy.columns]
    if le_cols:
        df_copy['life_expectancy_avg'] = df_copy[le_cols].mean(axis=1).round(1)
    else:
        df_copy['life_expectancy_avg'] = np.nan

    # 2. Immunization Average
    immunization_cols = [col for col in ['immunization_dpt_pct', 'immunization_measles_pct'] if col in df_copy.columns]
    if immunization_cols:
        df_copy['immunization_avg_pct'] = df_copy[immunization_cols].mean(axis=1)
    else:
        df_copy['immunization_avg_pct'] = np.nan

    # 3. Composite Vulnerability Index
    if 'infant_mortality_rate' in df_copy.columns:
        imm_pct = df_copy['immunization_avg_pct'].fillna(80)
        df_copy['vulnerability_score'] = (
            df_copy['infant_mortality_rate'] * (1 - (imm_pct / 100))
        ).round(2)
    else:
        df_copy['vulnerability_score'] = 0.0

    return df_copy

# Alias for backward compatibility
calculate_vulnerability_index = add_derived_features


# 2. Track C: Star Schema Warehouse Generator

def generate_star_schema(master_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Transforms the processed flat master DataFrame into an optimized 
    Star Schema design (Fact Table + Dimension Tables).
    """
    # 1. Dimension Table: Time
    dim_time = pd.DataFrame({'Year': sorted(master_df['Year'].dropna().unique().astype(int))})
    dim_time['Decade'] = (dim_time['Year'] // 10) * 10

    # 2. Dimension Table: Country
    dim_countries = pd.DataFrame({'Country': sorted(master_df['Country'].dropna().unique())})
    dim_countries['Region'] = 'Southeast Asia'

    # 3. Fact Table
    exclude_cols = ['processed_timestamp', 'source_origin']
    fact_cols = [col for col in master_df.columns if col not in exclude_cols]
    fact_health_metrics = master_df[fact_cols].copy()

    return fact_health_metrics, dim_countries, dim_time