import os
import csv

# 📂 Folder containing the CSV files
INPUT_FOLDER = "E:/LSCDATA/golden_corpus/suggest_1_0_800000"  # Change this to your folder path
OUTPUT_FILE = "record_counts.csv"  # Output file to store counts

def count_records_in_csv(file_path):
    """Counts the number of records (excluding header) in a CSV file."""
    try:
        with open(file_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            return sum(1 for _ in reader)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 0

def count_records_in_folder(input_folder, output_file):
    """Counts records in all CSV files within the folder and saves results to a new CSV file."""
    results = []

    # Scan the folder for CSV files
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".csv"):
            file_path = os.path.join(input_folder, file_name)
            count = count_records_in_csv(file_path)
            results.append([file_name, count])
            print(f"📊 {file_name}: {count} records")

    # Save the results to a new CSV file
    output_path = os.path.join(output_file)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Filename", "Record Count"])  # Header
        writer.writerows(results)

    print(f"\n✅ Record counts saved to: {output_path}")

# Run the script
count_records_in_folder(INPUT_FOLDER, OUTPUT_FILE)
