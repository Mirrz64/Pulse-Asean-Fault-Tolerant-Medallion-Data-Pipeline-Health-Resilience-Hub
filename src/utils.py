import pandas as pd
import numpy as np
from datetime import datetime

# 1. Data Cleaning Helpers

def clean_country_names(name: str) -> str:
    if pd.isna(name):
        return name
    name = str(name).strip()
    mapping = {
        "Indonesia": "Indonesia",
        "Lao's PDR": "Lao PDR",
        "Lao People's Democratic Republic": "Lao PDR",
        "Malaysia": "Malaysia",
        "Viet Nam": "Viet Nam"
    }
    return mapping.get(name, name)

def clean_numeric_value(val) -> float:
    if pd.isna(val):
        return np.nan
    val_str = str(val).strip()
    if val_str in ['', ',', 'nan', 'NaN']:
        return np.nan
    val_str = val_str.replace('<', '').replace('>', '').replace(' ', '').replace(',', '')
    try:
        return float(val_str)
    except ValueError:
        return np.nan

# 2. Track C: Schema Enforcement & DLQ Gate

def enforce_schema_and_validate(df: pd.DataFrame, source_name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Validates structural rules and splits records into a clean operational 
    DataFrame and a Dead Letter Queue (DLQ) Quarantine DataFrame.
    """
    df_copy = df.copy()
    
    # Audit metadata logging
    df_copy['processed_timestamp'] = datetime.now()
    df_copy['source_origin'] = source_name
    
    # Intercept records missing primary identifiers (Country or Year)
    malformed_mask = df_copy['Country'].isna() | (df_copy['Country'] == '') | df_copy['Year'].isna()
    
    # Dead Letter Queue (DLQ)
    dlq_records = df_copy[malformed_mask].copy()
    dlq_records['quarantine_reason'] = "Malformed Record: Missing essential Country/Year key"
    
    # Valid Records
    valid_records = df_copy[~malformed_mask].copy()
    
    return valid_records, dlq_records