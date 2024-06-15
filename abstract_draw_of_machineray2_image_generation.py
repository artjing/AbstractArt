import os
from PIL import Image, ImageOps, ImageFont, ImageDraw
import numpy as np
import random


# Set up constants and paths
results_dir = "results"
network_snapshot = "network-snapshot-000188.pkl"
info_file_path = "painting_info.txt"
font_path = '/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf'


# Clear out the results folder if it exists
if os.path.exists(results_dir):
    os.system(f"rm -r {results_dir}")


# Generate seed and arguments
seed = random.randint(0, 100000)
seed_arg = "--seeds="
for i in range(20):
    seed_arg += str(seed + i) + ","
seed_arg += str(seed + 20)


# Generate the images using stylegan2-ada-pytorch
os.system(f"python stylegan2-ada-pytorch/generate.py {seed_arg} --trunc=1.25 --outdir {results_dir} --network={network_snapshot}")


# Read the file containing the paintings and aspect ratios
x = np.linspace(0, 849, 850)
y = np.empty(shape=(850))
info_file = open(info_file_path, 'r')
lines = info_file.readlines()
count = 0


# Capture aspect ratios in the y array
for line in lines:
    parts = line.split(' ')
    if len(parts) == 2 and len(parts[1]) > 0:
        y[count] = float(parts[1])
    count += 1


# Sort the values
y = np.sort(y)


# Define utility functions
def get_aspect_ratio():
    input_x = np.random.rand(1) * 850
    y_interp = np.interp(input_x, x, y)
    return y_interp[0]


def get_concat_h(im1, im2):
    dst = Image.new('RGB', (im1.width + im2.width, im1.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst


def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst


# Get all the image file names
image_files = []
for root, dirs, files in os.walk(results_dir):
    files.sort()
    for file in files:
        if file.endswith(".png"):
            image_files.append(os.path.join(root, file))


# Generate a grid of thumbnails
aspect_ratios = []
size = 250
count = 0
thumbnails = []


for j in range(0, 3):
    for i in range(0, 7):
        tile = Image.open(image_files[count])
        aspect = get_aspect_ratio()
        aspect_ratios.append(aspect)
        if aspect < 1:
            newsize = (int(size * aspect), size)
        else:
            newsize = (size, int(size / aspect))
        tile = tile.resize(newsize)
        delta_w = size - newsize[0] + 20
        delta_h = size - newsize[1] + 30
        padding = (delta_w // 2, delta_h // 2, delta_w - (delta_w // 2), delta_h - (delta_h // 2))
        tile = ImageOps.expand(tile, padding, fill=(255, 255, 255))
        draw = ImageDraw.Draw(tile)
        draw.text((0, 0), str(count + 1), font=ImageFont.truetype(font_path, 20), fill=(0, 0, 0))
        if i % 7 == 0:
            row = tile
        else:
            row = get_concat_h(row, tile)
        count += 1
    if j % 4 == 0:
        group = row
    else:
        group = get_concat_v(group, row)
    thumbnails.append(group)


# Save the thumbnails or further process them as needed


# Example of further processing (commented out since EC2 can't display images)
# thumbnails[0].show()


# Optional: Provide functionality to choose a painting (not interactive on EC2)
chosen_thumbnail = 6  # Example selection


# Example of processing an image (commented out since EC2 can't display images)
# image = Image.open(image_files[chosen_thumbnail - 1])
# size = 1024
# aspect = aspect_ratios[chosen_thumbnail - 1]
# if aspect < 1:
#     newsize = (int(size * aspect), size)
# else:
#     newsize = (size, int(size / aspect))
# resized = image.resize(newsize)
# resized.show()
