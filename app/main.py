import os
import json
import shutil
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, Canvas, Frame, Scrollbar, Entry, Label
from PIL import Image, ImageTk
from rest_client import RestClient
from utils import get_path_for_vector_db, get_base_path
from constant import image_list, current_index, image_dir, output_dir, output_csv, label_data, csv_columns, annotated_images, total_images, base_path, have_base_path, label_file, button_per_row


api_client = RestClient("http://34.97.0.203:8004")

THUMBNAIL_SIZE = (200, 150)  # Thumbnail size
temp_all_images = []
current_video_id = ""
no_return_records = 10  # Default value

def show_propagated_records_dialog(root, base_path, propagated_records, label1, label2):
    """
    Opens a dialog to review and remove propagated records before saving.
    """
    global image_list, current_index
    temp_propagated_records = propagated_records.copy()
    for record in propagated_records:
        if record in annotated_images:
            temp_propagated_records.remove(record)
    propagated_records = temp_propagated_records

    def remove_selected():
        """Removes selected items from propagated_records and image_list, then updates the UI."""
        nonlocal propagated_records
        # Remove selected images from both propagated_records and image_list
        propagated_records = [img for img in propagated_records if img not in selected_images]
        
        # for img in selected_images:
        #     if img in image_list:
        #         image_list.remove(img)  # Remove from main image list as well
        
        selected_images.clear()
        update_grid()

        if not propagated_records or len(propagated_records) == 0:
            messagebox.showinfo("Success", "No more images to propagate.")
            clear_label_boxes()
            dialog.destroy()
            try:
                if (api_client.send_accepted_data([get_path_for_vector_db(image_list[current_index]).split(".")[0]])):
                    print("Successfully sent accepted data to server.")
                else:
                    print("Failed to send accepted data to server.")
                    messagebox.showerror("Error", "Failed to send accepted data to server.")
            except Exception as e:
                print(f"Error sending accepted data: {e}")
                messagebox.showerror("Error", f"Failed to send accepted data to server: {e}")
            save_annotation(label1, label2, skip_api_call=True)  # Resume save_annotation but skip API call
            return

    def remove_all():
        """Removes all propagated records and updates the UI."""
        nonlocal propagated_records
        propagated_records.clear()  # Clear all records
        selected_images.clear()  # Clear selected images set
        update_grid()  # Refresh the UI

        messagebox.showinfo("Success", "All propagated records have been removed.")
        clear_label_boxes()
        dialog.destroy()
        try:
            if (api_client.send_accepted_data([get_path_for_vector_db(image_list[current_index]).split(".")[0]])):
                print("Successfully sent accepted data to server.")
            else:
                print("Failed to send accepted data to server.")
                messagebox.showerror("Error", "Failed to send accepted data to server.")
        except Exception as e:
            print(f"Error sending accepted data: {e}")
            messagebox.showerror("Error", f"Failed to send accepted data to server: {e}")
        save_annotation(label1, label2, skip_api_call=True)  # Resume save_annotation but skip API call


    def submit_records():
        """Writes final propagated records to CSV and updates image list."""
        nonlocal propagated_records
        if not propagated_records:
            messagebox.showinfo("Info", "No records to save.")
            dialog.destroy()
            save_annotation(label1, label2, skip_api_call=True)  # Resume save_annotation but skip API call
            return

        # Save the remaining propagated records to CSV
        df = pd.DataFrame([[filename, label1, label2] for filename in propagated_records], columns=csv_columns)
        df.to_csv(output_csv, mode="a", header=not os.path.exists(output_csv), index=False)

        for img in propagated_records:
            annotated_images.add(img)
        
        try:
            temp_records = propagated_records.copy()
            temp_records.append(get_path_for_vector_db(image_list[current_index]).split(".")[0])
            print(temp_records)
            if (api_client.send_accepted_data(temp_records)):
                print("Successfully sent accepted data to server.")
            else:
                print("Failed to send accepted data to server.")
                messagebox.showerror("Error", "Failed to send accepted data to server.")
        except Exception as e:
            print(f"Error sending accepted data: {e}")
            messagebox.showerror("Error", f"Failed to send accepted data to server: {e}")
        
        update_progress_label()

        # Update UI to the next available image
        move_to_next_image()
        clear_label_boxes()

        dialog.destroy()

    def update_grid():
        """Refresh the grid with the current propagated records."""
        for widget in grid_frame.winfo_children():
            widget.destroy()

        row, col = 0, 0
        for img_path in propagated_records:
            try:
                # Find the real image path with extension
                img_full_path = None
                for ext in [".png", ".jpg", ".jpeg"]:
                    potential_path = os.path.join(base_path, img_path + ext).replace("\\", "/")
                    if os.path.exists(potential_path):
                        img_full_path = potential_path
                        break

                if not img_full_path:
                    print(f"Image file for {img_path} not found with any expected extension.")
                    continue

                if not os.path.exists(img_full_path):
                    print(f"Image file {img_full_path} not found.")
                    continue

                img = Image.open(img_full_path)
                img.thumbnail(THUMBNAIL_SIZE)
                img_tk = ImageTk.PhotoImage(img)

                btn = tk.Button(grid_frame, image=img_tk, width=THUMBNAIL_SIZE[0], height=THUMBNAIL_SIZE[1])
                btn.image = img_tk  # Prevent garbage collection

                btn.config(command=lambda p=img_path, b=btn: toggle_selection(p, b))
                btn.grid(row=row, column=col, padx=5, pady=5)

                col += 1
                if col >= 2:  # 3 images per row
                    col = 0
                    row += 1
            except Exception as e:
                print(f"Error loading {img_path}: {e}")

        canvas.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def toggle_selection(img_path, button):
        """Toggles selection of an image (highlights if selected)."""
        if img_path in selected_images:
            selected_images.remove(img_path)
            button.config(bg="white")  # Reset color
        else:
            selected_images.add(img_path)
            button.config(bg="red")  # Highlight selected

    def on_mouse_scroll(event):
        """Enable mouse scroll for the image grid."""
        canvas.yview_scroll(-1 * (event.delta // 120), "units")

    # Create the dialog window
    dialog = tk.Toplevel(root)
    dialog.title("Review Propagated Records")
    dialog.geometry("500x800")
    dialog.transient(root)
    dialog.grab_set()

    tk.Label(dialog, text="Click images to select/remove. Scroll to navigate.", font=("Arial", 12)).pack(pady=5)

    frame_container = tk.Frame(dialog)
    frame_container.pack(fill="both", expand=True, padx=10, pady=5)

    canvas = tk.Canvas(frame_container)
    scrollbar = tk.Scrollbar(frame_container, orient="vertical", command=canvas.yview)

    scroll_frame = tk.Frame(canvas)
    scroll_frame.bind("<Configure>", lambda e: canvas.config(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.config(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    grid_frame = tk.Frame(scroll_frame)
    grid_frame.pack()

    selected_images = set()

    update_grid()

    dialog.bind("<MouseWheel>", on_mouse_scroll)

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(fill="x", pady=10)

    remove_btn = tk.Button(btn_frame, text="Remove Selected", command=remove_selected, bg="red", fg="white", width=15, height=2)
    remove_btn.pack(side="left", padx=5)

    remove_all_btn = tk.Button(btn_frame, text="Remove All", command=remove_all, bg="orange", fg="white", width=15, height=2)
    remove_all_btn.pack(side="left", padx=5)

    submit_btn = tk.Button(btn_frame, text="Submit", command=submit_records, bg="green", fg="white", width=15, height=2)
    submit_btn.pack(side="right", padx=5)

    dialog.mainloop()

# Show image in GUI with height restriction
# def show_image(current_index, image_list, img_label, filename_label):
#     if not image_list:
#         print("No images to display.")
#         filename_label.config(text="No images available")
#         img_label.config(image="")  # Clear the previous image
#         return img_label, filename_label  # Ensure function always returns values

#     image_path = image_list[current_index]  # Already an absolute path
#     try:
#         image = Image.open(image_path)
#         max_height = 380
#         img_width, img_height = image.size
#         scale_factor = max_height / img_height
#         new_size = (int(img_width * scale_factor), max_height) if img_height > max_height else (img_width, img_height)

#         image = image.resize(new_size, Image.Resampling.LANCZOS)
#         img = ImageTk.PhotoImage(image)
#         img_label.config(image=img)
#         img_label.image = img  # Prevent garbage collection
#         filename_label.config(text=f"Image: {os.path.basename(image_path)}")

#     except Exception as e:
#         print(f"Error displaying image {image_path}: {e}")
#         filename_label.config(text=f"Error loading image: {os.path.basename(image_path)}")
#         img_label.config(image="")  # Clear image if error occurs

#     return img_label, filename_label  # Always return valid objects
def show_image(current_index, image_list, prev_img_label, img_label, next_img_label, filename_label):
    """Displays the current image along with its previous and next images."""
    
    if not image_list:
        print("No images to display.")
        filename_label.config(text="No images available")
        
        # Clear all image labels
        for lbl in [prev_img_label, img_label, next_img_label]:
            lbl.config(image="", bg="black")
        return

    # Get image paths (previous, current, next)
    current_image_path = image_list[current_index] if current_index < len(temp_all_images) else None
    idx_current_in_all_images = temp_all_images.index(current_image_path)
    prev_image_path = temp_all_images[idx_current_in_all_images - 1] if idx_current_in_all_images > 0 else None
    next_image_path = temp_all_images[idx_current_in_all_images + 1] if idx_current_in_all_images + 1 < len(temp_all_images) else None

    def load_thumbnail(image_path, label_widget, max_height=380):
        """Loads and resizes an image, setting it to the given label widget."""
        if image_path and os.path.exists(image_path):
            try:
                image = Image.open(image_path)
                img_width, img_height = image.size
                
                # Resize while maintaining aspect ratio
                scale_factor = max_height / img_height
                new_size = (int(img_width * scale_factor), max_height) if img_height > max_height else (img_width, img_height)
                
                image = image.resize(new_size, Image.Resampling.LANCZOS)
                img_tk = ImageTk.PhotoImage(image)
                
                label_widget.config(image=img_tk)
                label_widget.image = img_tk  # Prevent garbage collection
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
                label_widget.config(image="")  # Reset if error
        else:
            label_widget.config(image="")  # Reset if no image found

    # Load images into labels
    load_thumbnail(prev_image_path, prev_img_label, max_height=300)
    load_thumbnail(current_image_path, img_label, max_height=380)
    load_thumbnail(next_image_path, next_img_label, max_height=300)

    # Update filename label
    filename_label.config(text=f"Image: {os.path.basename(current_image_path)}" if current_image_path else "No Image")



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
    button_width = 11   # Fixed width (characters)
    button_height = 2   # Fixed height (lines)

    # Create buttons dynamically
    row, col = 0, 0
    for label in sorted_labels:
        btn = tk.Button(
            label_inner_frame, text=label, font=("Arial", 10), 
            wraplength=100,
            command=lambda l=label: save_annotation(l), 
            bg="lightgray", width=button_width, height=button_height
        )
        btn.grid(row=row, column=col, padx=5, pady=5)

        col += 1
        if col >= button_per_row: 
            col = 0
            row += 1

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
    global image_list, image_dir, current_index, annotated_images, total_images
    image_dir = filedialog.askdirectory(title="Select Image Directory")
    
    if not image_dir:
        return

    # Read the existing CSV file and track labeled images
    annotated_images = set()
    if os.path.exists(output_csv):
        try:
            df = pd.read_csv(output_csv)
            annotated_images = set(df["image_filename"].tolist())  # Ensure column name matches CSV
        except Exception as e:
            messagebox.showerror("Error", f"Could not read CSV file: {e}")

    global current_video_id
    try:
        video_id = "/".join(image_dir.split("/")[-2:])
        current_video_id = video_id
        if not api_client.init(video_id,[]):
            raise Exception("Could not clear session.")
    except Exception as e:
        print(f"Error clearing session: {e}")
        messagebox.showerror("Error", f"Could not clear session: {e}")
        return

    try: 
        temp = list(annotated_images)
        if not api_client.init(current_video_id, temp):
            raise Exception("Could not send annotated data.")
    except Exception as e:
        print(f"Error sending past data: {e}")
        messagebox.showerror("Error", f"Could not load_images: {e}")
        return

    # Get all images (absolute paths) and filter out already annotated ones
    all_images = [
        os.path.join(image_dir, f) for f in os.listdir(image_dir) 
        if f.lower().endswith((".png", ".jpg", ".jpeg"))
    ]
    total_images = len(all_images)
    print(f"Total images: {total_images}")

    # Ensure we only load new images
    image_list = sorted([img for img in all_images if os.path.splitext(get_path_for_vector_db(img))[0] not in annotated_images])
    global temp_all_images
    temp_all_images = sorted(all_images)
    print(f"New images to label: {len(image_list)}")

    if not image_list:
        messagebox.showinfo("Info", "No new images to label.")
        return

    global have_base_path
    if not have_base_path:
        global base_path 
        base_path = get_base_path(image_list[0])
        have_base_path = True
        print("Base path: ", base_path)

    current_index = 0
    update_progress_label()  # Update progress count
    global img_label, filename_label
    img_label, filename_label = show_image(current_index, image_list, prev_img_label, img_label, next_img_label, filename_label) or (img_label, filename_label)



# Select output directory
def select_output_folder():
    global output_dir
    output_dir = filedialog.askdirectory(title="Select Output Directory")
    if not output_dir:
        messagebox.showwarning("Warning", "No output directory selected!")

# Update progress label
def update_progress_label():
    progress_label.config(text=f"Progress: {len(annotated_images)}/{total_images}")

# Save annotation (copy image instead of moving)
def save_annotation(label1, label2 = "", skip_api_call=False):
    global current_index
    global annotated_images
    global selected_labels
    # if not image_list or not output_dir:
    #     messagebox.showwarning("Warning", "Please select an output directory first!")
    #     return

    image_name = image_list[current_index]
    image_name = get_path_for_vector_db(image_name) # Only for LSC dataset
    image_name_no_ext = str(os.path.splitext(image_name)[0])

     # If API call should be skipped, just append the record to CSV and move to the next image
    if skip_api_call:
        
        df = pd.DataFrame([[image_name_no_ext, label1, label2]], columns=csv_columns)
        df.to_csv(output_csv, mode="a", header=not os.path.exists(output_csv), index=False)
        annotated_images.add(image_name_no_ext)
        print(len(annotated_images))
        update_progress_label()
        move_to_next_image()
        return
    # label_folder = os.path.join(output_dir, label)

    # # Ensure label directory exists
    # os.makedirs(label_folder, exist_ok=True)

    # # Copy the image to the label directory
    # shutil.copy(os.path.join(image_dir, image_name), os.path.join(label_folder, image_name))

    # Propagate label by calling to server
    show_loading()
    response = None
    try: 
        response = api_client.get_similars(image_name_no_ext, no_return_records=no_return_records)
    except Exception as e:
        print(f"Error sending annotation: {e}")
        hide_loading()
        clear_label_boxes()
        messagebox.showerror("Error", f"Could not send annotation: {e}")
        return
    finally:  
        hide_loading()

    propagated_records = response if response else []
    if len(propagated_records) == 0:
        save_annotation(label1, label2, skip_api_call=True)  # Resume save_annotation but skip API call
        return
    for record in propagated_records:
        img_full_path = None
        for ext in [".png", ".jpg", ".jpeg"]:
            potential_path = os.path.join(base_path, record + ext).replace("\\", "/")
            if os.path.exists(potential_path):
                img_full_path = potential_path
                break

        if not img_full_path:
            print(f"Image file for {record} not found with any expected extension.")
            continue
        img_filename_with_ext = get_path_for_vector_db(img_full_path)
        if img_filename_with_ext in annotated_images:
            propagated_records.remove(record)
    if not propagated_records:
        print("No propagated records received.")
    else:
        # Show dialog to allow user to modify the list
        show_propagated_records_dialog(root, base_path, propagated_records, label1, label2)

    clear_label_boxes()
   

# Set custom CSV filename
def set_csv_filename():
    global output_csv
    filename = csv_entry.get().strip()
    if filename:
        if not filename.endswith(".csv"):
            filename += ".csv"
        output_csv = filename
        messagebox.showinfo("Success", f"Output CSV set to: {output_csv}")
    else:
        messagebox.showwarning("Warning", "Invalid CSV filename!")

# Global variables to store selected labels
selected_labels = ["", ""]  # Store first and second selected labels

def on_label_click(label):
    """Handles label selection and updates text boxes."""
    global selected_labels
    if not selected_labels[0]:  # First label slot is empty
        selected_labels[0] = label
        label_box_1.config(state="normal")
        label_box_1.delete(0, tk.END)
        label_box_1.insert(0, label)
        label_box_1.config(state="readonly")
    elif not selected_labels[1]:  # Second label slot is empty
        selected_labels[1] = label
        label_box_2.config(state="normal")
        label_box_2.delete(0, tk.END)
        label_box_2.insert(0, label)
        label_box_2.config(state="readonly")
        save_annotation(selected_labels[0], selected_labels[1])  # Save annotation

def on_tab_press(event):
    """Triggers save_annotation when Tab is pressed after the first label is chosen."""
    if selected_labels[0] and not selected_labels[1]:  # If first label is selected but not the second
        save_annotation(selected_labels[0])

def show_loading():
    """Displays loading message when API request is sent."""
    global loading_label
    loading_label.config(text="Processing...", fg="blue")
    root.update_idletasks()  # Update UI immediately
    print("show")

def hide_loading():
    """Hides loading message when API request is complete."""
    global loading_label
    loading_label.config(text="")

def clear_label_boxes():
    """Clears the selected labels from both label boxes."""
    global selected_labels
    selected_labels = ["", ""]
    label_box_1.config(state="normal")
    label_box_1.delete(0, tk.END)
    label_box_1.config(state="readonly")

    label_box_2.config(state="normal")
    label_box_2.delete(0, tk.END)
    label_box_2.config(state="readonly")

def move_to_next_image():
    """Move to the next image in the list."""
    global current_index
    current_index += 1
    if current_index < len(image_list):
        global img_label, filename_label
        img_path = image_list[current_index]
        img_path = get_path_for_vector_db(img_path)
        img_path = os.path.splitext(img_path)[0]
        if img_path in annotated_images:
            move_to_next_image()
            return

        img_label, filename_label = show_image(current_index, image_list, prev_img_label, img_label, next_img_label, filename_label) or (img_label, filename_label)
    else:
        messagebox.showinfo("Done", "All images labeled!")
        root.quit()

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


# Tkinter GUI Setup
root = tk.Tk()
root.title("Image Annotation Tool")
root.attributes('-fullscreen', True)  # Full-screen mode

# Top Menu Buttons
top_frame = tk.Frame(root)
top_frame.pack(fill="x", pady=1)

tk.Button(top_frame, text="Load Labels", font=("Arial", 12), command=load_labels).pack(side="left", padx=10)
tk.Button(top_frame, text="Load Images", font=("Arial", 12), command=load_images).pack(side="left", padx=10)
# tk.Button(top_frame, text="Set Output Folder", font=("Arial", 12), command=select_output_folder).pack(side="left", padx=10)
tk.Button(top_frame, text="Exit", font=("Arial", 12), command=lambda: on_exit(root), fg="white", bg="red").pack(side="right", padx=10)

# Loading Label
loading_label = tk.Label(root, text="", font=("Arial", 12))

# CSV Filename Entry
csv_frame = tk.Frame(root)
csv_frame.pack(fill="x", padx=10)

Label(csv_frame, text="Output CSV:", font=("Arial", 12)).pack(side="left", padx=5)
csv_entry = Entry(csv_frame, font=("Arial", 12), width=30)
csv_entry.pack(side="left", padx=5)
tk.Button(csv_frame, text="Set", font=("Arial", 12), command=set_csv_filename).pack(side="left", padx=5)

# Slider for controlling no_return_records
Label(csv_frame, text="Returned Records: ", font=("Arial", 8)).pack(side="left", padx=5)
slider = tk.Scale(csv_frame, from_=10, to=30, orient="horizontal", length=200,
                  font=("Arial", 10), command=update_no_return_records)
slider.pack(side="left", padx=10)
slider.set(no_return_records)  # Set initial value to default

# Label Selection Input Box
label_box_frame = tk.Frame(root)
label_box_frame.pack(pady=5)

Label(label_box_frame, text="Selected Labels:", font=("Arial", 12)).grid(row=0, column=0, columnspan=2)

label_box_1 = tk.Entry(label_box_frame, font=("Arial", 12), width=20, state="readonly")
label_box_1.grid(row=1, column=0, padx=5)

label_box_2 = tk.Entry(label_box_frame, font=("Arial", 12), width=20, state="readonly")
label_box_2.grid(row=1, column=1, padx=5)

clear_button = tk.Button(label_box_frame, text="Clear Labels", font=("Arial", 12), command=clear_label_boxes)
clear_button.grid(row=1, column=2, padx=5)


# Image Display Area (Three images in a row)
img_frame = tk.Frame(root,relief="solid", height=120, width=507)
img_frame.pack(fill="x", padx=20, pady=5)

# Ensure equal column expansion
img_frame.grid_columnconfigure(0, weight=1)
img_frame.grid_columnconfigure(1, weight=1)
img_frame.grid_columnconfigure(2, weight=1)

# Left Image (Previous Image)
prev_img_label = tk.Label(img_frame)  
prev_img_label.grid(row=0, column=0, sticky="nsew", padx=5)

# Center Image (Current Image)
img_label = tk.Label(img_frame, bg="red")  
img_label.grid(row=0, column=1, sticky="nsew", padx=5)

# Right Image (Next Image)
next_img_label = tk.Label(img_frame)  
next_img_label.grid(row=0, column=2, sticky="nsew", padx=5)

# Filename Label
filename_label = tk.Label(root, text="", font=("Arial", 14))
filename_label.pack(pady=5)


# Progress Label
progress_label = tk.Label(root, text="Progress: 0/0", font=("Arial", 12))
progress_label.pack(pady=5)

# Scrollable Label Selection Area
label_container = tk.Frame(root)
label_container.pack(fill="x", padx=10, pady=5)

label_canvas = Canvas(label_container, height=300)
label_scrollbar = Scrollbar(label_container, orient="vertical", command=label_canvas.yview)

label_inner_frame = Frame(label_canvas)
label_canvas.create_window((0, 0), window=label_inner_frame, anchor="nw")

label_canvas.config(yscrollcommand=label_scrollbar.set)
label_canvas.pack(side="left", fill="x", expand=True)
label_scrollbar.pack(side="right", fill="y")

label_canvas.bind("<MouseWheel>", on_mouse_scroll_label_canvas)
root.bind("<Tab>", on_tab_press)  # Bind Tab key to trigger save_annotation

# Load labels
json_file = label_file
if json_file:
    with open(json_file, "r") as f:
        label_data = sorted(json.load(f))  # Sort labels alphabetically
    print("Loaded labels from JSON file.")
    refresh_label_buttons(label_data, label_inner_frame, label_canvas, on_label_click)

root.mainloop()