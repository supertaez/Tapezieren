import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import os
from datetime import datetime
import calendar
import matplotlib.font_manager as fm

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

def get_font(font_name, font_size, bold=False, italic=False):
    try:
        for font_path in fm.findSystemFonts():
            try:
                font_prop = fm.FontProperties(fname=font_path)
                if (font_prop.get_name() == font_name and
                        font_prop.get_weight() == ('bold' if bold else 'normal') and
                        font_prop.get_style() == ('italic' if italic else 'normal')):
                    return ImageFont.truetype(font_path, font_size)
            except IOError:
                continue
        # If exact match not found, try to find any variant of the font
        for font_path in fm.findSystemFonts():
            try:
                if fm.FontProperties(fname=font_path).get_name() == font_name:
                    return ImageFont.truetype(font_path, font_size)
            except IOError:
                continue
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()

def add_calendar(image_path, output_path, font_name, font_color, box_color, weekday_color,
                 holiday_color, day_name_color, transparency, curvature, table_size, x_offset, y_offset,
                 selected_month, selected_year, bold=False, italic=False, hollow=False):
    try:
        with Image.open(image_path).convert("RGBA") as img:
            overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            img_width, img_height = img.size
            base_size = min(img_width, img_height)
            cell_width = int(base_size / 7 * table_size)
            cell_height = int(base_size / 8 * table_size)
            margin = int(0.02 * base_size * table_size)

            font_size = int(base_size * table_size / 20)  # Adjust font size based on table size
            regular_font = get_font(font_name, font_size, bold, italic)
            day_name_font = get_font(font_name, int(font_size * 0.9), bold, italic)
            month_font = get_font(font_name, int(font_size * 1.1), bold, italic)

            cal = calendar.monthcalendar(selected_year, selected_month)
            month_name = calendar.month_name[selected_month]

            x_start = int(x_offset * (img_width - cell_width * 7))
            y_start = int(y_offset * (img_height - (cell_height * (len(cal) + 1) + 2 * margin)))

            title_text = f"{month_name} {selected_year}"
            title_bbox = draw.textbbox((0, 0), title_text, font=month_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_height = title_bbox[3] - title_bbox[1]
            title_x = x_start + (cell_width * 7 - title_width) // 2
            title_y = y_start + margin

            # Draw background box
            box_color_with_alpha = (*box_color[:3], int(255 * transparency))
            calendar_width = cell_width * 7 + 2 * margin
            calendar_height = cell_height * (len(cal) + 1) + 2 * margin + title_height
            draw.rounded_rectangle(
                [(x_start, y_start), (x_start + calendar_width, y_start + calendar_height)],
                radius=int(curvature * base_size / 100), fill=box_color_with_alpha
            )

            # Draw month name
            if hollow:
                draw.text((title_x, title_y), title_text, font=month_font, stroke_width=2,
                          stroke_fill=font_color, fill=None)
            else:
                draw.text((title_x, title_y), title_text, font=month_font, fill=font_color)

            # Draw day names
            days = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
            for i, day in enumerate(days):
                x = x_start + i * cell_width + margin
                y = y_start + title_height + 2 * margin
                day_bbox = draw.textbbox((0, 0), day, font=day_name_font)
                day_width = day_bbox[2] - day_bbox[0]
                day_height = day_bbox[3] - day_bbox[1]
                day_x = x + (cell_width - day_width) // 2
                day_y = y + (cell_height - day_height) // 2
                if hollow:
                    draw.text((day_x, day_y), day, font=day_name_font, stroke_width=2,
                              stroke_fill=day_name_color, fill=None)
                else:
                    draw.text((day_x, day_y), day, font=day_name_font, fill=day_name_color)

            # Draw dates
            for week_index, week in enumerate(cal):
                for day_index, day in enumerate(week):
                    if day != 0:
                        x = x_start + day_index * cell_width + margin
                        y = y_start + (week_index + 1) * cell_height + title_height + 2 * margin

                        date_text = str(day)
                        date_bbox = draw.textbbox((0, 0), date_text, font=regular_font)
                        date_width = date_bbox[2] - date_bbox[0]
                        date_height = date_bbox[3] - date_bbox[1]
                        date_x = x + (cell_width - date_width) // 2
                        date_y = y + (cell_height - date_height) // 2

                        # Choose color based on whether it's a holiday (weekend)
                        color = holiday_color if day_index in [5, 6] else weekday_color

                        if hollow:
                            draw.text((date_x, date_y), date_text, font=regular_font,
                                      stroke_width=2, stroke_fill=color, fill=None)
                        else:
                            draw.text((date_x, date_y), date_text, font=regular_font, fill=color)

            img = Image.alpha_composite(img, overlay)
            if output_path.lower().endswith((".jpg", ".jpeg")):
                img = img.convert("RGB")
            img.save(output_path)
            return True
    except Exception as e:
        print(f"Failed to process {image_path}: {e}")
        return False

class CalendarApp:
    def __init__(self, master):
        self.master = master
        master.title("Tapezieren V1.1")

        self.fonts = get_available_fonts()
        if not self.fonts:
            self.fonts = ["default"]

        self.setup_variables()
        self.create_gui_elements()
        self.image_paths = []
        self.current_image_index = 0

        # Bind all variable changes to update_preview
        self.bind_variables()

    def setup_variables(self):
        self.font_var = tk.StringVar(self.master)
        self.transparency_var = tk.DoubleVar(self.master, value=0.5)
        self.curvature_var = tk.DoubleVar(self.master, value=20)
        self.table_size_var = tk.DoubleVar(self.master, value=1.0)
        self.x_offset_var = tk.DoubleVar(self.master, value=0.5)
        self.y_offset_var = tk.DoubleVar(self.master, value=0.5)

        current_date = datetime.now()
        self.month_var = tk.IntVar(self.master, value=current_date.month)
        self.year_var = tk.IntVar(self.master, value=current_date.year)

        self.bold_var = tk.BooleanVar(self.master, value=False)
        self.italic_var = tk.BooleanVar(self.master, value=False)
        self.hollow_var = tk.BooleanVar(self.master, value=False)

        self.font_color = (255, 255, 255)
        self.box_color = (0, 0, 0)
        self.weekday_color = (200, 200, 200)
        self.holiday_color = (255, 100, 100)
        self.day_name_color = (150, 150, 150)

        self.input_folder = ""
        self.output_folder = ""

    def create_gui_elements(self):
        # Create two main frames - left for controls, right for preview
        left_frame = ttk.Frame(self.master)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        right_frame = ttk.Frame(self.master)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Configure grid weights
        self.master.grid_columnconfigure(1, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

        current_row = 0

        # Font settings
        font_frame = ttk.LabelFrame(left_frame, text="Font Settings")
        font_frame.grid(row=current_row, column=0, padx=5, pady=5, sticky="ew")
        current_row += 1

        ttk.Label(font_frame, text="Font:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        font_dropdown = ttk.Combobox(font_frame, textvariable=self.font_var, values=self.fonts)
        font_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        font_dropdown.set(self.fonts[0])

        # Font style checkboxes
        style_frame = ttk.Frame(font_frame)
        style_frame.grid(row=1, column=0, columnspan=2, pady=5)

        ttk.Checkbutton(style_frame, text="Bold", variable=self.bold_var).pack(side=tk.LEFT)
        ttk.Checkbutton(style_frame, text="Italic", variable=self.italic_var).pack(side=tk.LEFT)
        ttk.Checkbutton(style_frame, text="Hollow", variable=self.hollow_var).pack(side=tk.LEFT)

        # Date settings
        date_frame = ttk.LabelFrame(left_frame, text="Date Settings")
        date_frame.grid(row=current_row, column=0, padx=5, pady=5, sticky="ew")
        current_row += 1

        months = list(calendar.month_name)[1:]
        ttk.Label(date_frame, text="Month:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        month_dropdown = ttk.Combobox(date_frame, values=months)
        month_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        month_dropdown.set(months[self.month_var.get() - 1])
        month_dropdown.bind('<<ComboboxSelected>>',
                            lambda e: self.month_var.set(months.index(month_dropdown.get()) + 1))

        ttk.Label(date_frame, text="Year:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        year_spinbox = ttk.Spinbox(date_frame, from_=1900, to=2100, textvariable=self.year_var)
        year_spinbox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Color settings
        color_frame = ttk.LabelFrame(left_frame, text="Color Settings")
        color_frame.grid(row=current_row, column=0, padx=5, pady=5, sticky="ew")
        current_row += 1

        color_grid = ttk.Frame(color_frame)
        color_grid.grid(row=0, column=0, padx=5, pady=5)

        ttk.Button(color_grid, text="Box Color",
                   command=self.choose_box_color).grid(row=0, column=0, padx=2, pady=2)
        ttk.Button(color_grid, text="Month Name Color",
                   command=self.choose_font_color).grid(row=0, column=1, padx=2, pady=2)
        ttk.Button(color_grid, text="Weekday Color",
                   command=self.choose_weekday_color).grid(row=1, column=0, padx=2, pady=2)
        ttk.Button(color_grid, text="Holiday Color",
                   command=self.choose_holiday_color).grid(row=1, column=1, padx=2, pady=2)
        ttk.Button(color_grid, text="Day Names Color",
                   command=self.choose_day_name_color).grid(row=2, column=0, columnspan=2, padx=2, pady=2)

        # Slider settings
        slider_frame = ttk.LabelFrame(left_frame, text="Layout Settings")
        slider_frame.grid(row=current_row, column=0, padx=5, pady=5, sticky="ew")
        current_row += 1

        self.create_slider(slider_frame, "Transparency", 0, self.transparency_var, 0, 1)
        self.create_slider(slider_frame, "Curvature", 1, self.curvature_var, 0, 100)
        self.create_slider(slider_frame, "Table Size", 2, self.table_size_var, 0.1, 2.0)
        self.create_slider(slider_frame, "X Offset", 3, self.x_offset_var, 0, 1)
        self.create_slider(slider_frame, "Y Offset", 4, self.y_offset_var, 0, 1)

        # Folder selection and processing
        folder_frame = ttk.LabelFrame(left_frame, text="Folder Settings")
        folder_frame.grid(row=current_row, column=0, padx=5, pady=5, sticky="ew")
        current_row += 1

        ttk.Button(folder_frame, text="Select Input Folder",
                   command=self.choose_input_folder).grid(row=0, column=0, padx=5, pady=5)
        ttk.Button(folder_frame, text="Select Output Folder",
                   command=self.choose_output_folder).grid(row=0, column=1, padx=5, pady=5)

        # Preview and Process buttons
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=current_row, column=0, padx=5, pady=5, sticky="ew")
        current_row += 1

        self.preview_button = ttk.Button(button_frame, text="Next Preview Image",
                                         command=self.next_preview_image)
        self.preview_button.grid(row=0, column=0, padx=5, pady=10)

        self.process_button = ttk.Button(button_frame, text="Process All Images",
                                         command=self.process_images)
        self.process_button.grid(row=0, column=1, padx=5, pady=10)

        # Processing status
        self.status_label = ttk.Label(left_frame, text="")
        self.status_label.grid(row=current_row, column=0, padx=5, pady=5, sticky="ew")
        current_row += 1

        # Preview area - now on the right side
        preview_frame = ttk.LabelFrame(right_frame, text="Preview")
        preview_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.grid(row=0, column=0, padx=5, pady=5)

        # Configure preview frame to expand
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

    def create_slider(self, parent, text, row, variable, min_val, max_val):
        ttk.Label(parent, text=f"{text}:").grid(row=row, column=0, sticky="w", padx=5, pady=5)
        slider = ttk.Scale(parent, from_=min_val, to=max_val, orient="horizontal", variable=variable)
        slider.grid(row=row, column=1, padx=5, pady=5, sticky="ew")
        return slider

    def bind_variables(self):
        # Bind all variables to update_preview
        self.font_var.trace_add("write", lambda *args: self.schedule_preview_update())
        self.transparency_var.trace_add("write", lambda *args: self.schedule_preview_update())
        self.curvature_var.trace_add("write", lambda *args: self.schedule_preview_update())
        self.table_size_var.trace_add("write", lambda *args: self.schedule_preview_update())
        self.x_offset_var.trace_add("write", lambda *args: self.schedule_preview_update())
        self.y_offset_var.trace_add("write", lambda *args: self.schedule_preview_update())
        self.month_var.trace_add("write", lambda *args: self.schedule_preview_update())
        self.year_var.trace_add("write", lambda *args: self.schedule_preview_update())
        self.bold_var.trace_add("write", lambda *args: self.schedule_preview_update())
        self.italic_var.trace_add("write", lambda *args: self.schedule_preview_update())
        self.hollow_var.trace_add("write", lambda *args: self.schedule_preview_update())

    def schedule_preview_update(self):
        # Cancel any existing scheduled update
        if hasattr(self, '_schedule_id'):
            self.master.after_cancel(self._schedule_id)
        # Schedule new update in 100ms
        self._schedule_id = self.master.after(100, self.update_preview)

    def choose_color(self, title, callback):
        color = colorchooser.askcolor(title=title)
        if color[1]:
            callback(tuple(map(int, color[0])))
            self.schedule_preview_update()

    def choose_font_color(self):
        self.choose_color("Choose Month Name Color", lambda c: setattr(self, 'font_color', c))

    def choose_box_color(self):
        self.choose_color("Choose Box Color", lambda c: setattr(self, 'box_color', c))

    def choose_weekday_color(self):
        self.choose_color("Choose Weekday Color", lambda c: setattr(self, 'weekday_color', c))

    def choose_holiday_color(self):
        self.choose_color("Choose Holiday Color", lambda c: setattr(self, 'holiday_color', c))

    def choose_day_name_color(self):
        self.choose_color("Choose Day Names Color", lambda c: setattr(self, 'day_name_color', c))

    def choose_input_folder(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_folder = folder
            self.image_paths = [
                os.path.join(folder, f) for f in os.listdir(folder)
                if f.lower().endswith(('.png', '.jpg', '.jpeg'))
            ]
            if self.image_paths:
                self.current_image_index = 0
                self.update_preview()
            else:
                messagebox.showerror("Error", "No valid images found in the selected folder.")

    def choose_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder = folder

    def next_preview_image(self):
        if self.image_paths:
            self.current_image_index = (self.current_image_index + 1) % len(self.image_paths)
            self.update_preview()

    def update_preview(self):
        if not self.image_paths:
            return

        temp_output_path = os.path.join(os.path.dirname(self.image_paths[0]), "temp_preview.png")

        success = add_calendar(
            self.image_paths[self.current_image_index],
            temp_output_path,
            self.font_var.get(),
            self.font_color,
            self.box_color,
            self.weekday_color,
            self.holiday_color,
            self.day_name_color,
            self.transparency_var.get(),
            self.curvature_var.get(),
            self.table_size_var.get(),
            self.x_offset_var.get(),
            self.y_offset_var.get(),
            self.month_var.get(),
            self.year_var.get(),
            self.bold_var.get(),
            self.italic_var.get(),
            self.hollow_var.get()
        )

        if success:
            preview_img = Image.open(temp_output_path)
            # Calculate aspect ratio for resizing
            width, height = preview_img.size
            max_size = (600, 800)  # Increased preview size
            ratio = min(max_size[0] / width, max_size[1] / height)
            new_size = (int(width * ratio), int(height * ratio))
            preview_img = preview_img.resize(new_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(preview_img)

            self.preview_label.configure(image=photo)
            self.preview_label.image = photo  # Keep a reference!

            try:
                os.remove(temp_output_path)
            except:
                pass

    def process_images(self):
        if not self.input_folder or not self.output_folder:
            messagebox.showerror("Error", "Please select both input and output folders.")
            return

        total_images = len(self.image_paths)
        for index, image_path in enumerate(self.image_paths, start=1):
            self.status_label.config(text=f"Processing {index} of {total_images} images")
            self.master.update()

            output_filename = f"calendar_{os.path.basename(image_path)}"
            output_path = os.path.join(self.output_folder, output_filename)

            success = add_calendar(
                image_path,
                output_path,
                self.font_var.get(),
                self.font_color,
                self.box_color,
                self.weekday_color,
                self.holiday_color,
                self.day_name_color,
                self.transparency_var.get(),
                self.curvature_var.get(),
                self.table_size_var.get(),
                self.x_offset_var.get(),
                self.y_offset_var.get(),
                self.month_var.get(),
                self.year_var.get(),
                self.bold_var.get(),
                self.italic_var.get(),
                self.hollow_var.get()
            )

            if not success:
                messagebox.showerror("Error", f"Failed to process {os.path.basename(image_path)}")
                self.status_label.config(text="")
                return

        self.status_label.config(text=f"Processed {total_images} images")

if __name__ == "__main__":
    root = tk.Tk()
    app = CalendarApp(root)
    root.mainloop()