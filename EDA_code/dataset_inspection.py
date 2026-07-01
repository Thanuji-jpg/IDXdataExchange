"""
Week 2 – Dataset inspection and missing value analysis
Run from project root:
    python3 src/eda/dataset_inspection.py
"""

import os

import pandas as pd

# Core market fields to keep even if they have some missing values
CORE_MARKET_FIELDS = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt",
    "City",
    "PostalCode",
    "PropertySubType",
    "CloseDate",
    "ListingContractDate",
    "Latitude",
    "Longitude",
    "MLSAreaMajor",
    "LotSizeSquareFeet",
    "MlsStatus",
]

# Fields mainly used for record-keeping, not market analysis
METADATA_FIELDS = [
    "ListingKey",
    "ListingKeyNumeric",
    "ListingId",
    "ListAgentEmail",
    "ListAgentFirstName",
    "ListAgentLastName",
    "ListAgentFullName",
    "CoListAgentFirstName",
    "CoListAgentLastName",
    "CoBuyerAgentFirstName",
    "BuyerAgentMlsId",
    "BuyerAgentFirstName",
    "BuyerAgentLastName",
    "ListOfficeName",
    "BuyerOfficeName",
    "CoListOfficeName",
    "BuyerOfficeName.1",
    "ListAgentAOR",
    "BuyerAgentAOR",
    "BuyerOfficeAOR",
    "OriginatingSystemName",
    "OriginatingSystemSubName",
    "BuyerAgencyCompensation",
    "BuyerAgencyCompensationType",
    "BuilderName",
]

DATASETS = {
    "sold": "combined_datasets/combined_sold_df.csv",
    "listings": "combined_datasets/combined_listing_df.csv",
}


def read_csv_safe(path):
    try:
        return pd.read_csv(path, low_memory=False)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="cp1252", low_memory=False)


def classify_columns(columns):
    market = [c for c in columns if c in CORE_MARKET_FIELDS]
    metadata = [c for c in columns if c in METADATA_FIELDS]
    other = [c for c in columns if c not in market and c not in metadata]
    return market, metadata, other


def inspect_dataset(name, path):
    print(f"\n{'=' * 60}")
    print(f"DATASET: {name.upper()}")
    print("=" * 60)

    df = read_csv_safe(path)

    # 1. Number of rows and columns
    rows, cols = df.shape
    print(f"\nRows: {rows:,}")
    print(f"Columns: {cols}")

    # 2. Column data types
    print("\n--- Column Data Types ---")
    dtype_summary = df.dtypes.astype(str).reset_index()
    dtype_summary.columns = ["column", "dtype"]
    print(dtype_summary.to_string(index=False))

    # 3. Missing counts and percentages
    missing_count = df.isna().sum()
    missing_pct = (missing_count / len(df) * 100).round(2)
    missing_df = pd.DataFrame(
        {
            "column": missing_count.index,
            "missing_count": missing_count.values,
            "missing_pct": missing_pct.values,
        }
    ).sort_values("missing_pct", ascending=False)

    print("\n--- Top 15 Columns by Missing % ---")
    print(missing_df.head(15).to_string(index=False))

    # 4. Flag columns with >90% missing
    high_missing = missing_df[missing_df["missing_pct"] > 90].copy()
    print(f"\n--- Columns with >90% Missing ({len(high_missing)}) ---")
    if len(high_missing) == 0:
        print("None")
    else:
        print(high_missing.to_string(index=False))

    # 5. Separate market vs metadata fields
    market, metadata, other = classify_columns(df.columns.tolist())
    print(f"\n--- Field Groups ---")
    print(f"Market analysis fields: {len(market)}")
    print(market)
    print(f"\nMetadata fields: {len(metadata)}")
    print(metadata)
    print(f"\nOther / property detail fields: {len(other)}")
    print(other)

    # 6. Drop vs retain recommendations
    drop_cols = high_missing["column"].tolist()
    retain_core = [c for c in CORE_MARKET_FIELDS if c in df.columns]
    print(f"\n--- Drop vs Retain ---")
    print(f"Recommend DROP (>90% missing): {len(drop_cols)} columns")
    print(drop_cols)
    print(f"\nRecommend RETAIN (core market fields): {len(retain_core)} columns")
    print(retain_core)

    # Save reports
    report_dir = f"reports/{name}"
    os.makedirs(report_dir, exist_ok=True)
    dtype_summary.to_csv(f"{report_dir}/column_dtypes.csv", index=False)
    missing_df.to_csv(f"{report_dir}/missing_values.csv", index=False)
    high_missing.to_csv(f"{report_dir}/columns_over_90pct_missing.csv", index=False)

    field_groups = pd.DataFrame(
        {
            "column": market + metadata + other,
            "field_group": (
                ["market"] * len(market)
                + ["metadata"] * len(metadata)
                + ["other"] * len(other)
            ),
        }
    )
    field_groups.to_csv(f"{report_dir}/field_groups.csv", index=False)

    print(f"\nReports saved to {report_dir}/")
    return df


def main():
    for name, path in DATASETS.items():
        if not os.path.exists(path):
            print(f"Skipping {name}: file not found at {path}")
            continue
        inspect_dataset(name, path)


if __name__ == "__main__":
    main()
