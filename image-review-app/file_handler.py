import pandas as pd
import os
from config import OUTPUT_DIR, TEMP_DIR

def load_csv(file_path):
    """Loads the CSV file and returns a DataFrame."""
    if not os.path.exists(file_path):
        return None
    return pd.read_csv(file_path, header=None, names=["partial_url"])

def get_filtered_images(csv_path):
    """Returns images that are not in the golden corpus and not declined."""
    action_label = os.path.basename(csv_path).replace(".csv", "")
    golden_path = f"{TEMP_DIR}/temp_golden_corpus_for_{action_label}.csv"
    declined_csv_path = f"{TEMP_DIR}/declined_{action_label}.csv"
    
    df = load_csv(csv_path)
    if df is None or "partial_url" not in df.columns:
        return []

    # Exclude images already approved (golden corpus)
    if os.path.exists(golden_path):
        golden_df = load_csv(golden_path)
        if golden_df is not None and "partial_url" in golden_df.columns:
            df = df[~df["partial_url"].isin(golden_df["partial_url"])]

    # Exclude declined images
    declined_images = set()
    if os.path.exists(declined_csv_path):
        with open(declined_csv_path, "r") as f:
            declined_images = set(line.strip() for line in f.readlines())

    # Filter out declined images
    filtered_images = df[~df["partial_url"].isin(declined_images)]["partial_url"].tolist()

    print(f"📌 Loaded {len(filtered_images)}/{len(df)} images (Declined {len(declined_images)})")

    return filtered_images


def save_approved_image(action_label, image_url):
    """Save approved image to golden corpus"""
    golden_path = f"{TEMP_DIR}/temp_golden_corpus_for_{action_label}.csv"
    with open(golden_path, "a") as f:
        f.write(f"{image_url}\n")
