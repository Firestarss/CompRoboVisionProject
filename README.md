# CompRoboVisionProject

## Introduction

The goal of this project was to be able to take a picture of a slide puzzle and, using OpenCV and an OCR library, generate the current state of the puzzle. Below is a gif of the program running and sucessfully (kinda) recognizing the tiles.

![Program Running](assets/run.gif)

## What is this program actually doing?

The program has 2 distinct parts to it:
1. Taking the base image and transforming it so that the puzzle area is cropped and directly head on to the camera.
2. Splitting the resulting image into individual tiles and extracting the text on them.

### Part 1: 4-Corner Transform

The first part is done through something called a 4-point transform. For that to work, you need to be able to either detect or select the 4 corners of the reigion of interest (ROI). In the above gif, you can see I am using my mouse to select the corners. From there, using built in methods in OpenCV, the code generates a transformation matrix that, once applied to the original image, takes it from something like this:

![Original Image](images/IMG_1090.jpg)

To this:

![Processed Image](assets/flattened.png)

### Part 2: Slicing and OCR

Once you have the flattened image, you can split it evenly in to N segments. Since the slide puzzle I am using was a 6x6 puzzle, the image was segmented into 36 tiles all the same size. The segmenting looks something like this:

![Slices](assets/split_lines.png)

This generates 36 individual images that look like the following:

![1](assets/1.png)

![2](assets/2.png)

![3](assets/3.png)

![4](assets/4.png)

![5](assets/5.png)

![6](assets/6.png)