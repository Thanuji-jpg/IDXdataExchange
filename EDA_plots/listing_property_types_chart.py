import glob
import os

import matplotlib.pyplot as plt
import pandas as pd

# Step 1: Read PropertyType from every monthly listing file in Data/
listing_files = sorted(glob.glob("Data/CRMLSListing*.csv"))
all_property_types = []

for filename in listing_files:
    try:
        df = pd.read_csv(filename, usecols=["PropertyType"])
    except UnicodeDecodeError:
        df = pd.read_csv(filename, usecols=["PropertyType"], encoding="cp1252")
    all_property_types.append(df)

# Combine into one table
listing_data = pd.concat(all_property_types, ignore_index=True)

# Step 2: Print all property types
print("Property types in the data:")
print(listing_data["PropertyType"].unique())

# Step 3: Count how many of each type
counts = listing_data["PropertyType"].value_counts()
print("\nCount of each property type:")
print(counts)

# Step 4: Get residential count and all other types combined
number_of_residential = len(listing_data[listing_data["PropertyType"] == "Residential"])
number_of_other = len(listing_data) - number_of_residential

print(f"\nResidential: {number_of_residential:,}")
print(f"Other types: {number_of_other:,}")

# Step 5: Make folder for graphs
os.makedirs("notebooks/graphs", exist_ok=True)

# Chart 1 - every property type
plt.figure(figsize=(10, 5))
counts.plot(kind="bar", color="skyblue", edgecolor="black")
plt.title("Property Types Comparison")
plt.xlabel("Property Type")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("notebooks/graphs/listing_property_types_comparison.png", dpi=300)
plt.close()

# Chart 2 - residential vs everything else
plt.figure(figsize=(8, 5))
plt.bar(
    ["Residential", "Other Property Types"],
    [number_of_residential, number_of_other],
    color=["red", "blue"],
    edgecolor="black",
)
plt.title("Residential vs Other Property Types")
plt.ylabel("Count")
plt.bar_label(plt.gca().containers[0], padding=3)
plt.tight_layout()
plt.savefig("notebooks/graphs/listing_residential_vs_other.png", dpi=300)
plt.close()

print("\nSaved charts to notebooks/graphs/")
