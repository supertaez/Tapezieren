import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
from datetime import datetime
import calendar
import matplotlib.font_manager as fm
from io import BytesIO


class CalendarStyle:
    def __init__(self, name, box_color, box_alpha, corner_radius, font_color):
        self.name = name
        self.box_color = box_color
        self.box_alpha = box_alpha
        self.corner_radius = corner_radius
        self.font_color = font_color


class CalendarGUI:
    def __init__(self, master):
        self.master = master
        master.title("Tapezieren - Enhanced Calendar Overlay")

        self.fonts = get_monospaced_fonts()
        if not self.fonts:
            print("No monospaced fonts detected. Adding fallback options.")
            self.fonts = ["Consolas", "Monospace"]

        self.styles = [
            CalendarStyle("Classic", (0, 0, 0), 128, 0, (255, 255, 255)),
            CalendarStyle("Modern", (255, 255, 255), 200, 20, (0, 0, 0)),
            CalendarStyle("Pastel", (255, 230, 230), 180, 15, (100, 100, 100)),
        ]

        self.create_widgets()

        self.input_folder = ""
        self.output_folder = ""

    def create_widgets(self):
        # Font selection
        ttk.Label(self.master, text="Select Font:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.font_var = tk.StringVar(self.master)
        self.font_dropdown = ttk.Combobox(self.master, textvariable=self.font_var, values=self.fonts)
        self.font_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.font_dropdown.set(self.fonts[0] if self.fonts else "")

        # Font size
        ttk.Label(self.master, text="Font Size:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.font_size_var = tk.IntVar(self.master, value=40)
        self.font_size_entry = ttk.Entry(self.master, textvariable=self.font_size_var)
        self.font_size_entry.grid(row=1, column=1, padx=5, pady=5)

        # Style selection
        ttk.Label(self.master, text="Select Style:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.style_var = tk.StringVar(self.master)
        self.style_dropdown = ttk.Combobox(self.master, textvariable=self.style_var,
                                           values=[style.name for style in self.styles])
        self.style_dropdown.grid(row=2, column=1, padx=5, pady=5)
        self.style_dropdown.set(self.styles[0].name)
        self.style_dropdown.bind("<<ComboboxSelected>>", self.update_preview)

        # Custom color options
        self.color_button = ttk.Button(self.master, text="Choose Font Color", command=self.choose_color)
        self.color_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.box_color_button = ttk.Button(self.master, text="Choose Box Color", command=self.choose_box_color)
        self.box_color_button.grid(row=4, column=0, columnspan=2, pady=5)

        # Box transparency
        ttk.Label(self.master, text="Box Transparency:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.transparency_var = tk.IntVar(self.master, value=128)
        self.transparency_scale = ttk.Scale(self.master, from_=0, to=255, variable=self.transparency_var,
                                            orient=tk.HORIZONTAL)
        self.transparency_scale.grid(row=5, column=1, padx=5, pady=5)
        self.transparency_scale.bind("<ButtonRelease-1>", self.update_preview)

        # Corner radius
        ttk.Label(self.master, text="Corner Radius:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.corner_radius_var = tk.IntVar(self.master, value=0)
        self.corner_radius_scale = ttk.Scale(self.master, from_=0, to=50, variable=self.corner_radius_var,
                                             orient=tk.HORIZONTAL)
        self.corner_radius_scale.grid(row=6, column=1, padx=5, pady=5)
        self.corner_radius_scale.bind("<ButtonRelease-1>", self.update_preview)

        # Folder selection
        self.input_folder_button = ttk.Button(self.master, text="Select Input Folder", command=self.choose_input_folder)
        self.input_folder_button.grid(row=7, column=0, columnspan=2, pady=5)

        self.output_folder_button = ttk.Button(self.master, text="Select Output Folder",
                                               command=self.choose_output_folder)
        self.output_folder_button.grid(row=8, column=0, columnspan=2, pady=5)

        # Preview
        self.preview_button = ttk.Button(self.master, text="Update Preview", command=self.update_preview)
        self.preview_button.grid(row=9, column=0, columnspan=2, pady=5)

        self.preview_canvas = tk.Canvas(self.master, width=300, height=200)
        self.preview_canvas.grid(row=10, column=0, columnspan=2, padx=5, pady=5)

        # Process button
        self.process_button = ttk.Button(self.master, text="Process Images", command=self.process_images)
        self.process_button.grid(row=11, column=0, columnspan=2, pady=10)

        self.font_color = (255, 255, 255)
        self.box_color = (0, 0, 0)

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Font Color")
        if color[1]:
            self.font_color = tuple(map(int, color[0]))
            self.update_preview()

    def choose_box_color(self):
        color = colorchooser.askcolor(title="Choose Box Color")
        if color[1]:
            self.box_color = tuple(map(int, color[0]))
            self.update_preview()

    def choose_input_folder(self):
        self.input_folder = filedialog.askdirectory(title="Select Input Folder")
        self.update_preview()

    def choose_output_folder(self):
        self.output_folder = filedialog.askdirectory(title="Select Output Folder")

    def update_preview(self, event=None):
        if not self.input_folder:
            messagebox.showwarning("Warning", "Please select an input folder first.")
            return

        image_files = [f for f in os.listdir(self.input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not image_files:
            messagebox.showwarning("Warning", "No image files found in the input folder.")
            return

        sample_image_path = os.path.join(self.input_folder, image_files[0])

        style = next((s for s in self.styles if s.name == self.style_var.get()), self.styles[0])

        preview_image = self.create_preview(sample_image_path, style)
        self.display_preview(preview_image)

    def create_preview(self, image_path, style):
        with Image.open(image_path).convert("RGBA") as img:
            img.thumbnail((300, 200))
            draw = ImageDraw.Draw(img)

            font_path = self.get_font_path()
            font_size = self.font_size_var.get()
            font = ImageFont.truetype(font_path, font_size)

            cal_text = self.generate_calendar_text()

            box_color = self.box_color + (self.transparency_var.get(),)
            corner_radius = self.corner_radius_var.get()

            self.draw_rounded_rectangle(draw, (10, 10, img.width - 10, img.height - 10), box_color, corner_radius)

            draw.text((20, 20), cal_text, font=font, fill=self.font_color)

        return img

    def display_preview(self, image):
        photo = ImageTk.PhotoImage(image)
        self.preview_canvas.config(width=image.width, height=image.height)
        self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.preview_canvas.image = photo

    def get_font_path(self):
        selected_font = self.font_var.get()
        font_path = selected_font
        if not os.path.isfile(font_path):
            try:
                font_path = fm.findfont(fm.FontProperties(family=selected_font))
            except:
                font_path = ImageFont.load_default().path
        return font_path

    def generate_calendar_text(self):
        now = datetime.now()
        year, month = now.year, now.month
        cal = calendar.monthcalendar(year, month)
        month_name = calendar.month_name[month]
        cal_text = f"{month_name} {year}\n"
        cal_text += "Su Mo Tu We Th Fr Sa\n"
        for week in cal:
            cal_text += " ".join(f"{day:2}" if day != 0 else "  " for day in week) + "\n"
        return cal_text

    def draw_rounded_rectangle(self, draw, xy, fill, radius):
        x1, y1, x2, y2 = xy
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
        draw.pieslice([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=fill)
        draw.pieslice([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=fill)
        draw.pieslice([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=fill)
        draw.pieslice([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=fill)

    def process_images(self):
        if not self.input_folder or not self.output_folder:
            tk.messagebox.showerror("Error", "Please select both input and output folders.")
            return

        font_path = self.get_font_path()
        font_size = self.font_size_var.get()
        style = next((s for s in self.styles if s.name == self.style_var.get()), self.styles[0])

        box_color = self.box_color + (self.transparency_var.get(),)
        corner_radius = self.corner_radius_var.get()

        process_folder(self.input_folder, self.output_folder, font_path, font_size, self.font_color, box_color,
                       corner_radius)
        tk.messagebox.showinfo("Success", "Images processed successfully!")


def process_folder(folder_path, output_folder, font_path, font_size, font_color, box_color, corner_radius):
    if not os.path.exists(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(folder_path, filename)
            output_path = os.path.join(output_folder, f"calendar_{filename}")
            add_calendar(image_path, output_path, font_path, font_size, font_color, box_color, corner_radius)


def add_calendar(image_path, output_path, font_path, font_size, font_color, box_color, corner_radius):
    try:
        with Image.open(image_path).convert("RGBA") as img:
            draw = ImageDraw.Draw(img)

            base_resolution = 1000
            relative_font_size = int(font_size * (max(img.size) / base_resolution))

            try:
                font = ImageFont.truetype(font_path, relative_font_size)
            except IOError:
                print(f"Failed to load font {font_path}. Using default font.")
                font = ImageFont.load_default()

            cal_text = generate_calendar_text()

            calendar_lines = cal_text.split('\n')
            line_height = draw.textbbox((0, 0), "A", font=font)[3]
            total_height = line_height * len(calendar_lines)
            max_line_width = max(draw.textbbox((0, 0), line, font=font)[2] for line in calendar_lines)

            margin = int(0.05 * min(img.size))
            text_x = img.size[0] - max_line_width - margin
            text_y = (img.size[1] - total_height) // 2

            box_padding = int(0.02 * min(img.size))
            box_x1 = text_x - box_padding
            box_y1 = text_y - box_padding
            box_x2 = img.size[0] - margin + box_padding
            box_y2 = text_y + total_height + box_padding

            draw_rounded_rectangle(draw, (box_x1, box_y1, box_x2, box_y2), box_color, corner_radius)

            current_y = text_y
            for line in calendar_lines:
                draw.text((text_x, current_y), line, font=font, fill=font_color)
                current_y += line_height

            if output_path.lower().endswith((".jpg", ".jpeg")):
                img = img.convert("RGB")

            img.save(output_path)
            print(f"Saved output to {output_path}")
    except Exception as e:
        print(f"Failed to process {image_path}: {e}")


def generate_calendar_text():
    now = datetime.now()
    year, month = now.year, now.month
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    cal_text = f"{month_name} {year}\n"
    cal_text += "Su Mo Tu We Th Fr Sa\n"
    for week in cal:
        cal_text += " ".join(f"{day:2}" if day != 0 else "  " for day in week) + "\n"
    return cal_text

def draw_rounded_rectangle(draw, xy, fill, radius):
    x1, y1, x2, y2 = xy
    draw.rectangle([x1+radius, y1, x2-radius, y2], fill=fill)
    draw.rectangle([x1, y1+radius, x2, y2-radius], fill=fill)
    draw.pieslice([x1, y1, x1+radius*2, y1+radius*2], 180, 270, fill=fill)
    draw.pieslice([x2-radius*2, y1, x2, y1+radius*2], 270, 360, fill=fill)
    draw.pieslice([x1, y2-radius*2, x1+radius*2, y2], 90, 180, fill=fill)
    draw.pieslice([x2-radius*2, y2-radius*2, x2, y2], 0, 90, fill=fill)

def get_monospaced_fonts():
    monospaced_fonts = []
    all_fonts = fm.findSystemFonts()
    print(f"Total fonts found: {len(all_fonts)}")
    for font in all_fonts:
        try:
            with ImageFont.truetype(font, 12) as pil_font:
                widths = [pil_font.getbbox(char)[2] for char in 'il1']
                if len(set(widths)) == 1:
                    monospaced_fonts.append(font)
        except Exception as e:
            print(f"Error processing font {font}: {e}")
    print(f"Monospaced fonts found: {len(monospaced_fonts)}")
    return sorted(set(monospaced_fonts))

if __name__ == "__main__":
    root = tk.Tk()
    gui = CalendarGUI(root)
    root.mainloop()