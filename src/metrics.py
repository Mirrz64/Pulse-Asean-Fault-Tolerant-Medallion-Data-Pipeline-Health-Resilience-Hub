import numpy as np
import pandas as pd


# ============================================================
# 1. PIPELINE TRANSFORMATIONS
# ============================================================

def interpolate_country_gaps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply linear interpolation across each country's historical
    time series to handle missing numerical values.

    This represents a Silver Layer transformation.
    """
    df_copy = df.copy()

    # Sort records before performing time-series interpolation.
    df_copy = df_copy.sort_values(by=["Country", "Year"])

    # Select numerical columns, excluding Year.
    numeric_cols = df_copy.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [col for col in numeric_cols if col != "Year"]

    # Interpolate missing values separately for each country.
    for col in numeric_cols:
        df_copy[col] = (
            df_copy.groupby("Country")[col]
            .transform(
                lambda group: group.interpolate(
                    method="linear",
                    limit_direction="both",
                )
            )
        )

    return df_copy


# Alias retained for backward compatibility.
calculate_interpolated_metrics = interpolate_country_gaps


# ============================================================
# 2. HEALTH-RISK CALCULATION HELPERS
# ============================================================

def min_max_normalize(series: pd.Series) -> pd.Series:
    """
    Normalize a numeric pandas Series to values between 0 and 1.

    Returns zero when the column contains no usable values or when
    all usable values are identical.
    """
    numeric_series = pd.to_numeric(series, errors="coerce")

    minimum = numeric_series.min()
    maximum = numeric_series.max()

    if pd.isna(minimum) or pd.isna(maximum) or maximum == minimum:
        return pd.Series(
            0.0,
            index=series.index,
            dtype="float64",
        )

    return (numeric_series - minimum) / (maximum - minimum)


def identify_primary_risk_driver(row: pd.Series) -> str:
    """
    Identify the factor contributing most strongly to a record's
    overall health-risk score.
    """
    risk_drivers = {
        "High infant mortality": (
            row.get("infant_mortality_risk", 0.0) * 0.45
        ),
        "Low immunization coverage": (
            row.get("immunization_risk", 0.0) * 0.30
        ),
        "Low life expectancy": (
            row.get("life_expectancy_risk", 0.0) * 0.25
        ),
    }

    cleaned_drivers = {
        driver: 0.0 if pd.isna(value) else float(value)
        for driver, value in risk_drivers.items()
    }

    return max(cleaned_drivers, key=cleaned_drivers.get)
    


def recommend_intervention(primary_driver: str) -> str:
    """
    Return an explainable public-health recommendation based on
    the primary identified risk factor.
    """
    recommendations = {
        "High infant mortality": (
            "Prioritize maternal, neonatal, and primary-care resources."
        ),
        "Low immunization coverage": (
            "Deploy mobile vaccination teams and community outreach."
        ),
        "Low life expectancy": (
            "Expand preventive care and chronic disease screening."
        ),
        "Insufficient health expenditure": (
            "Review emergency funding and regional support allocation."
        ),
    }

    return recommendations.get(
        primary_driver,
        "Conduct a detailed public-health needs assessment.",
    )


def calculate_health_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate an explainable public-health resilience risk score.

    The score combines:

    - Infant mortality risk: 45%
    - Immunization coverage risk: 30%
    - Life expectancy risk: 25%

    Higher scores represent greater public-health vulnerability.

    Capital health expenditure is retained in the dataset but excluded
    from the composite score because the available field is an absolute
    national amount rather than a per-capita or GDP-adjusted indicator.
    """
    df_copy = df.copy()

    # --------------------------------------------------------
    # Infant mortality risk
    # Higher infant mortality means higher risk.
    # --------------------------------------------------------
    if "infant_mortality_rate" in df_copy.columns:
        df_copy["infant_mortality_risk"] = min_max_normalize(
            df_copy["infant_mortality_rate"]
        )
    else:
        df_copy["infant_mortality_risk"] = 0.0

    # --------------------------------------------------------
    # Immunization risk
    # Lower immunization coverage means higher risk.
    # --------------------------------------------------------
    if "immunization_avg_pct" in df_copy.columns:
        df_copy["immunization_risk"] = (
            1 - min_max_normalize(df_copy["immunization_avg_pct"])
        )
    else:
        df_copy["immunization_risk"] = 0.0

    # --------------------------------------------------------
    # Life expectancy risk
    # Lower life expectancy means higher risk.
    # --------------------------------------------------------
    if "life_expectancy_avg" in df_copy.columns:
        df_copy["life_expectancy_risk"] = (
            1 - min_max_normalize(df_copy["life_expectancy_avg"])
        )
    else:
        df_copy["life_expectancy_risk"] = 0.0

    # Retain the column for compatibility, but do not use it
    # in the composite score.
    df_copy["health_expenditure_risk"] = np.nan

    # --------------------------------------------------------
    # Weighted composite risk score
    # --------------------------------------------------------
    df_copy["health_risk_score"] = (
        df_copy["infant_mortality_risk"] * 0.45
        + df_copy["immunization_risk"] * 0.30
        + df_copy["life_expectancy_risk"] * 0.25
    ) * 100

    df_copy["health_risk_score"] = (
        df_copy["health_risk_score"]
        .fillna(0.0)
        .clip(lower=0, upper=100)
        .round(1)
    )

    df_copy["risk_level"] = pd.cut(
        df_copy["health_risk_score"],
        bins=[-0.01, 25, 50, 75, 100],
        labels=[
            "Low",
            "Moderate",
            "High",
            "Critical",
        ],
        include_lowest=True,
    )

    df_copy["primary_risk_driver"] = df_copy.apply(
        identify_primary_risk_driver,
        axis=1,
    )

    df_copy["recommended_action"] = df_copy[
        "primary_risk_driver"
    ].apply(recommend_intervention)

    return df_copy

