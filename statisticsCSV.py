import os
import pandas as pd

def count_records_in_csv_folder(folder_path):
    """Counts total records, duplicated records, and distinct records across all CSV files in a folder."""
    
    all_data = []  # Store all rows from all CSV files

    # Ensure the folder exists
    if not os.path.exists(folder_path):
        print("Error: Folder does not exist.")
        return

    # Iterate over all CSV files in the folder
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            file_path = os.path.join(folder_path, file)

            # Skip empty files
            if os.path.getsize(file_path) == 0:
                print(f"Skipping empty file: {file}")
                continue

            try:
                df = pd.read_csv(file_path, header=None)  # No header assumed
                all_data.append(df)
            except pd.errors.EmptyDataError:
                print(f"Skipping unreadable file: {file}")
                continue

    # **Merge all data into a single DataFrame**
    if not all_data:
        print("No valid CSV data found.")
        return

    combined_df = pd.concat(all_data, ignore_index=True)

    # **Compute record counts**
    total_records = len(combined_df)
    duplicate_records = combined_df.duplicated(keep=False).sum()  # Count all duplicated rows
    unique_records = len(combined_df.drop_duplicates())  # Unique (distinct) rows

    # **Print results**
    print("📊 CSV Folder Analysis:")
    print(f"✅ Total records: {total_records}")
    print(f"✅ Duplicated records: {duplicate_records}")
    print(f"✅ Distinct records: {unique_records}")

if __name__ == "__main__":
    folder_path = "E:/LSCDATA/golden_corpus/suggest_1"
    count_records_in_csv_folder(folder_path)
