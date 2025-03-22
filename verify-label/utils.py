import os
import re

import re


def get_path_for_vector_db(image_path):
    # Normalize path to use forward slashes
    normalized_path = image_path.replace("\\", "/")  # Convert Windows backslashes to forward slashes
    # Regex to extract the expected "YYYYMM/DD/filename.jpg" format
    match = re.search(r"(\d{6}/\d{2}/[^/]+)$", normalized_path)
    if match:
        return match.group(1)  # Extracted "yearmonth/day/filename.jpg"
    else:
        raise ValueError(f"Could not determine relative path for image: {image_path}")
    

def get_base_path(image_path):
    """Retrieves the base path by removing 'YYYYMM/DD/filename.jpg' from the absolute image path."""
    normalized_path = image_path.replace("\\", "/")  # Normalize slashes

    match = re.search(r"(\d{6}/\d{2}/[^/]+)$", normalized_path)
    if match:
        return normalized_path[: -len(match.group(1))].rstrip("/")  # Remove matched part and trailing slash
    else:
        raise ValueError(f"Could not determine base path for image: {image_path}")