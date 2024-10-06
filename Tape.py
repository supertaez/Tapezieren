import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import os
import random

def select_folder(type):
    folder_path = filedialog.askdirectory()
    if folder_path:  # Ensure a folder is selected
        if type == 'sticker':
            sticker_folder.set(folder_path)
            stickers_dropdown['values'] = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        elif type == 'wallpaper':
            wallpaper_folder.set(folder_path)
        elif type == 'output':
            output_folder.set(folder_path)

def preview_image():
    if not wallpaper_folder.get() or not sticker_folder.get():
        return

    sticker_path = os.path.join(sticker_folder.get(), stickers_dropdown.get())
    wallpapers = [f for f in os.listdir(wallpaper_folder.get()) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    random_wallpaper = os.path.join(wallpaper_folder.get(), random.choice(wallpapers))

    sticker = Image.open(sticker_path).convert("RGBA")
    wallpaper = Image.open(random_wallpaper).convert("RGBA")

    # Calculate sticker size relative to wallpaper dimensions
    sticker_width = int(wallpaper.size[0] * sticker_scale.get())
    sticker_height = int(sticker.size[1] * (sticker_width / sticker.size[0]))
    sticker = sticker.resize((sticker_width, sticker_height), Image.LANCZOS)

    # Create a new image with the same size as the wallpaper
    combined = Image.new("RGBA", wallpaper.size)
    combined.paste(wallpaper, (0, 0))

    # Position the sticker based on slider values
    pos_x = int(x_pos_slider.get() * (wallpaper.size[0] - sticker.size[0]))
    pos_y = int(y_pos_slider.get() * (wallpaper.size[1] - sticker.size[1]))
    combined.paste(sticker, (pos_x, pos_y), sticker)

    combined.thumbnail((400, 400))  # Resize for preview

    combined_img = ImageTk.PhotoImage(combined)
    preview_label.config(image=combined_img)
    preview_label.image = combined_img

    # Schedule the next update
    root.after(100, preview_image)

def process_images():
    for filename in os.listdir(wallpaper_folder.get()):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            wallpaper_path = os.path.join(wallpaper_folder.get(), filename)
            sticker_path = os.path.join(sticker_folder.get(), stickers_dropdown.get())

            wallpaper = Image.open(wallpaper_path).convert("RGBA")
            sticker = Image.open(sticker_path).convert("RGBA")

            # Calculate sticker size relative to wallpaper dimensions
            sticker_width = int(wallpaper.size[0] * sticker_scale.get())
            sticker_height = int(sticker.size[1] * (sticker_width / sticker.size[0]))
            sticker = sticker.resize((sticker_width, sticker_height), Image.LANCZOS)

            # Create a new image with the same size as the wallpaper
            combined = Image.new("RGBA", wallpaper.size)
            combined.paste(wallpaper, (0, 0))

            # Position the sticker based on slider values
            pos_x = int(x_pos_slider.get() * (wallpaper.size[0] - sticker.size[0]))
            pos_y = int(y_pos_slider.get() * (wallpaper.size[1] - sticker.size[1]))
            combined.paste(sticker, (pos_x, pos_y), sticker)

            # Convert to RGB if saving as JPEG
            if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
                combined = combined.convert("RGB")

            combined.save(os.path.join(output_folder.get(), filename))

root = tk.Tk()
root.title("Wallpaper Sticker Overlay")

sticker_folder = tk.StringVar()
wallpaper_folder = tk.StringVar()
output_folder = tk.StringVar()

tk.Label(root, text="Sticker Folder:").pack()
tk.Entry(root, textvariable=sticker_folder).pack()
tk.Button(root, text="Select Sticker Folder", command=lambda: select_folder('sticker')).pack()

tk.Label(root, text="Stickers:").pack()
stickers_dropdown = ttk.Combobox(root)
stickers_dropdown.pack()

tk.Label(root, text="Wallpaper Folder:").pack()
tk.Entry(root, textvariable=wallpaper_folder).pack()
tk.Button(root, text="Select Wallpaper Folder", command=lambda: select_folder('wallpaper')).pack()

tk.Label(root, text="Output Folder:").pack()
tk.Entry(root, textvariable=output_folder).pack()
tk.Button(root, text="Select Output Folder", command=lambda: select_folder('output')).pack()

tk.Button(root, text="Preview", command=preview_image).pack(pady=10)

preview_label = tk.Label(root)
preview_label.pack()

sticker_scale = tk.DoubleVar()
sticker_scale.set(0.1)  # Default scale factor
tk.Scale(root, from_=0.01, to=1, resolution=0.01, variable=sticker_scale, orient=tk.HORIZONTAL, label="Sticker Size (relative to wallpaper width)").pack()

x_pos_slider = tk.DoubleVar()
x_pos_slider.set(0.5)
tk.Scale(root, from_=0, to=1, resolution=0.01, variable=x_pos_slider, orient=tk.HORIZONTAL, label="X Position").pack()

y_pos_slider = tk.DoubleVar()
y_pos_slider.set(0.5)
tk.Scale(root, from_=0, to=1, resolution=0.01, variable=y_pos_slider, orient=tk.HORIZONTAL, label="Y Position").pack()

tk.Button(root, text="Process", command=process_images).pack(pady=20)

# Start the real-time preview update
root.after(100, preview_image)

root.mainloop()
