import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
from datetime import datetime
import calendar
import matplotlib.font_manager as fm
import threading
import queue

# Set Sunday as the first day of the week
calendar.setfirstweekday(6)

def get_available_fonts():
    all_fonts = fm.findSystemFonts()
    available_fonts = []
    for font in all_fonts:
        try:
            ImageFont.truetype(font, 12)
            font_name = fm.FontProperties(fname=font).get_name()
            available_fonts.append(font_name)
        except IOError:
            continue
    return sorted(set(available_fonts))

def get_font(font_name, font_size):
    try:
        return ImageFont.truetype(font_name, font_size)
    except IOError:
        print(f"Font {font_name} not found. Trying system fonts.")
        system_fonts = fm.findSystemFonts()
        for font_path in system_fonts:
            try:
                if fm.FontProperties(fname=font_path).get_name() == font_name:
                    return ImageFont.truetype(font_path, font_size)
            except IOError:
                continue
        print("Specified font not found. Using default font.")
        return ImageFont.load_default()


def add_calendar(image_path, output_path, font_name, font_size, font_color, box_color, transparency, curvature,
                 table_size, x_offset, y_offset):
    try:
        with Image.open(image_path).convert("RGBA") as img:
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            img_width, img_height = img.size
            base_size = min(img_width, img_height)
            cell_width = int(base_size / 7 * table_size)
            cell_height = int(base_size / 8 * table_size)
            margin = int(0.02 * base_size * table_size)

            font = get_font(font_name, font_size)

            now = datetime.now()
            year, month = now.year, now.month
            cal = calendar.monthcalendar(year, month)
            month_name = calendar.month_name[month]

            x_start, y_start = int(x_offset * img_width), int(y_offset * img_height)
            title_text = f"{month_name} {year}"
            title_bbox = draw.textbbox((0, 0), title_text, font=font)
            title_width, title_height = title_bbox[2] - title_bbox[0], title_bbox[3] - title_bbox[1]
            title_x = x_start + (cell_width * 7 - title_width) // 2
            title_y = y_start + margin

            box_color_with_alpha = (*box_color[:3], int(255 * transparency))
            calendar_width = cell_width * 7 + 2 * margin
            calendar_height = cell_height * (len(cal) + 1) + 2 * margin + title_height
            draw.rounded_rectangle(
                [(x_start, y_start), (x_start + calendar_width, y_start + calendar_height)],
                radius=int(curvature * base_size / 100), fill=box_color_with_alpha
            )

            draw.text((title_x, title_y), title_text, font=font, fill=font_color)

            days = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"]
            for i, day in enumerate(days):
                x = x_start + i * cell_width + margin
                y = y_start + title_height + 2 * margin
                day_bbox = draw.textbbox((0, 0), day, font=font)
                day_width, day_height = day_bbox[2] - day_bbox[0], day_bbox[3] - day_bbox[1]
                day_x = x + (cell_width - day_width) // 2
                day_y = y + (cell_height - day_height) // 2
                draw.text((day_x, day_y), day, font=font, fill=font_color)

            holiday_color = (*font_color[:3], 128)  # Semi-transparent version of font color
            border_width = max(1, int(cell_width * 0.03))  # Adjust border width based on cell size

            for week_index, week in enumerate(cal):
                for day_index, day in enumerate(week):
                    if day != 0:
                        x = x_start + day_index * cell_width + margin
                        y = y_start + (week_index + 1) * cell_height + title_height + 2 * margin

                        # Draw holiday border for Friday (day_index 5) and Saturday (day_index 6)
                        if day_index in [5, 6]:
                            draw.rectangle(
                                [(x, y), (x + cell_width, y + cell_height)],
                                outline=holiday_color,
                                width=border_width
                            )

                        date_text = str(day)
                        date_bbox = draw.textbbox((0, 0), date_text, font=font)
                        date_width, date_height = date_bbox[2] - date_bbox[0], date_bbox[3] - date_bbox[1]
                        date_x = x + (cell_width - date_width) // 2
                        date_y = y + (cell_height - date_height) // 2
                        draw.text((date_x, date_y), date_text, font=font, fill=font_color)

            img = Image.alpha_composite(img, overlay)

            if output_path.lower().endswith((".jpg", ".jpeg")):
                img = img.convert("RGB")

            img.save(output_path)
    except Exception as e:
        print(f"Failed to process {image_path}: {e}")

def process_folder(folder_path, output_folder, font_name, font_size, font_color, box_color, transparency, curvature, table_size, x_offset, y_offset):
    if not os.path.exists(folder_path):
        print(f"Input folder does not exist: {folder_path}")
        return
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(folder_path, filename)
            output_path = os.path.join(output_folder, f"calendar_{filename}")
            add_calendar(image_path, output_path, font_name, font_size, font_color, box_color, transparency, curvature, table_size, x_offset, y_offset)

