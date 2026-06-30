import glob
import os

import pandas as pd

# Finds all .csv files that start with "CRMLSListing"
listing_file_pattern = "Data/CRMLSListing*.csv"
all_listing_files = sorted(glob.glob(listing_file_pattern))

# Initialize an empty list to store the individual data frames
listing_df_list = []

# Initialize an empty list to track row counts before concatenation
total_entries = []

# Use a for loop to read each file and add it to the list
for filename in all_listing_files:
    try:
        listing_df = pd.read_csv(filename)
        total_entries.append(len(listing_df))
        listing_df_list.append(listing_df)
    except UnicodeDecodeError:
        listing_df = pd.read_csv(filename, encoding="cp1252")
        total_entries.append(len(listing_df))
        listing_df_list.append(listing_df)

# Concatenates all data frames to create final listing data frame
combined_listing_df = pd.concat(listing_df_list, ignore_index=True)

# Prints row counts
print("LISTINGS - files used:", len(all_listing_files))
print("LISTINGS - avg rows per file:", round(sum(total_entries) / len(total_entries), 0))
print("LISTINGS - total rows BEFORE concatenation:", sum(total_entries))
print("LISTINGS - total rows AFTER concatenation:", len(combined_listing_df))

# Filters the Property Type to 'Residential' only
combined_listing_df = combined_listing_df[
    combined_listing_df["PropertyType"] == "Residential"
]

print("LISTINGS - total rows AFTER Residential filter:", len(combined_listing_df))

# Save the combined data frame to a new .csv file
os.makedirs("combined_datasets", exist_ok=True)
combined_listing_df.to_csv("combined_datasets/combined_listing_df.csv", index=False)
print("LISTINGS - saved: combined_datasets/combined_listing_df.csv")
