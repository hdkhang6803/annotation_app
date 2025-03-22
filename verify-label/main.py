import os
import json
import shutil
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, Canvas, Frame, Scrollbar, Entry, Label
from PIL import Image, ImageTk
from rest_client import RestClient
from utils import get_path_for_vector_db, get_base_path
from constant import IMAGE_DIR, button_per_col, label_file


api_client = RestClient("http://server.selab.edu.vn:20715")

THUMBNAIL_SIZE = (200, 150)  # Thumbnail size
temp_all_images = []
current_video_id = ""
no_return_records = 10  # Default value
image_extension = ".webp"
temp_index = -1
index_path = []
annotations = []
csv_filename = ""
selected_labels = ["", ""]

if os.path.exists(IMAGE_DIR):
    for root_dir, _, files in os.walk(IMAGE_DIR):
        for file in files:
            if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                image_extension = os.path.splitext(file)[1]
                print(f"Image extension set to: {image_extension}")
                break
        else:
            continue
        break
else:
    print(f"IMAGE_DIR does not exist: {IMAGE_DIR}")

# Show image in GUI with height restriction
def display_image(canvas, image_path, max_size, row=0, col=0, clear_previous=True):
    """Displays an image in the given canvas, maintaining aspect ratio and optionally clearing previous images."""
    if image_path and os.path.exists(image_path):
        # ❗ Clear previous image **only if specified**
        if clear_previous:
            for widget in canvas.winfo_children():
                widget.destroy()

        # Open the image
        img = Image.open(image_path)
        max_width, max_height = max_size

        # Get original width and height
        orig_width, orig_height = img.size

        # Compute scale ratio for both dimensions
        width_ratio = max_width / orig_width
        height_ratio = max_height / orig_height

        # Use the smallest ratio to fit within both constraints
        scale_ratio = min(width_ratio, height_ratio)
        new_width = int(orig_width * scale_ratio)
        new_height = int(orig_height * scale_ratio)

        # Resize while maintaining aspect ratio
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        img_tk = ImageTk.PhotoImage(img)

        # Display new image
        label = tk.Label(canvas, image=img_tk)
        label.image = img_tk  # Keep reference to prevent garbage collection
        label.grid(row=row, column=col, padx=5, pady=5)  # Place in grid


        # Close the image to free memory (reduces "Fail to allocate bitmap" issue)
        img.close()     


def show_image(current_index, annotations, left_canvas, center_canvas, right_canvas, filename_label, count_index=True):
    """Displays the current image along with its previous and next images."""
    
    if not annotations:
        print("No images to display.")
        filename_label.config(text="No images available")
        
        # Clear all image labels
        for lbl in [prev_img_label, img_label, next_img_label]:
            lbl.config(image="", bg="black")
        return

    image_data = annotations[current_index]
    image_filename = image_data["image_filename"]
    main_label = image_data["main label"]

    # Get image paths (previous, current, next)
    global image_extension, IMAGE_DIR
    center_image_path = IMAGE_DIR + '/' + image_filename + image_extension if current_index < len(annotations) else None
    display_image(center_canvas, center_image_path, (350, 350))

    # Update filename label
    filename_label.config(text=f"Image: {os.path.basename(center_image_path)}" if center_image_path else "No Image")
    global label_box_1
    label_box_1.config(state="normal")
    label_box_1.delete(0, "end")
    label_box_1.insert(0, main_label)
    label_box_1.config(state="readonly")
    update_progress_label()
    return filename_label



