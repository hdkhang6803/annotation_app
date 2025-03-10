import os
from dotenv import load_dotenv

load_dotenv()

IMAGE_DIR = os.getenv("IMAGE_DIR") 
OUTPUT_DIR = os.getenv("OUTPUT_DIR") 
TEMP_DIR = os.getenv("TEMP_DIR")  
ORIGIN_GOLDEN_CORPUS = os.getenv("ORIGIN_GOLDEN_CORPUS")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
