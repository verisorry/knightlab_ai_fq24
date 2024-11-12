# Knight Lab AI Editorial Model Training (FQ24)
Python image parser for Northwestern University's Knight Lab (FQ24) to crop a folder of training images of different sizes and formats into:
- 512x512 square
  - if the original image was vertical, crop from top
  - if the original image was horizontal, crop evenly from left and right edges
- Reformat to png
- Save all label .txt files

This repository includes two versions of the python script: one with basic capabilities and one with additional 'facial recognition' capabilities courtesy of the `facial-recognition` library.