# Enable mouse scroll for label selection area
def on_mouse_scroll_label_canvas(event):
    label_canvas.yview_scroll(-1 * (event.delta // 120), "units")

# Create a scrollable label selection area
def refresh_label_buttons(label_data, label_inner_frame, label_canvas, save_annotation):
    # Clear existing buttons inside the frame without destroying it
    for widget in label_inner_frame.winfo_children():
        widget.destroy()
    
    # Sort labels alphabetically before displaying
    sorted_labels = sorted(label_data)

    # Button size settings
    button_width = 13   # Fixed width (characters)
    button_height = 2   # Fixed height (lines)

    # Create buttons dynamically
    row, col = 0, 0
    for label in sorted_labels:
        btn = tk.Button(
            label_inner_frame, text=label, font=("Arial", 9), 
            wraplength=100,
            command=lambda l=label: save_annotation(l), 
            bg="lightgray", width=button_width, height=button_height
        )
        btn.grid(row=row, column=col, padx=5, pady=5)

        row += 1
        if row >= button_per_col: 
            row = 0
            col += 1

    # Update scroll region
    label_canvas.update_idletasks()
    label_canvas.config(scrollregion=label_canvas.bbox("all"))


# Load labels from JSON file
def load_labels():
    global label_data
    json_file = filedialog.askopenfilename(title="Select Labels JSON", filetypes=[("JSON Files", "*.json")])
    if json_file:
        with open(json_file, "r") as f:
            label_data = sorted(json.load(f))  # Sort labels alphabetically
        refresh_label_buttons(label_data, label_inner_frame, label_canvas, save_annotation)

# Load images from directory (only those not in CSV)
def load_images():
    """ Load and sort the CSV data by main label first, then by filename """
    global annotations, csv_filename
    csv_filename = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV Files", "*.csv")])
    if not csv_filename:
        return
    if os.path.exists(csv_filename):
        with open(csv_filename, "r") as file:
            reader = csv.DictReader(file)
            annotations = sorted(reader, key=lambda x: (x["main label"], x["image_filename"]))
        print(f"Loaded {len(annotations)} annotations.")
    else:
        print("CSV file not found.")
    global filename_label, left_canvas, center_canvas, right_canvas, current_index
    current_index = 0
    filename_label = show_image(current_index, annotations, left_canvas, center_canvas, right_canvas, filename_label) or (filename_label)
    update_progress_label()
    
    

# Update progress label
def update_progress_label():
    global current_index, annotations, progress_label
    if not annotations:
        return
    progress_label.config(text=f"Reviewed: {current_index + 1} / {len(annotations)}")


# Save annotation (copy image instead of moving)
import csv

def save_annotation(label1, label2="", skip_api_call=False):
    """ Updates the current image's main label and rewrites the CSV file """
    if not annotations:
        print("No images to save.")
        return
    
    global current_index
    image_filename = annotations[current_index]["image_filename"]

    # Update in-memory annotations list
    annotations[current_index]["main label"] = label1
    annotations[current_index]["concurrent label"] = label2

    # Read the CSV file and modify only the relevant row
    updated_rows = []
    with open(csv_filename, "r", newline="") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames  # Preserve column order
        for row in reader:
            if row["image_filename"] == image_filename:
                row["main label"] = label1
                row["concurrent label"] = label2
            updated_rows.append(row)

    # Rewrite the CSV file with updated data
    with open(csv_filename, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    print(f"Updated '{image_filename}' label to '{label1}' (Concurrent: '{label2}') in CSV.")
    go_next()

    


def on_label_click(label):
    """Handles label selection and updates text boxes."""
    global selected_labels
    selected_labels[0] = label
    label_box_1.config(state="normal")
    label_box_1.delete(0, tk.END)
    label_box_1.insert(0, label)
    label_box_1.config(state="readonly")
    save_annotation(selected_labels[0], selected_labels[1])  # Comment if want to have 2nd label
        
   


# Exit function
def on_exit(root):
    """Ensures all Tkinter windows close properly."""
    for window in root.winfo_children():  # Close any open dialogs
        window.destroy()
    root.quit()
    root.destroy()  # Fully terminate the application

def update_no_return_records(value):
    """Updates the global variable with the selected slider value."""
    global no_return_records
    no_return_records = int(value)

def load_neighbors():
    """Fetch and display neighboring images in a grid layout."""
    if not annotations:
        return

    image_url = annotations[current_index]["image_filename"]
    response = sorted(api_client.get_neighbors(image_url))

    if not response:
        print("No neighbors found.")
        return

    middle_index = len(response) // 2
    front_neighbors = response[:middle_index]
    back_neighbors = response[middle_index + 1:]

    # Define the grid size (3 rows, 2 columns)
    GRID_ROWS = 3
    GRID_COLS = 2

    # ❗ Clear left & right canvas **before** adding images
    global left_canvas, right_canvas
    for widget in left_canvas.winfo_children():
        widget.destroy()
    for widget in right_canvas.winfo_children():
        widget.destroy()

    # Display Left Neighbors (Before)
    for i, img_url in enumerate(front_neighbors[:GRID_ROWS * GRID_COLS]):
        full_path = os.path.join(IMAGE_DIR, img_url + image_extension).replace("\\", "/")
        row, col = divmod(i, GRID_COLS)  # Convert index to grid row/col
        display_image(left_canvas, full_path, (140, 130), row, col, clear_previous=False)

    # Display Right Neighbors (After)
    for i, img_url in enumerate(back_neighbors[:GRID_ROWS * GRID_COLS]):
        full_path = os.path.join(IMAGE_DIR, img_url + image_extension).replace("\\", "/")
        row, col = divmod(i, GRID_COLS)  # Convert index to grid row/col
        display_image(right_canvas, full_path, (140, 130), row, col, clear_previous=False)

    print(f"Neighbors loaded: {len(response)}")

def go_back():
    global current_index
    if annotations and current_index > 0:
        current_index -= 1
        global center_canvas, filename_label, left_canvas, right_canvas
        show_image(current_index, annotations, left_canvas, center_canvas, right_canvas, filename_label)
        for widget in left_canvas.winfo_children():
            widget.destroy()
        for widget in right_canvas.winfo_children():
            widget.destroy()
   

def go_next():
    global current_index
    if annotations and current_index < len(annotations) - 1:
        current_index += 1
        global center_canvas, filename_label, left_canvas, right_canvas
        show_image(current_index, annotations, left_canvas, center_canvas, right_canvas, filename_label)
        for widget in left_canvas.winfo_children():
            widget.destroy()
        for widget in right_canvas.winfo_children():
            widget.destroy()
    else:
        messagebox.showinfo("End of Images", "No more images to review.")
    


# Tkinter GUI Setup

root = tk.Tk()
root.title("Image Annotation Tool")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

window_width = int(screen_width * 0.96)
window_height = int(screen_height * 0.9)

x_position = 0
y_position = 0

root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")


# Top Menu Buttons
top_frame = tk.Frame(root)
top_frame.pack(fill="x", pady=1)

# tk.Button(top_frame, text="Load Labels", font=("Arial", 12), command=load_labels).pack(side="left", padx=10)
# tk.Button(top_frame, text="Set Output Folder", font=("Arial", 12), command=select_output_folder).pack(side="left", padx=10)
# tk.Button(top_frame, text="Exit", font=("Arial", 12), command=lambda: on_exit(root), fg="white", bg="red").pack(side="right", padx=10)

# Loading Label
loading_label = tk.Label(root, text="", font=("Arial", 12))

# CSV Filename Entry
csv_frame = tk.Frame(root)
csv_frame.pack(fill="x", padx=10)

# Label(csv_frame, text="Output CSV:", font=("Arial", 12)).pack(side="left", padx=5)
# csv_entry = Entry(csv_frame, font=("Arial", 12), width=30)
# csv_entry.pack(side="left", padx=5)
# tk.Button(csv_frame, text="Set", font=("Arial", 12), command=set_csv_filename).pack(side="left", padx=5)

# Slider for controlling no_return_records
tk.Button(csv_frame, text="Load CSV", font=("Arial", 9), command=load_images).pack(side="left", padx=10)
Label(csv_frame, text="Returned Records: ", font=("Arial", 8)).pack(side="left", padx=5)
slider = tk.Scale(csv_frame, from_=10, to=30, orient="horizontal", length=200,
                  font=("Arial", 9), command=update_no_return_records)
slider.pack(side="left", padx=10)
slider.set(no_return_records)  # Set initial value to default

# Label Selection Input Box
label_box_frame = tk.Frame(root)
label_box_frame.pack(pady=5)

Label(label_box_frame, text="Selected Labels:", font=("Arial", 9)).grid(row=0, column=0, columnspan=2)

label_box_1 = tk.Entry(label_box_frame, font=("Arial", 9), width=20, state="readonly")
label_box_1.grid(row=0, column=2)


neighbor_button = tk.Button(label_box_frame, text="Load Neighbors", font=("Arial", 9), command=load_neighbors)
neighbor_button.grid(row=0, column=4, padx=5)

back_button = tk.Button(label_box_frame, text="BACK", font=("Arial", 9), bg="yellow", command=go_back)
back_button.grid(row=0, column=5, padx=5)

next_button = tk.Button(label_box_frame, text="NEXT", font=("Arial", 9), bg="yellow", command=go_next)
next_button.grid(row=0, column=7, padx=5)

 # **Main Layout Frame**
main_frame = tk.Frame(root, height=500)
main_frame.pack(expand=True, fill="both")

# **Left Section (Neighbors - Before)**
left_frame = tk.Frame(main_frame)
left_frame.pack(side="left", expand=True, fill="both")

# **Center Section (Main Image)**
center_frame = tk.Frame(main_frame)
center_frame.pack(side="left", expand=True, fill="both")

# **Right Section (Neighbors - After)**
right_frame = tk.Frame(main_frame)
right_frame.pack(side="left", expand=True, fill="both")

# **Canvases for Images**
left_canvas = tk.Frame(left_frame)
left_canvas.pack(expand=True, fill="both")

center_canvas = tk.Canvas(center_frame, width=500, height=350)
center_canvas.pack(expand=True)

right_canvas = tk.Frame(right_frame)
right_canvas.pack(expand=True, fill="both")


# Filename Label
filename_label = tk.Label(root, text="", font=("Arial", 10))
filename_label.pack(pady=5)


# Progress Label
progress_frame = tk.Frame(root)
progress_frame.pack(pady=5)

progress_label = tk.Label(progress_frame, text="Reviewd: 0", font=("Arial", 12))
progress_label.pack(side="left", padx=5)

# Scrollable Label Selection Area
label_container = tk.Frame(root, width=800)
label_container.pack(padx=10, pady=5)

label_canvas = Canvas(label_container, height=300, width=1000)
label_scrollbar = Scrollbar(label_container, orient="vertical", command=label_canvas.yview)

label_inner_frame = Frame(label_canvas)
label_canvas.create_window((0, 0), window=label_inner_frame, anchor="nw")

label_canvas.config(yscrollcommand=label_scrollbar.set)
label_canvas.pack(side="left", fill="x", expand=True)
label_scrollbar.pack(side="right", fill="y")

label_canvas.bind("<MouseWheel>", on_mouse_scroll_label_canvas)
root.bind("<s>", lambda event: load_neighbors())
# root.bind("<Tab>", on_tab_press)  # Bind Tab key to trigger save_annotation

# Load labels
json_file = label_file
if json_file:
    with open(json_file, "r") as f:
        label_data = sorted(json.load(f))  # Sort labels alphabetically
    print("Loaded labels from JSON file.")
    refresh_label_buttons(label_data, label_inner_frame, label_canvas, on_label_click)

root.bind("<Right>", lambda event: go_next())
root.bind("<Left>", lambda event: go_back())

root.mainloop()