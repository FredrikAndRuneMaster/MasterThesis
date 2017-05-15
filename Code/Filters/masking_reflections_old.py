#!/usr/bin/env python

import os
import sys
from PIL import Image
from PIL import ImageEnhance
import numpy as np
import json
import subprocess
from scipy import weave
import scipy.misc
import argparse
import random
import cv2

import time

current_milli_time = lambda: int(round(time.time() * 1000))


rgb_limit = 0
padding_radius = 5

def filter_images(in_folder, out_folder):
	# Seed the random
	random.seed(current_milli_time)
	
	# Create the output folder if it doesn't exist
	if not os.path.exists(out_folder):
		os.makedirs(out_folder)

	# Go through every .png image in the folder
	for file in os.listdir(in_folder):
		if ".png" in file:

			# Get the absolute path to the image
			image_path = in_folder + file

			# Open it, convert it to a numpy array and create a copy which is written to
			img = Image.open(image_path)
			img_array = np.array(img)
			out_array = img_array.copy()

			# Get the width and the height of the image
			width = img_array.shape[1]
			height = img_array.shape[0]

			# Used to check whether an area is marked or not (0 = normal, 1 = reflection)
			high_coords = np.zeros((height, width))

			# Mark the reflections
			out_array, high_coords = mark_reflections(img_array, out_array, high_coords, width, height)
			
			# Pad the marked reflection
			if padding_radius > 0:
				out_array = pad_marked_reflections(img_array, out_array, high_coords, width, height)

			# Fill the marked areas with colors
			out_array = fill_marked_areas(img_array, out_array, high_coords, width, height)

			# Save the image
			scipy.misc.toimage(out_array, cmin=0.0, cmax=0.0).save(out_folder + os.sep + file)
			#sys.exit(1)


def mark_reflections(img_array, out_array, high_coords, width, height):
	# Do the detection of white areas, and expand them
	code = r"""
		// img_array: The original image
		// out_array: The output image
		// high_coords: A mask, 1 = above rgb limit, 0 = under rgb limit

		uint8_t *out_array_tmp = (uint8_t *)malloc(height * width * 3);
		uint8_t *img_array_tmp = (uint8_t *)malloc(height * width * 3);
		uint8_t *high_coords_tmp = (uint8_t *)malloc(height * width);
		uint8_t rgb_limit_tmp[3];

		#define IMG_ARRAY(i, j, k) (img_array_tmp[i * width * 3 + j * 3 + k])
		#define OUT_ARRAY(i, j, k) (out_array_tmp[i * width * 3 + j * 3 + k])
		#define HIGH_COORDS(i, j) (high_coords_tmp[i * width, j])

		// Copy from the arguments to the arrays
		memcpy(out_array_tmp, out_array, width * height * 3);
		memcpy(img_array_tmp, img_array, width * height * 3);
		memcpy(high_coords_tmp, high_coords, width * height);
		memcpy(rgb_limit_tmp, rgb_limit, 3);


		// Mark the bright pixels red
		for (int i = 0; i < height; i++)
		{
			for (int j = 0; j < width; j++)
			{
				if (IMG_ARRAY(i, j, 0) > rgb_limit_tmp[0] && IMG_ARRAY(i, j, 1) > rgb_limit_tmp[1] && IMG_ARRAY(i, j, 2) > rgb_limit_tmp[2])
				{
					OUT_ARRAY(i, j, 0) = 0;
					OUT_ARRAY(i, j, 1) = 0;
					OUT_ARRAY(i, j, 2) = 255;
					HIGH_COORDS(i, j) = 1;
				}
			}
		}
		memcpy(out_array, out_array_tmp, width * height * 3);
		memcpy(high_coords, high_coords_tmp, width * height);

		free(out_array_tmp);
		free(img_array_tmp);
		free(high_coords_tmp);
	"""
	io = ["img_array", "out_array", "high_coords", "width", "height", "rgb_limit"]
	weave.inline(code, io, extra_compile_args=['-O0'])

	return out_array, high_coords



