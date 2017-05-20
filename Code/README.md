This folder contains the tools made during the thesis.

## Json Creator
This is a tool which takes annoated data as input, exracts images from the videos, scans for the polyp location, optionally applies data enhancement methods, and saves the json files for training and evaluation.

## Image Enhancement
This is a small C++ program which applies a CLAHE filter to the image.
There are 2 versions:
* main.cc: Takes in two arguments, input and output folder. It traverses the input folder, and for each image, it applies the filter and saves the new version in the output folder.
* single_image.cc: Takes an image as the argument, applies CLAHE to the image, and overwrites the old image with the new one.

Remember to run either build.sh or build_single_image.sh before executing either version.

## Filters
This is the masking_reflections tool which tries to mask the reflections in the image, and replace them with surrounding colors.
This script is part of Json Creator, and not meant to run independently.

## Cordinate checker
A simple script which displays the polyp location in the images from the json files Json Creator generates.

## Detection graph
graph_maker.py is a script for generating detection graphs, which are graphs containing the ground truth for the polyp, and every frame the system detected a polyp.
It accepts one argument, which is a folder containing the following folders: TP, FP, TN, FN, which each contains the images.

It generates 3 files:
* ground truth, which is the frames where the polyp is visible
* detections, which is the frame num with the polyps the system were able to detect
* all, which are all the frames. Used for finding the max value in the x-axis.

These files are then used in detection_graph.gp, which is a Gnuplot script.
This script is used to generate the graphs seen in the thesis.
