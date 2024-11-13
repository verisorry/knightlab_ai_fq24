# Silvia Fang
# 11 Nov, 2024
# Python image standardiser for Knight Lab (FQ24) to crop images into a square and reformat

import face_recognition
from PIL import Image
import os, glob, shutil, time, argparse
from tqdm import tqdm

def resizer(img: Image, target_size: int) -> Image:
    """
    Resizes image's smallest side to target_size, maintaining aspect ratio

    :param Image img: Image object to be resized
    :param int target_size: Target size of resized image
    :return: The final resized Image object
    :rtype: Image
    """
    width, height = img.size

    # if the image is horizontally oriented, resize so height is target_size
    if width > height:
        new_height = target_size
        new_width = int((target_size / height) * width)
    # if the image is vertically oriented, resize so width is target_size
    else:
        new_width = target_size
        new_height = int((target_size / width) * height)
    return img.resize((new_width, new_height), Image.LANCZOS)

def cropper(img: Image, target_size: int) -> Image:
    """
    Crops image into a square of target_size, depending on image orientation

    :param Image img: Image object to be cropped
    :param int target_size: Target size of cropped image
    :return: The cropped Image object
    :rtype: Image
    """
    width, height = img.size

    # horizontal image, crop evenly from left and right
    if width > height:
        left = (width - target_size) // 2
        right = left + target_size
        return img.crop((left, 0, right, target_size))

    # vertical image, crop from x0, y0
    else:
        return img.crop((0, 0, target_size, target_size))

def face_cropper(image_path: str, target_size: int) -> Image:
    """
    Crops image into a square of target_size, centred on first recognised face

    :param str image_path: Path to image to be cropped
    :param int target_size: Target size of cropped image
    :return: The cropped Image object
    :rtype: Image
    """
    # Load the image using face_recognition
    image = face_recognition.load_image_file(image_path)

    # Detect faces in the image
    face_locations = face_recognition.face_locations(image)

    # if a face isn't detected, use normal cropping
    if not face_locations:
        print("No face detected in the image.")
        with Image.open(image_path) as img:
            return cropper(img, target_size)

    top, right, bottom, left = face_locations[0]

    # Calculate the center of the face
    face_center_x = (left + right) // 2
    face_center_y = (top + bottom) // 2

    # Pillow for cropping
    img = Image.open(image_path)
    if img.mode == 'P':
        img = img.convert('RGBA')

    # calculate crop bounds around centre of face
    img_width, img_height = img.size
    half = target_size // 2
    left = max(face_center_x - half, 0)
    top = max(face_center_y - half, 0)

    right = left + target_size
    bottom = top + target_size

    # if the centre of the face causes the crop bound to be outside the image bounds,
    # shift crop boundaries to fit into the image
    if right > img_width:
        right = img_width
        left = max(right - target_size, 0)
    if bottom > img_height:
        bottom = img_height
        top = max(bottom - target_size, 0)

    # Crop the image
    cropped_img = img.crop((left, top, right, bottom))
    return cropped_img

def copy_text_files(src_path: str, dest_path: str) -> None:
    """
    Copies all .txt files from source directory to output directory

    :param str src_path: Source directory path
    :param str dest_path: Output directory path
    :return: None
    """
    # Copy all .txt files to the new folder
    txt_files = glob.glob(os.path.join(src_path, '*.txt'))
    for file in tqdm(txt_files, desc="Copying label files", unit=" file"):
        shutil.copy2(file, dest_path)

def make_directory(dest_path: str) -> None:
    """
    Makes a new directory for output images

    :param str dest_path: Destination path at where to make directory
    :return: None
    """
    # delete existing directory at directory path if it already exists
    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)

    # try to make new directory for fixed images
    try:
        os.makedirs(dest_path, exist_ok=True)
        print(f"Destination directory created: {dest_path}")
    except PermissionError:
        print("Permission denied")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

def parse_arg() -> argparse.ArgumentParser.parse_args:
    """
    Parses command line arguments

    :return: Parsed arguments
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description='Image Parser to standardise images for training')
    parser.add_argument('input_folder',
                        help='Path to the folder containing images to process')

    # optional arguments
    # specify crop size
    parser.add_argument('--crop-size',
                        default=512, type=int,
                        help='Set the square image size, defaults to 512')
    # specify save format
    parser.add_argument('--format',
                        default='png', type=str,
                        choices=['png', 'jpg', 'jpeg'],
                        help='Output format for the image, defaults to png')
    # specify whether to skip labels or not
    parser.add_argument('--skip-labels',
                        action='store_true',
                        help='Whether to skip label copying, defaults to false')

    parser.add_argument('--facial-recognition',
                        action='store_true',
                        help='Facial recognition mode, defaults to false')

    args = parser.parse_args()
    return args

def main():
    args = parse_arg()

    src_path = args.input_folder
    target_size = args.crop_size
    if args.facial_recognition:
        dest_path = src_path + '_cleaned_facial_recognition'
    else:
        dest_path = src_path + '_cleaned'

    start_time = time.time()
    make_directory(dest_path)

    # don't skip labels if false
    if not args.skip_labels:
        copy_text_files(src_path, dest_path)
    else:
        print("Label copying skipped")

    # Process each image in the source directory
    image_files = [f for ext in ["jpg", "jpeg", "png", "webp", "bmp"] for f in glob.glob(src_path + f'/*.{ext}')]
    for item in tqdm(image_files, desc="Processing images", unit=" image"):
        with Image.open(item) as img:
            # if image is palette-based, convert to RGBA mode
            if img.mode == 'P':
                img = img.convert('RGBA')

            # if output format is not png, convert image to RGB mode as
            # transparency is not needed
            if args.format.lower() != 'png':
                img = img.convert('RGB')

            # Resizing
            resized_img = resizer(img, target_size)

            # Cropping
            if args.facial_recognition:
                temp_path = os.path.join(str(dest_path), str(os.path.splitext(os.path.basename(item))[0]) + f".{args.format}")
                resized_img.save(temp_path)
                cropped_img = face_cropper(temp_path, target_size)
            else:
                cropped_img = cropper(resized_img, target_size)

            # Saving as .png in the destination folder
            output_filename = os.path.splitext(os.path.basename(item))[0] + f".{args.format}"
            output_path = os.path.join(dest_path, output_filename)
            cropped_img.save(output_path)

    print("All operations complete! Elapsed time: %.2f s" % (time.time() - start_time))


if __name__ == "__main__":
    main()
