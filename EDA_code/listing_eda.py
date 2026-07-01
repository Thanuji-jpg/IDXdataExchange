import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Paths for your project
LISTING_PATH = "combined_datasets/combined_listing_df.csv"
RAW_LISTING_PATTERN = "Data/CRMLSListing*.csv"
OUTPUT_CSV = "filtered_datasets/listing_residential_filtered.csv"
PLOT_DIR = "reports/numeric_plots/listing"

os.makedirs(PLOT_DIR, exist_ok=True)
os.makedirs("filtered_datasets", exist_ok=True)

# Load combined listing data (Week 1 output)
listing_data = pd.read_csv(LISTING_PATH, low_memory=False)

# Inspects the structure of the data
print("=" * 60)
print("LISTING EDA")
print("=" * 60)
print("\nColumns:", len(listing_data.columns))
print(listing_data.columns.tolist())
print("\nHead:")
print(listing_data.head())

# Property type share from raw monthly files (unfiltered)
import glob

raw_files = sorted(glob.glob(RAW_LISTING_PATTERN))
property_types = []
for filename in raw_files:
    try:
        chunk = pd.read_csv(filename, usecols=["PropertyType"])
    except (UnicodeDecodeError, ValueError):
        chunk = pd.read_csv(filename, usecols=["PropertyType"], encoding="cp1252")
    property_types.append(chunk)

unfiltered_types = pd.concat(property_types, ignore_index=True)
print("\nProperty categories (from raw monthly files):")
print(unfiltered_types["PropertyType"].unique())
print("\nResidential vs other property type share (%):")
print(unfiltered_types["PropertyType"].value_counts(normalize=True) * 100)

# Combined file is already Residential from Week 1
print("\nWorking dataset PropertyType (combined file):")
print(listing_data["PropertyType"].value_counts(normalize=True) * 100)

listing_data = listing_data[listing_data["PropertyType"] == "Residential"]

# Median and average close prices
print("\nMedian ClosePrice:", listing_data["ClosePrice"].median())
print("Average ClosePrice:", listing_data["ClosePrice"].mean())

# Percentage sold above vs below list price
listing_data["PriceRatio"] = listing_data["ClosePrice"] / listing_data["ListPrice"]
above = (listing_data["PriceRatio"] > 1).mean() * 100
below = (listing_data["PriceRatio"] < 1).mean() * 100
print("\nAbove list (%):", round(above, 2))
print("Below list (%):", round(below, 2))

# Date consistency check
listing_data["CloseDate"] = pd.to_datetime(listing_data["CloseDate"], errors="coerce")
listing_data["ListingContractDate"] = pd.to_datetime(
    listing_data["ListingContractDate"], errors="coerce"
)
invalid_dates = listing_data[
    listing_data["CloseDate"] < listing_data["ListingContractDate"]
]
print("\nInvalid date rows (CloseDate < ListingContractDate):", len(invalid_dates))

# Counties with highest median prices
print("\nTop 10 counties by median ClosePrice:")
print(
    listing_data.groupby("CountyOrParish")["ClosePrice"]
    .median()
    .sort_values(ascending=False)
    .head(10)
)

# Null count summary and 90% missing flag
null_counts = listing_data.isnull().sum().sort_values(ascending=False)
null_percent = (null_counts / len(listing_data)) * 100
missing_report = pd.DataFrame(
    {
        "NullCount": null_counts,
        "PercentNull": null_percent.round(2),
        "Flag_90pct": null_percent > 90,
    }
)
print("\nTop 15 columns by missing %:")
print(missing_report.head(15))
missing_report.to_csv("reports/listings/missing_report_eda.csv")

# Numeric fields to analyze
numeric_fields = [
    "ClosePrice",
    "ListPrice",
    "OriginalListPrice",
    "LivingArea",
    "LotSizeAcres",
    "BedroomsTotal",
    "BathroomsTotalInteger",
    "DaysOnMarket",
    "YearBuilt",
]

# Percentile summary
summary = listing_data[numeric_fields].describe(
    percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
)
print("\nNumeric summary:")
print(summary)
summary.to_csv("reports/listings/numeric_summary.csv")

# Histograms and boxplots
for col in numeric_fields:
    plt.figure(figsize=(10, 5))
    plt.hist(listing_data[col].dropna(), bins=40, color="skyblue", edgecolor="black")
    plt.title(f"Histogram of {col}")
    plt.xlabel(col)
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(f"{PLOT_DIR}/listing_hist_{col}.png", dpi=300)
    plt.close()

    plt.figure(figsize=(10, 5))
    sns.boxplot(x=listing_data[col], color="orange")
    plt.title(f"Boxplot of {col}")
    plt.tight_layout()
    plt.savefig(f"{PLOT_DIR}/listing_box_{col}.png", dpi=300)
    plt.close()

# IQR outlier counts
outlier_report = {}
for col in numeric_fields:
    q1 = listing_data[col].quantile(0.25)
    q3 = listing_data[col].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outliers = listing_data[(listing_data[col] < lower) | (listing_data[col] > upper)]
    outlier_report[col] = len(outliers)

print("\nOutlier counts (IQR method):")
print(outlier_report)

listing_data.to_csv(OUTPUT_CSV, index=False)
print(f"\nSaved filtered dataset: {OUTPUT_CSV}")
print(f"Saved plots to: {PLOT_DIR}/")
