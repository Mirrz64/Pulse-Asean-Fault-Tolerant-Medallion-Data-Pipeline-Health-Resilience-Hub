import pandas as pd
import numpy as np

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