import os
from config import IMAGE_DIR

def get_full_image_path(partial_url):
    """Converts partial URL to full image path."""
    return os.path.join(IMAGE_DIR, partial_url) + ".jpg"
