import json

# Load the JSON file
with open("oldToNewLabelMap.json", "r") as file:
    labels_data = json.load(file)

# Extract unique labels and assign new IDs
unique_labels = sorted(set(labels_data.values()))  # Sort for consistency
label_to_id = {f"n{str(i).zfill(3)}": label for i, label in enumerate(unique_labels)}

# Save the mapping to a new file
with open("newLabelMap.json", "w") as outfile:
    json.dump(label_to_id, outfile, indent=4)

# Print the result
print(json.dumps(label_to_id, indent=4))