def pad_marked_reflections(img_array, out_array, high_coords, width, height):


	# Do the detection of white areas, and expand them
	code = r"""
		// img_array: The original image
		// out_array: The output image
		// high_coords: A mask, 1 = above rgb limit, 0 = under rgb limit
		uint8_t *out_array_tmp = (uint8_t *)malloc(height * width * 3);
		uint8_t *img_array_tmp = (uint8_t *)malloc(height * width * 3);
		uint8_t *high_coords_tmp = (uint8_t *)malloc(height * width);

		#define IMG_ARRAY(i, j, k) (img_array_tmp[i * width * 3 + j * 3 + k])
		#define OUT_ARRAY(i, j, k) (out_array_tmp[i * width * 3 + j * 3 + k])
		#define HIGH_COORDS(i, j) (high_coords_tmp[i * width, j])

		// Copy from the arguments to the arrays
		memcpy(out_array_tmp, out_array, width * height * 3);
		memcpy(img_array_tmp, img_array, width * height * 3);
		memcpy(high_coords_tmp, high_coords, width * height);


		// Expand in the y-axis
		for (int i = 0; i < height; i++)
		{
			for (int j = 0; j < width; j++)
			{
				
				// Upwards
				for (int k = 0; k < padding_radius; k++)
				{
					if (HIGH_COORDS(i, j) == 1 && i - k > 0 && HIGH_COORDS(i, j)j] == 0)
					{
						if (img_array_tmp[i-k][j][0] > 15 || img_array_tmp[i-k][j][1] > 15 || img_array_tmp[i-k][j][2] > 15)
						{
							out_array_tmp[i-k][j][0] = 0;
							out_array_tmp[i-k][j][1] = 0;
							out_array_tmp[i-k][j][2] = 255;
						}

						// To the right
						for (int l = 0; l < padding_radius; l++)
						{
							if (j + l < width && HIGH_COORDS(i, j)j+l] == 0)
							{
								if (img_array_tmp[i-k][j+l][0] > 15 || img_array_tmp[i-k][j+l][1] > 15 || img_array_tmp[i-k][j+l][2] > 15)
								{
									out_array_tmp[i-k][j+l][0] = 0;
									out_array_tmp[i-k][j+l][1] = 0;
									out_array_tmp[i-k][j+l][2] = 255;
								}
							}
						}


						// To the left
						for (int l = 0; l < padding_radius; l++)
						{
							if (j - l > 0 && HIGH_COORDS(i, j)j-l] == 0)
							{
								if (img_array_tmp[i-k][j-l][0] > 15 || img_array_tmp[i-k][j-l][1] > 15 || img_array_tmp[i-k][j-l][2] > 15)
								{
									out_array_tmp[i-k][j-l][0] = 0;
									out_array_tmp[i-k][j-l][1] = 0;
									out_array_tmp[i-k][j-l][2] = 255;
								}
							}
						}
					}
				}


				// Downwards
				for (int k = 0; k < padding_radius; k++)
				{
					if (HIGH_COORDS(i, j) == 1 && i + k < height && HIGH_COORDS(i, j)j] == 0)
					{
						if (img_array_tmp[i+k][j][0] > 15 || img_array_tmp[i+k][j][1] > 15 || img_array_tmp[i+k][j][2] > 15)
						{
							out_array_tmp[i+k][j][0] = 0;
							out_array_tmp[i+k][j][1] = 0;
							out_array_tmp[i+k][j][2] = 255;
						}


						// To the right
						for (int l = 0; l < padding_radius; l++)
						{
							if (j + l < width && HIGH_COORDS(i, j)j+l] == 0)
							{
								if (img_array_tmp[i+k][j+1][0] > 15 || img_array_tmp[i+k][j+1][1] > 15 || img_array_tmp[i+k][j+1][2] > 15)
								{
									out_array_tmp[i+k][j+l][0] = 0;
									out_array_tmp[i+k][j+l][1] = 0;
									out_array_tmp[i+k][j+l][2] = 255;
								}
							}
						}


						// To the left
						for (int l = 0; l < padding_radius; l++)
						{
							if (j - l > 0 && HIGH_COORDS(i, j)j-l] == 0)
							{
								if (img_array_tmp[i+k][j-1][0] > 15 || img_array_tmp[i+k][j-1][1] > 15 || img_array_tmp[i+k][j-1][2] > 15)
								{
									out_array_tmp[i+k][j-l][0] = 0;
									out_array_tmp[i+k][j-l][1] = 0;
									out_array_tmp[i+k][j-l][2] = 255;
								}
							}
						}
					}
				}
			}
		}

		
		// Expand in the x-axis
		for (int i = 0; i < height; i++)
		{
			for (int j = 0; j < width; j++)
			{
				
				// Upwards
				for (int k = 0; k < padding_radius; k++)
				{
					if (HIGH_COORDS(i, j) == 1 && j - k > 0 && HIGH_COORDS(i, j)k] == 0)
					{
						if (img_array_tmp[i][j-k][0] > 15 || img_array_tmp[i][j-k][1] > 15 || img_array_tmp[i][j-k][2] > 15)
						{
							out_array_tmp[i][j-k][0] = 0;
							out_array_tmp[i][j-k][1] = 0;
							out_array_tmp[i][j-k][2] = 255;
						}
					}
				}

				// Downwards
				for (int k = 0; k < padding_radius; k++)
				{
					if (HIGH_COORDS(i, j) == 1 && j + k < width && HIGH_COORDS(i, j)k] == 0)
					{
						if (img_array_tmp[i][j+k][0] > 15 || img_array_tmp[i][j+k][1] > 15 || img_array_tmp[i][j+k][2] > 15)
						{
							out_array_tmp[i][j+k][0] = 0;
							out_array_tmp[i][j+k][1] = 0;
							out_array_tmp[i][j+k][2] = 255;
						}
					}
				}
			}
		}
		

		memcpy(out_array, out_array_tmp[0][0], width * height * 3 * sizeof(char));
	"""
	io = ["img_array", "out_array", "high_coords", "width", "height", "padding_radius", "rgb_limit"]
	weave.inline(code, io, extra_compile_args=['-O3'])

	return out_array



