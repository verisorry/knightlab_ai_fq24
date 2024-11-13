# Knight Lab AI Editorial Model Training (FQ24)
A Python-based image preprocessing tool developed for Northwestern University's Knight Lab (FQ24) to standardise image dimensions and formats for LoRA training. The tool also offers facial recognition-based cropping to centre faces in each image where possible.

## Overview
This script processes a folder of images by:
1. **Resizing**: Adjusts images to a specified target size while maintaining aspect ratio
2. **Cropping**: Crops image into square dimensions, with two modes:
   - Standard Cropping: Crops based on image orientation:
     - Vertical Images: Cropped from the top (starting at `x0, y0`
     - Horizontal Images: Cropped evenly from the left and right edges
  - Facial Recognition Cropping: Centres cropping on the first detected face in each image
3. **Reformatting**: Saves images in the specified format (png, jpeg)
4. **Label Handling**: Copies accompanying `.txt` label files from the source directory to the output directory for each image

## Getting Started

### Prerequisites 
- Python version >= 3.12.0
- `Pillow` library for image manipulation
- `facial-recognition` library for face detection
- `tqdm` library for progress bar

## Usage
### Command-Line Arguments
This script takes the following arguments:
1. Positional Argument
   - `input_folder`: The path to the source folder containing images to process
2. Optional Arguments
   - `--crop-size`: Specifies the target size for square cropped images. Defaults to 512.
   - `--format`: Sets the output format for images (`png`, `jpg`, or `jpeg`). Defaults to `png`.
   - `--skip-labels`: Skips copying `.txt` label files if set
   - `--facial-recognition`: Enables facial recognition-based cropping if set
  
### Example Usage
1. Prepare your input image folder: create a folder containing images you want to process with corresponding labels in `.txt` format
2. Clone this repo and navigate to the project directory
   ```
   git clone https://github.com/knight-lab-ai/FQ24-image-parser.git
   cd /path/to/FQ24-image-parser
   ```
4. Install requirements:
   ```
   pip install -r requirements.txt
   ```
5. To run the script..
   a. with basic cropping mode:
   ```
   python3 image_parser.py /path/to/input_folder [--crop-size=512] [--format=png] [--skip-labels]
   ```
   b. with facial recognition cropping:
   ```
   python3 image_parser.py /path/to/input_folder --facial-recognition [--crop-size=512] [--format=png] [--skip-labels]
   ```
   c. (example) with facial recognition cropping, skipping copying label files:
   ```
   python3 image_parser.py /path/to/input_folder --skip-labels --facial-recognition
   ```
   d. (example) with basic cropping, with size 256x256 and of format jpg:
   ```
   python3 image_parser.py /path/to/input_folder --format=jpg --crop-size=256
   ```
6. Processed images are saved in a new folder named `<input_folder>_cleaned` or `<input_folder>_cleaned_facial_recognition` if `--facial-recognition` is enabled.

## Functions Overview
- `resizer(img, target_size)`: Resizes the image’s smallest side to `target_size` while maintaining aspect ratio.
- `cropper(img, target_size)`: Crops the image to a square of `target_size`, based on image orientation.
- `face_cropper(image_path, target_size)`: Centers the crop around the first detected face. If no face is detected, falls back to standard cropping.
- `copy_text_files(src_path, dest_path)`: Copies all `.txt` label files from the source directory to the destination directory.
- `make_directory(dest_path)`: Creates or refreshes the destination directory for processed images.
- `parse_arg()`: Parses command-line arguments.