class CalendarApp:
    def __init__(self, master):
        self.master = master
        master.title("Calendar Wallpaper Overlay")

        self.fonts = get_available_fonts()
        if not self.fonts:
            self.fonts = ["default"]

        ttk.Label(master, text="Select Font:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.font_var = tk.StringVar(master)
        self.font_dropdown = ttk.Combobox(master, textvariable=self.font_var, values=self.fonts)
        self.font_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.font_dropdown.set(self.fonts[0])

        ttk.Label(master, text="Font Size:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.font_size_var = tk.IntVar(master, value=40)
        self.font_size_entry = ttk.Entry(master, textvariable=self.font_size_var)
        self.font_size_entry.grid(row=1, column=1, padx=5, pady=5)

        self.font_color_button = ttk.Button(master, text="Choose Font Color", command=self.choose_font_color)
        self.font_color_button.grid(row=2, column=0, columnspan=2, pady=5)

        self.box_color_button = ttk.Button(master, text="Choose Box Color", command=self.choose_box_color)
        self.box_color_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.create_slider(master, "Transparency", 4, 0.5, 0, 1)
        self.create_slider(master, "Curvature", 5, 20, 0, 100)
        self.create_slider(master, "Table Size", 6, 1.0, 0.1, 2.0)
        self.create_slider(master, "X Offset", 7, 0.5, 0, 1)
        self.create_slider(master, "Y Offset", 8, 0.5, 0, 1)

        self.input_folder_button = ttk.Button(master, text="Select Input Folder", command=self.choose_input_folder)
        self.input_folder_button.grid(row=9, column=0, columnspan=2, pady=5)

        self.output_folder_button = ttk.Button(master, text="Select Output Folder", command=self.choose_output_folder)
        self.output_folder_button.grid(row=10, column=0, columnspan=2, pady=5)

        self.preview_button = ttk.Button(master, text="Preview", command=self.preview_image)
        self.preview_button.grid(row=11, column=0, columnspan=2, pady=10)

        self.process_button = ttk.Button(master, text="Process Images", command=self.process_images)
        self.process_button.grid(row=12, column=0, columnspan=2, pady=10)

        self.font_color = (255, 255, 255)
        self.box_color = (0, 0, 0)
        self.input_folder = ""
        self.output_folder = ""

    def create_slider(self, master, text, row, default, min_val, max_val):
        ttk.Label(master, text=f"{text}:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        var = tk.DoubleVar(master, value=default)
        slider = ttk.Scale(master, from_=min_val, to=max_val, orient="horizontal", variable=var)
        slider.grid(row=row, column=1, padx=5, pady=5)
        setattr(self, f"{text.lower().replace(' ', '_')}_var", var)

    def choose_font_color(self):
        color = colorchooser.askcolor(title="Choose Font Color")
        if color[1]:
            self.font_color = tuple(map(int, color[0]))

    def choose_box_color(self):
        color = colorchooser.askcolor(title="Choose Box Color")
        if color[1]:
            self.box_color = tuple(map(int, color[0]))

    def choose_input_folder(self):
        self.input_folder = filedialog.askdirectory(title="Select Input Folder")

    def choose_output_folder(self):
        self.output_folder = filedialog.askdirectory(title="Select Output Folder")

    def preview_image(self):
        if not self.input_folder:
            messagebox.showerror("Error", "Please select an input folder first.")
            return

        for filename in os.listdir(self.input_folder):
            if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                image_path = os.path.join(self.input_folder, filename)
                break
        else:
            messagebox.showerror("Error", "No images found in the input folder.")
            return

        temp_output_path = os.path.join(self.input_folder, "temp_preview.png")

        add_calendar(
            image_path, temp_output_path, self.font_var.get(), self.font_size_var.get(),
            self.font_color, self.box_color, self.transparency_var.get(),
            self.curvature_var.get(), self.table_size_var.get(),
            self.x_offset_var.get(), self.y_offset_var.get()
        )

        preview_img = Image.open(temp_output_path)
        preview_img.thumbnail((500, 500))
        preview_img = ImageTk.PhotoImage(preview_img)

        if hasattr(self, 'preview_label'):
            self.preview_label.config(image=preview_img)
            self.preview_label.image = preview_img
        else:
            self.preview_label = ttk.Label(self.master, image=preview_img)
            self.preview_label.image = preview_img
            self.preview_label.grid(row=13, column=0, columnspan=2, pady=10)

    def process_images(self):
        if not self.input_folder or not self.output_folder:
            messagebox.showerror("Error", "Please select both input and output folders.")
            return

        process_folder(
            self.input_folder, self.output_folder, self.font_var.get(),
            self.font_size_var.get(), self.font_color, self.box_color,
            self.transparency_var.get(), self.curvature_var.get(),
            self.table_size_var.get(), self.x_offset_var.get(), self.y_offset_var.get()
        )
        messagebox.showinfo("Success", "Images processed successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()