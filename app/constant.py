from dotenv import load_dotenv
import os

# Global variables
image_list = []
current_index = 0
image_dir = ""
output_dir = ""
output_csv = "annotations.csv"
load_dotenv()
label_file = os.getenv("LABEL_FILE")
label_data = []
csv_columns = ["image_filename", "main label", "concurrent label"]
annotated_images = set()  # Track already labeled images
total_images = 0  # Total images in directory
base_path = ""
have_base_path = False
button_per_row=10