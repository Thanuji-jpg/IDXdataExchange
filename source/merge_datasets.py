"""
Runs the sold and listing aggregation scripts to build both combined datasets.
Run from the project root folder:
    python3 merge_datasets.py
"""

import subprocess
import sys

scripts = [
    "src/sold_data_script/sold_data_aggregation.py",
    "src/listing_data_script/listing_data_aggregation.py",
]

for script in scripts:
    print(f"\n{'=' * 50}")
    print(f"Running {script}")
    print("=" * 50)
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"Error: {script} failed.")
        sys.exit(1)

print("\nDone. Both combined CSVs are in combined_datasets/")
