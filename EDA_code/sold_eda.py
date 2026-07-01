import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

SOLD_PATH = "combined_datasets/combined_sold_df.csv"
RAW_SOLD_PATTERN = "Data/CRMLSSold*.csv"
OUTPUT_CSV = "filtered_datasets/sold_residential_filtered.csv"
PLOT_DIR = "reports/numeric_plots/sold"

os.makedirs(PLOT_DIR, exist_ok=True)
os.makedirs("filtered_datasets", exist_ok=True)
os.makedirs("reports/sold", exist_ok=True)

sold_data = pd.read_csv(SOLD_PATH, low_memory=False)

print("=" * 60)
print("SOLD EDA")
print("=" * 60)
print("\nColumns:", len(sold_data.columns))
print("\nHead:")
print(sold_data.head())

# Property type share from raw monthly files
import glob
import os

raw_files = sorted(glob.glob(RAW_SOLD_PATTERN))
property_types = []
for filename in raw_files:
    if "_filled" in filename:
        month = os.path.basename(filename)[9:15]
        regular = f"Data/CRMLSSold{month}.csv"
        if regular in raw_files:
            continue
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

sold_data = sold_data[sold_data["PropertyType"] == "Residential"]

print("\nMedian ClosePrice:", sold_data["ClosePrice"].median())
print("Average ClosePrice:", sold_data["ClosePrice"].mean())

sold_data["PriceRatio"] = sold_data["ClosePrice"] / sold_data["ListPrice"]
above = (sold_data["PriceRatio"] > 1).mean() * 100
below = (sold_data["PriceRatio"] < 1).mean() * 100
print("\nAbove list (%):", round(above, 2))
print("Below list (%):", round(below, 2))

sold_data["CloseDate"] = pd.to_datetime(sold_data["CloseDate"], errors="coerce")
sold_data["ListingContractDate"] = pd.to_datetime(
    sold_data["ListingContractDate"], errors="coerce"
)
invalid_dates = sold_data[sold_data["CloseDate"] < sold_data["ListingContractDate"]]
print("\nInvalid date rows:", len(invalid_dates))

print("\nTop 10 counties by median ClosePrice:")
print(
    sold_data.groupby("CountyOrParish")["ClosePrice"]
    .median()
    .sort_values(ascending=False)
    .head(10)
)

null_counts = sold_data.isnull().sum().sort_values(ascending=False)
null_percent = (null_counts / len(sold_data)) * 100
missing_report = pd.DataFrame(
    {
        "NullCount": null_counts,
        "PercentNull": null_percent.round(2),
        "Flag_90pct": null_percent > 90,
    }
)
print("\nTop 15 columns by missing %:")
print(missing_report.head(15))
missing_report.to_csv("reports/sold/missing_report_eda.csv")

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

summary = sold_data[numeric_fields].describe(
    percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
)
print("\nNumeric summary:")
print(summary)
summary.to_csv("reports/sold/numeric_summary.csv")

for col in numeric_fields:
    plt.figure(figsize=(10, 5))
    plt.hist(sold_data[col].dropna(), bins=40, color="skyblue", edgecolor="black")
    plt.title(f"Histogram of {col}")
    plt.xlabel(col)
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(f"{PLOT_DIR}/sold_hist_{col}.png", dpi=300)
    plt.close()

    plt.figure(figsize=(10, 5))
    sns.boxplot(x=sold_data[col], color="orange")
    plt.title(f"Boxplot of {col}")
    plt.tight_layout()
    plt.savefig(f"{PLOT_DIR}/sold_box_{col}.png", dpi=300)
    plt.close()

outlier_report = {}
for col in numeric_fields:
    q1 = sold_data[col].quantile(0.25)
    q3 = sold_data[col].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outliers = sold_data[(sold_data[col] < lower) | (sold_data[col] > upper)]
    outlier_report[col] = len(outliers)

print("\nOutlier counts (IQR method):")
print(outlier_report)

sold_data.to_csv(OUTPUT_CSV, index=False)
print(f"\nSaved filtered dataset: {OUTPUT_CSV}")
print(f"Saved plots to: {PLOT_DIR}/")
