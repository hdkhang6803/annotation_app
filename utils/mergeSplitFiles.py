import os
import pandas as pd
import re

def merge_csv_files(folder_path, output_folder=None):
    if output_folder is None:
        output_folder = folder_path + "/merged"
        os.makedirs(output_folder, exist_ok=True)

    if not os.path.exists(folder_path):
        os.makedirs(output_folder, exist_ok=True)


    file_groups = {}
    
    # Regex patterns to categorize files
    temp_golden_pattern = re.compile(r"^(temp_golden_corpus_for_[^_]+)(?:_\d+)?\.csv$")
    declined_pattern = re.compile(r"^(declined_[^_]+)(?:_\d+)?\.csv$")
    
    # Group files based on their base name
    for filename in os.listdir(folder_path):
        match_temp = temp_golden_pattern.match(filename)
        match_declined = declined_pattern.match(filename)

        if match_temp:
            base_name = match_temp.group(1)
        elif match_declined:
            base_name = match_declined.group(1)
        else:
            continue  # Skip unrelated files

        file_path = os.path.join(folder_path, filename)
        if base_name not in file_groups:
            file_groups[base_name] = []
        file_groups[base_name].append(file_path)
    
    # Process each group
    for base_name, file_list in file_groups.items():
        merged_data = []

        for file_path in sorted(file_list):  # Sort to maintain order
            df = pd.read_csv(file_path, header=None, names=["Image Path"])
            df["Original Index"] = df.index  # Add Original Index
            merged_data.append(df)

        merged_df = pd.concat(merged_data, ignore_index=True)

        # Save the merged file
        output_filename = f"{base_name}.csv"
        output_path = os.path.join(output_folder, output_filename)
        merged_df.to_csv(output_path, index=False)
        print(f"Merged file saved: {output_path}")

# Example usage
merge_csv_files("C:/Users/ADMIN/Downloads/Lượt 1")
