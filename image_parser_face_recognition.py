# Silvia Fang
# 11 Nov, 2024
# Python image parser with facial recognition capabilities for Knight Lab (FQ24)
# to crop images around faces into a 512x512 square and reformat to png

import glob, shutil, sys, os, face_recognition, time
from tqdm import tqdm
from image_parser import resizer, cropper
from PIL import Image

def face_cropper(image_path: str, target_size=512) -> Image:
    # Load the image using face_recognition
    image = face_recognition.load_image_file(image_path)

    # Detect faces in the image
    face_locations = face_recognition.face_locations(image)

    if not face_locations:
        # print("No face detected in the image.")
        with Image.open(image_path) as img:
            return cropper(img, 512)

    top, right, bottom, left = face_locations[0]

    # Calculate the center of the face
    face_center_x = (left + right) // 2
    face_center_y = (top + bottom) // 2

    # Pillow for cropping
    img = Image.open(image_path)
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    img_width, img_height = img.size
    left = max(face_center_x - target_size // 2, 0)
    top = max(face_center_y - target_size // 2, 0)
    right = min(left + target_size, img_width)
    bottom = min(top + target_size, img_height)

    # Crop the image
    cropped_img = img.crop((left, top, right, bottom))
    return cropped_img

def main():
    start_time = time.time()
    src_path = sys.argv[1]
    dest_path = src_path + '_cleaned_facial_recognition'
    target_size = int(sys.argv[2]) if len(sys.argv) == 3 else 512

    # Delete existing directory if it already exists
    if os.path.exists(dest_path):
        shutil.rmtree(dest_path)

    # Create new directory for cleaned images
    try:
        os.makedirs(dest_path, exist_ok=True)
        print(f"Destination directory created: {dest_path}")
    except PermissionError:
        print("Permission denied")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    # Copy all .txt files to new folder with progress bar
    txt_files = glob.glob(os.path.join(src_path, '*.txt'))
    for file in tqdm(txt_files, desc="Copying label files", unit=" file"):
        shutil.copy2(file, dest_path)

    # Process each image file in the source directory
    image_files = [f for ext in ["jpg", "jpeg", "png", "webp", "bmp"] for f in glob.glob(src_path + f'/*.{ext}')]
    for item in tqdm(image_files, desc="Processing images", unit=" image"):
        # Load and resize image
        with Image.open(item) as img:
            resized_img = resizer(img, target_size)

            # Save the resized image temporarily for face cropping
            temp_path = os.path.join(dest_path, os.path.basename(item) + ".png")
            resized_img.save(temp_path, "PNG")

            # Crop the resized image around the face
            cropped_img = face_cropper(temp_path, target_size)

            # Save the cropped image
            output_filename = os.path.splitext(os.path.basename(item))[0] + ".png"
            output_path = os.path.join(dest_path, output_filename)
            cropped_img.save(output_path, "PNG")

            # Remove the temporary file
            os.remove(temp_path)

    print("All operations complete! Elapsed time: %.2f s" % (time.time() - start_time))

if