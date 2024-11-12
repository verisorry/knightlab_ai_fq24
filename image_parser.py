# Silvia Fang
# 11 Nov, 2024
# Python image parser for Knight Lab (FQ24) to crop images into a 512x512 square and reformat to png

from PIL import Image
import sys, os, glob, shutil, time
from tqdm import tqdm

# resizes image's smallest side to 512, maintaining aspect ratio
def resizer(img: Image, target_size=512) -> Image:
    width, height = img.size
    if width > height:
        new_height = target_size
        new_width = int((target_size / height) * width)
    else:
        new_width = target_size
        new_height = int((target_size / width) * height)
    return img.resize((new_width, new_height), Image.LANCZOS)


def cropper(img: Image, target_size=512) -> Image:
    width, height = img.size

    # horizontal image, crop evenly from left and right
    if width > height:
        left = (width - target_size) // 2
        right = left + target_size
        return img.crop((left, 0, right, target_size))

    # vertical image, crop from x0, y0
    else:
        return img.crop((0, 0, target_size, target_size))


def main():
    start_time = time.time()
    src_path = sys.argv[1]
    dest_path = src_path + '_cleaned'
    target_size = int(sys.argv[2]) if len(sys.argv) == 3 else 512

    # delete existing new directory path if it already exists
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

    # Copy all .txt files to the new folder
    txt_files = glob.glob(os.path.join(src_path, '*.txt'))
    for file in tqdm(txt_files, desc="Copying label files", unit=" file"):
        shutil.copy2(file, dest_path)

    # Process each image in the source directory
    image_files = [f for ext in ["jpg", "jpeg", "png", "webp", "bmp"] for f in glob.glob(src_path + f'/*.{ext}')]
    for item in tqdm(image_files, desc="Processing images", unit=" image"):
        with Image.open(item) as img:

            if img.mode != "RGBA": img = img.convert("RGBA")

            # Resizing
            resized_img = resizer(img, target_size)

            # Cropping
            cropped_img = cropper(resized_img, target_size)

            # Saving as .png in the destination folder
            output_filename = os.path.splitext(os.path.basename(item))[0] + ".png"
            output_path = os.path.join(dest_path, output_filename)
            cropped_img.save(output_path, "PNG")

    print("All operations complete! Elapsed time: %.2f s" % (time.time() - start_time))


if __name__ == "__main__":
    main()
