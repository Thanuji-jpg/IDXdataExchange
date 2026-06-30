import glob
import os

import pandas as pd

# Finds all .csv files that start with "CRMLSSold"
sold_file_pattern = "Data/CRMLSSold*.csv"
all_sold_files = sorted(glob.glob(sold_file_pattern))

# Keep one sold file per month (skip _filled if regular file exists for that month)
sold_files_to_use = []
for filename in all_sold_files:
    month = os.path.basename(filename)[9:15]  # e.g. "202403" from CRMLSSold202403.csv
    if "_filled" in filename:
        regular_file = f"Data/CRMLSSold{month}.csv"
        if regular_file in all_sold_files:
            continue
    sold_files_to_use.append(filename)

# Initialize an empty list to store the individual data frames
sold_df_list = []

# Initialize an empty list to track row counts before concatenation
total_entries = []

# Use a for loop to read each file and add it to the list
for filename in sold_files_to_use:
    try:
        sold_df = pd.read_csv(filename)
        total_entries.append(len(sold_df))
        sold_df_list.append(sold_df)
    except UnicodeDecodeError:
        sold_df = pd.read_csv(filename, encoding="cp1252")
        total_entries.append(len(sold_df))
        sold_df_list.append(sold_df)

# Concatenates all data frames to create final sold data frame
combined_sold_df = pd.concat(sold_df_list, ignore_index=True)

# Removes extra columns if they exist
combined_sold_df = combined_sold_df.drop(columns=["latfilled", "lonfilled"], errors="ignore")

# Prints row counts
print("SOLD - files used:", len(sold_files_to_use))
print("SOLD - avg rows per file:", round(sum(total_entries) / len(total_entries), 0))
print("SOLD - total rows BEFORE concatenation:", sum(total_entries))
print("SOLD - total rows AFTER concatenation:", len(combined_sold_df))

# Filters the Property Type to 'Residential' only
combined_sold_df = combined_sold_df[combined_sold_df["PropertyType"] == "Residential"]

print("SOLD - total rows AFTER Residential filter:", len(combined_sold_df))

# Save the combined data frame to a new .csv file
os.makedirs("combined_datasets", exist_ok=True)
combined_sold_df.to_csv("combined_datasets/combined_sold_df.csv", index=False)
print("SOLD - saved: combined_datasets/combined_sold_df.csv")
