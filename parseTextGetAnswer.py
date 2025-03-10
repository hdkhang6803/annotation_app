import re
import csv

# Define the regex pattern for the format YYYYMMDD_HHMMSS_NNN
pattern = re.compile(r'\b\d{8}_\d{6}_\d{3}\b')

# Read the input file and extract matching strings
input_file = "C:/Users/ADMIN/Downloads/lsc22-topics-qrels-shared.txt"  # Change this to your actual file name
output_file = "output.csv"

matches = []
with open(input_file, "r", encoding="utf-8") as file:
    for line in file:
        matches.extend(pattern.findall(line))

# Write matches to a CSV file
with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Matched Strings"])  # Header
    for match in matches:
        writer.writerow([match])

print(f"Extracted {len(matches)} matches and saved to {output_file}.")
