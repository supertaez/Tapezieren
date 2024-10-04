# Tapezieren

Tapezieren is a Python application that allows users to add customizable calendar overlays to images. The name "Tapezieren" comes from the German word for "wallpapering," reflecting its primary use in creating themed wallpapers with calendar information.

## Features

- User-friendly graphical interface
- Customizable calendar styles
- Live preview of calendar overlay
- Batch processing of images
- Support for various image formats (PNG, JPG, JPEG)
- Adjustable font, colors, transparency, and corner radius
- Predefined styles for quick customization

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7 or higher
- pip (Python package installer)

## Installation

Follow these steps to install Tapezieren:

1. Clone this repository or download the source code:
   ```
   git clone https://github.com/supertaez/Tapezieren.git
   ```

2. Navigate to the project directory:
   ```
   cd Tapezieren
   ```

3. Install the required dependencies:
   ```
   pip install pillow matplotlib
   ```

## Usage

To run Tapezieren:

1. Open a terminal or command prompt.
2. Navigate to the project directory.
3. Run the following command:
   ```
   python Tapezieren.py
   ```
4. The graphical user interface (GUI) will appear.

To add calendar overlays to your images:

1. Select a font from the dropdown menu.
2. Choose a font size.
3. Pick a predefined style or customize your own.
4. Adjust the font color, box color, transparency, and corner radius as desired.
5. Click "Select Input Folder" and choose the folder containing your images.
6. Click "Select Output Folder" to specify where the processed images should be saved.
7. Click "Update Preview" to see how your calendar overlay will look.
8. Once satisfied with the preview, click "Process Images" to apply the overlay to all images in the input folder.

## Customization Options

- **Font**: Choose from available monospaced fonts on your system.
- **Font Size**: Adjust the size of the calendar text.
- **Style**: Select from predefined styles (Classic, Modern, Pastel) or create your own.
- **Font Color**: Customize the color of the calendar text.
- **Box Color**: Change the color of the background box behind the calendar.
- **Box Transparency**: Adjust the opacity of the background box.
- **Corner Radius**: Round the corners of the background box.

## Contributing

Contributions to Tapezieren are welcome! Here's how you can contribute:

1. Fork the repository.
2. Create a new branch: `git checkout -b feature-branch-name`.
3. Make your changes and commit them: `git commit -m 'Add some feature'`.
4. Push to the original branch: `git push origin feature-branch-name`.
5. Create the pull request.

Alternatively, see the GitHub documentation on [creating a pull request](https://help.github.com/articles/creating-a-pull-request/).

## License

This project is open source and available under the [MIT License](LICENSE).
