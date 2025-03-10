import json

# Generate 157 dummy labels (e.g., Label_1, Label_2, ..., Label_157)
dummy_labels = [f"Label_{i}" for i in range(1, 158)]

# Save to labels.json
with open("labels.json", "w") as f:
    json.dump(dummy_labels, f, indent=4)

print("✅ 'labels.json' has been created with 157 labels.")
