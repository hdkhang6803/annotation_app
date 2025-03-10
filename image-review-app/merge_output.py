import os
import pandas as pd
from config import TEMP_DIR,ORIGIN_GOLDEN_CORPUS, OUTPUT_DIR

def merge_csv_files():
    """Merges <action_label>.csv with temp_golden_corpus_for_<action_label>.csv files in a given folder."""
    csv_files = [f for f in os.listdir(TEMP_DIR) if f.endswith(".csv")]
    csv_files += [f for f in os.listdir(ORIGIN_GOLDEN_CORPUS) if f.endswith(".csv")]

    # Identify pairs: <action_label>.csv and temp_golden_corpus_for_<action_label>.csv
    action_labels = set()
    for file in csv_files:
        if file.startswith("temp_golden_corpus_for_") and file.endswith(".csv"):
            action_label = file.replace("temp_golden_corpus_for_", "").replace(".csv", "")
            if f"{action_label}.csv" in csv_files:
                action_labels.add(action_label)

    for action_label in action_labels:
        action_file = os.path.join(ORIGIN_GOLDEN_CORPUS, f"{action_label}.csv")
        golden_file = os.path.join(TEMP_DIR, f"temp_golden_corpus_for_{action_label}.csv")

        # Read both CSV files
        df_action = pd.read_csv(action_file, header=None) if os.path.exists(action_file) else pd.DataFrame()
        df_golden = pd.read_csv(golden_file, header=None) if os.path.exists(golden_file) else pd.DataFrame()

        # Merge, remove duplicates, and sort
        merged_df = pd.concat([df_action, df_golden]).drop_duplicates().reset_index(drop=True)

        # Save merged file
        output_filename = os.path.join(OUTPUT_DIR, f"{action_label}.csv")
        merged_df.to_csv(output_filename, index=False, header=False)
        print(f"Merged and updated to: {output_filename}")
