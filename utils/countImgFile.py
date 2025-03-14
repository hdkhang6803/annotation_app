import os

def count_image_files(directory):
    image_extensions = ('.jpg', '.webp')
    count = 0

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(image_extensions):
                count += 1

    return count

if __name__ == "__main__":
    directory = input("Enter the directory path: ")
    total_images = count_image_files(directory)
    print(f"Total image files (.jpg and .webp): {total_images}")