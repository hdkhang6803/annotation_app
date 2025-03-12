import os
import pandas as pd

def count_records_in_csv_folder(folder_path, output_file="duplicated_records.csv"):
    """Counts total records, duplicated records, and distinct records across all CSV files in a folder.
    Saves duplicated records along with the filenames they appear in.
    """
    
    all_data = []  # Store all rows from all CSV files
    record_sources = {}  # Store file sources for each record

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

                # Store records along with the file they came from
                for _, row in df.iterrows():
                    row_tuple = tuple(row)  # Convert row to a hashable format
                    if row_tuple in record_sources:
                        record_sources[row_tuple].append(file)  # Append file to existing entry
                    else:
                        record_sources[row_tuple] = [file]

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
    duplicate_records = combined_df[combined_df.duplicated(keep=False)]  # Keep all duplicate occurrences
    unique_records = len(combined_df.drop_duplicates())  # Unique (distinct) rows

    # **Prepare duplicate records with file sources**
    duplicate_data = []
    for record in duplicate_records.itertuples(index=False, name=None):
        record_tuple = tuple(record)  # Convert row to tuple for lookup
        files_containing = record_sources.get(record_tuple, [])
        
        if len(files_containing) > 1:  # Only store if it appears in more than one file
            duplicate_data.append(list(record) + [", ".join(set(files_containing))])  # Deduplicate file list

    # **Save duplicate records to file**
    if duplicate_data:
        duplicate_df = pd.DataFrame(duplicate_data)
        column_names = [f"Column_{i}" for i in range(len(duplicate_df.columns) - 1)] + ["Files"]
        duplicate_df.columns = column_names
        duplicate_df.to_csv(output_file, index=False)
        print(f"📂 Duplicated records saved to: {output_file}")
    else:
        print("✅ No duplicated records found across multiple files.")

    # **Print summary results**
    print("📊 CSV Folder Analysis:")
    print(f"✅ Total records: {total_records}")
    print(f"✅ Duplicated records: {len(duplicate_records)}")
    print(f"✅ Distinct records: {unique_records}")

   
if __name__ == "__main__":
    folder_path = "E:/LSCDATA/golden_corpus/suggest_1_0_800000"
    count_records_in_csv_folder(folder_path)
