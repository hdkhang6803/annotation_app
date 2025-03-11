import json

# Load the JSON file
with open("oldToNewLabelMap.json", "r", encoding="utf-8") as file:
    label_mapping = json.load(file)

# Extract unique labels
unique_labels = set(label_mapping.values())

# Write the distinct labels to a JSON file
with open("unique_labels.json", "w", encoding="utf-8") as outfile:
    json.dump(list(unique_labels), outfile, ensure_ascii=False, indent=4)
