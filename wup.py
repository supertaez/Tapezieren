import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import os
from datetime import datetime
import calendar
import matplotlib.font_manager as fm

# Set Sunday as the first day of the week
calendar.setfirstweekday(6)


def get_monospaced_fonts():
    monospaced_fonts = []
    all_fonts = fm.findSystemFonts()
    print(f"Total fonts found: {len(all_fonts)}")
    for font in all_fonts:
        try:
            with ImageFont.truetype(font, 12) as pil_font:
                widths = [pil_font.getbbox(char)[2] for char in 'il1']
                if len(set(widths)) == 1:  # All characters have the same width
                    monospaced_fonts.append(font)
        except Exception as e:
            print(f"Error processing font {font}: {e}")
    print(f"Monospaced fonts found: {len(monospaced_fonts)}")
    return sorted(set(monospaced_fonts))


def add_calendar(image_path, output_path, font_path, font_size, font_color, box_color=(0, 0, 0, 128)):
    try:
        with Image.open(image_path).convert("RGBA") as img:
            draw = ImageDraw.Draw(img)

            # Calculate relative font size based on image resolution
            base_resolution = 1000  # Base resolution for font size calculation
            relative_font_size = int(font_size * (max(img.size) / base_resolution))

            try:
                font = ImageFont.truetype(font_path, relative_font_size)
            except IOError:
                print(f"Failed to load font {font_path}. Using default font.")
                font = ImageFont.load_default()

            now = datetime.now()
            year = now.year
            month = now.month

            cal = calendar.monthcalendar(year, month)
            month_name = calendar.month_name[month]
            cal_text = f"{month_name} {year}\n"
            cal_text += "Su Mo Tu We Th Fr Sa\n"
            for week in cal:
                cal_text += " ".join(f"{day:2}" if day != 0 else "  " for day in week) + "\n"

            calendar_lines = cal_text.split('\n')

            line_height = draw.textbbox((0, 0), "A", font=font)[3]
            total_height = line_height * len(calendar_lines)
            max_line_width = max(draw.textbbox((0, 0), line, font=font)[2] for line in calendar_lines)

            # Calculate position for right-hand side, center alignment
            margin = int(0.05 * min(img.size))  # 5% of the smaller dimension as margin
            text_x = img.size[0] - max_line_width - margin
            text_y = (img.size[1] - total_height) // 2  # Vertically centered

            box_padding = int(0.02 * min(img.size))  # 2% of the smaller dimension as padding
            box_x1 = text_x - box_padding
            box_y1 = text_y - box_padding
            box_x2 = img.size[0] - margin + box_padding
            box_y2 = text_y + total_height + box_padding

            box_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
            box_draw = ImageDraw.Draw(box_img)
            box_draw.rectangle([box_x1, box_y1, box_x2, box_y2], fill=box_color)

            img = Image.alpha_composite(img, box_img)
            draw = ImageDraw.Draw(img)

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


def process_folder(folder_path, output_folder, font_path, font_size, font_color, box_color=(0, 0, 0, 128)):
    if not os.path.exists(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(folder_path):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            image_path = os.path.join(folder_path, filename)
            output_path = os.path.join(output_folder, f"calendar_{filename}")
            add_calendar(image_path, output_path, font_path, font_size, font_color, box_color)


class CalendarGUI:
    def __init__(self, master):
        self.master = master
        master.title("Calendar Image Processor")

        self.fonts = get_monospaced_fonts()
        if not self.fonts:
            print("No monospaced fonts detected. Adding fallback options.")
            self.fonts = ["Courier", "Consolas", "Monospace"]

        ttk.Label(master, text="Select Font:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.font_var = tk.StringVar(master)
        self.font_dropdown = ttk.Combobox(master, textvariable=self.font_var, values=self.fonts)
        self.font_dropdown.grid(row=0, column=1, padx=5, pady=5)
        self.font_dropdown.set(self.fonts[0] if self.fonts else "")

        ttk.Label(master, text="Font Size:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.font_size_var = tk.IntVar(master, value=40)
        self.font_size_entry = ttk.Entry(master, textvariable=self.font_size_var)
        self.font_size_entry.grid(row=1, column=1, padx=5, pady=5)

        self.color_button = ttk.Button(master, text="Choose Font Color", command=self.choose_color)
        self.color_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.input_folder_button = ttk.Button(master, text="Select Input Folder", command=self.choose_input_folder)
        self.input_folder_button.grid(row=3, column=0, columnspan=2, pady=5)

        self.output_folder_button = ttk.Button(master, text="Select Output Folder", command=self.choose_output_folder)
        self.output_folder_button.grid(row=4, column=0, columnspan=2, pady=5)

        self.process_button = ttk.Button(master, text="Process Images", command=self.process_images)
        self.process_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.font_color = (255, 255, 255)  # Default to white
        self.input_folder = ""
        self.output_folder = ""

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Font Color")
        if color[1]:
            self.font_color = tuple(map(int, color[0]))

    def choose_input_folder(self):
        self.input_folder = filedialog.askdirectory(title="Select Input Folder")

    def choose_output_folder(self):
        self.output_folder = filedialog.askdirectory(title="Select Output Folder")

    def process_images(self):
        if not self.input_folder or not self.output_folder:
            tk.messagebox.showerror("Error", "Please select both input and output folders.")
            return

        selected_font = self.font_var.get()
        font_path = selected_font
        if not os.path.isfile(font_path):
            print(f"Font file not found: {font_path}")
            print("Trying to find the font in the system...")
            try:
                font_path = fm.findfont(fm.FontProperties(family=selected_font))
                print(f"Found font path: {font_path}")
            except:
                print(f"Could not find font: {selected_font}")
                tk.messagebox.showerror("Error", f"Could not find font: {selected_font}. Using default font.")
                font_path = ImageFont.load_default().path

        font_size = self.font_size_var.get()

        process_folder(self.input_folder, self.output_folder, font_path, font_size, self.font_color)
        tk.messagebox.showinfo("Success", "Images processed successfully!")


if __name__ == "__main__":
    root = tk.Tk()
    gui = CalendarGUI(root)
    root.mainloop()