# ============================================================
# 3. DERIVED FEATURES
# ============================================================

def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate derived health metrics, including:

    - Average life expectancy
    - Average immunization coverage
    - Existing vulnerability score
    - Explainable health-risk score
    - Risk level
    - Primary risk driver
    - Recommended intervention
    """
    df_copy = df.copy()

    # --------------------------------------------------------
    # 1. Average life expectancy
    # --------------------------------------------------------
    life_expectancy_cols = [
        col
        for col in [
            "life_expectancy_male",
            "life_expectancy_female",
        ]
        if col in df_copy.columns
    ]

    if life_expectancy_cols:
        df_copy["life_expectancy_avg"] = (
            df_copy[life_expectancy_cols]
            .mean(axis=1)
            .round(1)
        )
    else:
        df_copy["life_expectancy_avg"] = np.nan

    # --------------------------------------------------------
    # 2. Average immunization coverage
    # --------------------------------------------------------
    immunization_cols = [
        col
        for col in [
            "immunization_dpt_pct",
            "immunization_measles_pct",
        ]
        if col in df_copy.columns
    ]

    if immunization_cols:
        df_copy["immunization_avg_pct"] = (
            df_copy[immunization_cols]
            .mean(axis=1)
            .round(1)
        )
    else:
        df_copy["immunization_avg_pct"] = np.nan

    # --------------------------------------------------------
    # 3. Existing vulnerability score
    # Retained so the original dashboard continues to work.
    # --------------------------------------------------------
    if "infant_mortality_rate" in df_copy.columns:
        immunization_pct = df_copy[
            "immunization_avg_pct"
        ].fillna(80)

        df_copy["vulnerability_score"] = (
            df_copy["infant_mortality_rate"]
            * (1 - immunization_pct / 100)
        ).round(2)
    else:
        df_copy["vulnerability_score"] = 0.0

    # --------------------------------------------------------
    # 4. New explainable health-risk features
    # --------------------------------------------------------
    df_copy = calculate_health_risk(df_copy)

    return df_copy


# Alias retained for backward compatibility.
calculate_vulnerability_index = add_derived_features


# ============================================================
# 4. STAR-SCHEMA WAREHOUSE GENERATOR
# ============================================================

def generate_star_schema(
    master_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Transform the processed master DataFrame into a star schema:

    - Fact health metrics table
    - Country dimension table
    - Time dimension table
    """
    required_columns = {"Country", "Year"}
    missing_columns = required_columns.difference(master_df.columns)

    if missing_columns:
        raise ValueError(
            "Cannot generate star schema. Missing required columns: "
            f"{sorted(missing_columns)}"
        )

    # --------------------------------------------------------
    # 1. Time dimension
    # --------------------------------------------------------
    valid_years = pd.to_numeric(
        master_df["Year"],
        errors="coerce",
    ).dropna()

    dim_time = pd.DataFrame(
        {
            "Year": sorted(
                valid_years.astype(int).unique()
            )
        }
    )

    dim_time["Decade"] = (
        dim_time["Year"] // 10
    ) * 10

    # --------------------------------------------------------
    # 2. Country dimension
    # --------------------------------------------------------
    dim_countries = pd.DataFrame(
        {
            "Country": sorted(
                master_df["Country"]
                .dropna()
                .astype(str)
                .unique()
            )
        }
    )

    dim_countries["Region"] = "Southeast Asia"

    # --------------------------------------------------------
    # 3. Fact table
    # --------------------------------------------------------
    excluded_columns = [
        "processed_timestamp",
        "source_origin",
    ]

    fact_columns = [
        col
        for col in master_df.columns
        if col not in excluded_columns
    ]

    fact_health_metrics = master_df[
        fact_columns
    ].copy()

    return (
        fact_health_metrics,
        dim_countries,
        dim_time,
    )