def fill_marked_areas(img_array, out_array, high_coords, width, height):
	code = r"""
		#include <stdio.h>    	
		#include <stdlib.h>     
		#include <time.h> 

		#define EQUALS(array, height, width, r, g, b) (array[height][width][0] == r && array[height][width][1] == g && array[height][width][2] == b)
		#define HIGHER_OR(array, height, width, r, g, b) (array[height][width][0] > r || array[height][width][1] > g || array[height][width][2] > b)
		#define LOWER_OR(array, height, width, r, g, b) (array[height][width][0] < r || array[height][width][1] < g || array[height][width][2] < b)

		#define CLAMP(val, add, max) (val + add > max ? max : val + add)

		// img_array: The original image
		// out_array: The output image
		// high_coords: A mask, 1 = above rgb limit, 0 = under rgb limit
		unsigned char img_array_tmp[height][width][3];
		unsigned char out_array_tmp[height][width][3];
		unsigned char high_coords_tmp[height][width];


		// Copy from the arguments to the arrays
		memcpy(img_array_tmp[0][0], img_array, width * height * 3 * sizeof(char));
		memcpy(out_array_tmp[0][0], out_array, width * height * 3 * sizeof(char));
		memcpy(high_coords_tmp[0], high_coords, width * height * sizeof(char));



		// Seet the random
		srand (time(NULL));

		// Go through every pixel
		for (int i = 0; i < height; i++)
		{
			for (int j = 0; j < width; j++)
			{	
				// Find a relevant pixel to copy for every pixel in the image
				int found_color = 0;
				unsigned char rgb_left[3] = {0};
				unsigned char rgb_right[3] = {0};
				int avg_rgb[3] = {0};

				int number_of_pixels = 0;

				// If it's a blue pixel (a marked bright pixel)
				if EQUALS(out_array_tmp, i, j, 0, 0, 255)
				{
					if (!found_color) 
					{
						// Find an appropiate color/pixel to the left
						//int cur_pos = j - 20;
						int cur_pos = j-1;
						// number_of_pixels += 20;
						while (1)
						{
							if (HIGHER_OR(out_array_tmp, i, cur_pos, 15, 15, 15) && !EQUALS(out_array_tmp, i, cur_pos, 0, 0, 255))
							{
								rgb_left[0] = out_array_tmp[i][cur_pos][0];
								rgb_left[1] = out_array_tmp[i][cur_pos][1];
								rgb_left[2] = out_array_tmp[i][cur_pos][2];
								break;
								
							} else if (LOWER_OR(img_array_tmp, i, cur_pos, 15, 15, 15) || cur_pos == 0)
							{
								rgb_left[0] = 0;
								rgb_left[1] = 0;
								rgb_left[2] = 0;
								break;
							}

							cur_pos--;
							//number_of_pixels++;
						}
						
						//printf("Our pos: %d, %d | Pos to the right: %d, %d\n", j, i, j + 1, i);
						//printf("Our col: %d, %d, %d | Col to the right: %d, %d, %d\n", out_array_tmp[i][j][0], out_array_tmp[i][j][1], out_array_tmp[i][j][2], out_array_tmp[i][j+1][0], out_array_tmp[i][j+1][1], out_array_tmp[i][j+1][2]);

						// Find an appropiate color/pixel to the right
						//cur_pos = j + 10;
						cur_pos = j;
						// number_of_pixels += 10;
						int righty_tighty = 1;
						while(1) {
							cur_pos++;
							number_of_pixels++;

							if LOWER_OR(img_array_tmp, i, cur_pos, 15, 15, 15)
							{
								break;
							}

							//printf("j: %d, curpos: %d, R: %u, G: %u, B: %u\n", j, cur_pos, out_array_tmp[i][cur_pos][0], out_array_tmp[i][cur_pos][1], out_array_tmp[i][cur_pos][2]);

							//if (out_array_tmp[i][cur_pos][0] == 0 && out_array_tmp[i][cur_pos][1] == 0 && out_array_tmp[i][cur_pos][2] == 255)
							//{
							//	printf("Should find blue next\n");
							//}


							if EQUALS(out_array_tmp, i, cur_pos, 0, 0, 255)
							{
								// printf("FANT EN BLUEUEUEUEUE!!!!\n");
								continue;
							}

							righty_tighty--;

							if (righty_tighty == 0)
							{
								rgb_right[0] = out_array_tmp[i][cur_pos][0];
								rgb_right[1] = out_array_tmp[i][cur_pos][1];
								rgb_right[2] = out_array_tmp[i][cur_pos][2];
								break;
							}
						}
						found_color = 1;
					}
					if (rgb_right[0] == 0 && rgb_right[1] == 0 && rgb_right[2] == 0)
					{
						out_array_tmp[i][j][0] = rgb_left[0];
						out_array_tmp[i][j][1] = rgb_left[1];
						out_array_tmp[i][j][2] = rgb_left[2];
					
					} else {

						int r_step = 0;
						int g_step = 0;
						int b_step = 0;

						r_step = (1/number_of_pixels)*(rgb_right[0] - rgb_left[0]);
						g_step = (1/number_of_pixels)*(rgb_right[1] - rgb_left[1]);
						b_step = (1/number_of_pixels)*(rgb_right[2] - rgb_left[2]);

						// printf("right RGB: %u, %u, %u, left RGB: %u, %u, %u, r_step: %d, number_of_pixels: %d\n", rgb_right[0], rgb_right[1], rgb_right[2], rgb_left[0], rgb_left[1], rgb_left[2], r_step, number_of_pixels);

						for (int k = 0; k < number_of_pixels; k++)
						{
							if (rgb_left[0] == 0 && rgb_left[1] == 0 && rgb_left[2] == 0)
							{
								// out_array_tmp[i][j+k][0] = (rgb_right[0] + out_array_tmp[i-1][j][0]) / 2;
								// out_array_tmp[i][j+k][1] = (rgb_right[1] + out_array_tmp[i-1][j][1]) / 2;
								// out_array_tmp[i][j+k][2] = (rgb_right[2] + out_array_tmp[i-1][j][2]) / 2;
								out_array_tmp[i][j+k][0] = out_array_tmp[i-1][j+5][0] + (int) ((((float)(k+1) / (float)number_of_pixels) * (float)(rgb_right[0] - out_array_tmp[i-1][j+5][0])));
								out_array_tmp[i][j+k][1] = out_array_tmp[i-1][j+5][1] + (int) ((((float)(k+1) / (float)number_of_pixels) * (float)(rgb_right[1] - out_array_tmp[i-1][j+5][1])));
								out_array_tmp[i][j+k][2] = out_array_tmp[i-1][j+5][2] + (int) ((((float)(k+1) / (float)number_of_pixels) * (float)(rgb_right[2] - out_array_tmp[i-1][j+5][2])));	
							
							} else {
								out_array_tmp[i][j+k][0] = rgb_left[0] + (int) ((((float)(k+1) / (float)number_of_pixels) * (float)(rgb_right[0] - rgb_left[0])));
								out_array_tmp[i][j+k][1] = rgb_left[1] + (int) ((((float)(k+1) / (float)number_of_pixels) * (float)(rgb_right[1] - rgb_left[1])));
								out_array_tmp[i][j+k][2] = rgb_left[2] + (int) ((((float)(k+1) / (float)number_of_pixels) * (float)(rgb_right[2] - rgb_left[2])));
								//out_array_tmp[i][j+k][1] = rgb_left[1] + (((k+1)/(number_of_pixels)) * (rgb_right[1] - rgb_left[1]));
								//out_array_tmp[i][j+k][2] = rgb_left[2] + (((k+1)/(number_of_pixels)) * (rgb_right[2] - rgb_left[2]));

								// printf("setting R: %d, G: %d, B: %d\n", out_array_tmp[i][j+k][0], out_array_tmp[i][j+k][1], out_array_tmp[i][j+k][2]);
							}
						}

						j += number_of_pixels - 1;

						//out_array_tmp[i][j][0] = (rgb_left[0] + rgb_right[0]) / 2;
						//out_array_tmp[i][j][1] = (rgb_left[1] + rgb_right[1]) / 2;
						//out_array_tmp[i][j][2] = (rgb_left[2] + rgb_right[2]) / 2;
						//printf("%u, %u, %u\n", out_array_tmp[i][j][0], out_array_tmp[i][j][1], out_array_tmp[i][j][2]);
					}
					
				}
			}
		}

		memcpy(out_array, out_array_tmp[0][0], width * height * 3 * sizeof(char));
	"""
	io = ["img_array", "out_array", "high_coords", "width", "height", "padding_radius"]
	weave.inline(code, io, extra_compile_args=['-O3'])


	return out_array



if __name__ == "__main__":
	#Initialize the parser
	parser = argparse.ArgumentParser(description="A helper script for generating json files for TensorBox")

	# Add mandatory arguments
	parser.add_argument("in_folder", help="The folder with the images to apply the filter on")
	parser.add_argument("out_folder", help="The folder where the filtered images should be saved. Will be generated if it doesn't exist")
	
	parser.add_argument("-rgb", "--rgb_limit", type=int, default=[250, 150, 150], nargs=3, 
						help="The RGB limit of a pixel that should be marked as a reflection. When one of the channels are over, it's marked")

	parser.add_argument("-p", "--padding_radius", type=int, default=5, help="The radius to expand the marked areas")

	# Parse the provided arguments
	args = parser.parse_args()

	in_folder = args.in_folder
	out_folder = args.out_folder

	rgb_limit = np.array(args.rgb_limit, dtype=np.byte)
	padding_radius = args.padding_radius

	# Filter the images
	filter_images(in_folder, out_folder)
	


