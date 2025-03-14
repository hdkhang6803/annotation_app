import os
import pandas as pd
from collections import defaultdict

def merge_csv_by_action_label(root_folder, output_folder):
    """Merges all CSV files with the same <action_label>.csv name across subfolders into a single CSV file."""
    
    # Dictionary to hold all data categorized by action_label
    csv_data = defaultdict(list)

    # Walk through all subdirectories
    for subdir, _, files in os.walk(root_folder):
        for file in files:
            if file.endswith(".csv"):  # Process only CSV files
                action_label = file  # File name acts as key
                file_path = os.path.join(subdir, file)

                # **Skip empty files**
                if os.path.getsize(file_path) == 0:
                    print(f"Skipping empty file: {file_path}")
                    continue

                try:
                    # Read CSV (no header, single-column format)
                    df = pd.read_csv(file_path, header=None)

                    # **Skip if file has no valid data (failsafe)**
                    if df.empty:
                        print(f"Skipping empty data in: {file_path}")
                        continue

                    # Store data for this action_label
                    csv_data[action_label].append(df)

                except pd.errors.EmptyDataError:
                    print(f"Skipping unreadable file: {file_path}")
                    continue

    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Merge all files with the same <action_label>.csv name
    for action_label, dataframes in csv_data.items():
        merged_df = pd.concat(dataframes, ignore_index=True).drop_duplicates()
        output_file = os.path.join(output_folder, action_label)

        # Save merged CSV (no header)
        merged_df.to_csv(output_file, index=False, header=False)
        print(f"Merged {len(dataframes)} files into: {output_file}")

if __name__ == "__main__":
    root_folder = "E:/LSCDATA/Ground truth LSC"
    output_folder = "E:/LSCDATA/Ground truth LSC"

    if os.path.exists(root_folder):
        merge_csv_by_action_label(root_folder, output_folder)
        print("All CSV files with the same name have been merged successfully!")
    else:
        print("Invalid root folder path.")
