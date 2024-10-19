# Tapezieren V1.1 - README

Tapezieren V1.1 is a Python-based desktop application that allows you to add customizable calendars to your images. Using an intuitive GUI built with Tkinter, the app helps you design and overlay monthly calendars with various font styles, colors, and layout options. The images are processed in batches, making it easy to apply the same design across multiple files.

## Features
- **Custom Font Support**: Select from available system fonts and apply styles like bold, italic, and hollow.
- **Color Customization**: Customize the font color, box background, weekday color, holiday color, and day name color.
- **Layout Control**: Adjust transparency, curvature of the calendar box, table size, and offsets for precise placement on your image.
- **Preview Functionality**: Instantly preview how the calendar will look on the image before processing.
- **Batch Processing**: Apply the calendar design to multiple images at once by selecting an input folder.
- **Supports Common Image Formats**: Works with PNG, JPG, and JPEG images.

## Installation

1. **Clone the repository**:
   ```
   git clone https://github.com/supertaez/tapezieren.git
   cd tapezieren
   ```

2. **Install dependencies**:
   You will need Python 3 and the following libraries:
   ```bash
   pip install Pillow matplotlib
   ```

3. **Run the application**:
   ```bash
   python tapezieren.py
   ```

## Usage

1. **Font Settings**: Choose the font from the dropdown and optionally apply bold, italic, or hollow styles.
2. **Date Settings**: Select the month and year for the calendar you want to overlay.
3. **Color Settings**: Customize the colors for different parts of the calendar.
4. **Layout Settings**: Adjust sliders for transparency, box curvature, table size, and position offsets.
5. **Select Folders**:
   - Input Folder: Choose a folder containing images to which you want to add the calendar.
   - Output Folder: Choose where the processed images should be saved.
6. **Preview**: Preview the changes by cycling through the images with the **Next Preview Image** button.
7. **Process**: Once satisfied, click the **Process All Images** button to apply the calendar to all images in the input folder.

## GUI Screenshots

![Screenshot 2024-10-19](https://github.com/user-attachments/assets/4405841c-27d7-4e8c-8244-1446e09b5580)


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

Feel free to customize and extend this README to suit your needs or repository style!
