import os
import concurrent.futures
from PIL import Image
from tqdm import tqdm

# 🛠 Configuration
INPUT_FOLDER = "E:/LSCDATA/keyframes_1"  # Change this to your actual folder
OUTPUT_FOLDER = "E:/LSCDATA/compressed_keyframes_1"  # Change this to where converted images will be saved
QUALITY = 30  # Adjust quality (higher = better quality, but larger file)
NUM_THREADS = 8  # Adjust based on CPU capability

def process_image(image_path, output_path):
    """Reduces image storage size while keeping dimensions and converts to WebP."""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB (for PNGs with transparency)
            img = img.convert("RGB")

            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Save as WebP with optimized settings
            img.save(output_path, "WEBP", quality=QUALITY, optimize=True)

            return f"✅ Processed: {image_path} → {output_path}"

    except Exception as e:
        return f"❌ Error processing {image_path}: {e}"

def get_all_images(folder):
    """Recursively collects all image paths from the folder structure."""
    image_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                image_files.append(os.path.join(root, file))
    return image_files

def convert_images():
    """Runs the conversion process in parallel using multithreading."""
    image_paths = get_all_images(INPUT_FOLDER)
    
    # Prepare input-output path mappings
    tasks = []
    for img_path in image_paths:
        relative_path = os.path.relpath(img_path, INPUT_FOLDER)  # Preserve folder structure
        webp_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(relative_path)[0] + ".webp")
        tasks.append((img_path, webp_path))

    print(f"🔄 Processing {len(tasks)} images...")

    # Run in parallel using ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        results = list(tqdm(executor.map(lambda t: process_image(*t), tasks), total=len(tasks)))

    # Print summary
    for res in results:
        print(res)

if __name__ == "__main__":
    convert_images()
