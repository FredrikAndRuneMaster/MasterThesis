#!/usr/bin/env python

import numpy as np
import scipy.misc
from scipy import weave
from PIL import Image

def mask_reflections(enable_masking, image_path, rgb_limit=[240, 150, 150], padding_radius=5):
	img = Image.open(image_path)

	# Just return the original image if masking is disabled
	if not enable_masking:
		return img

	print "Masking image " + image_path + " | Padding: " + str(padding_radius) + ", RGB: "+ str(rgb_limit)

	original_image = np.array(img)
	out_image = original_image.copy()
	
	# Get the width and the height of the image
	width = original_image.shape[1]
	height = original_image.shape[0]

	# Used to check whether an area is marked or not (0 = normal, 1 = reflection)
	high_coords = np.zeros((height, width))

	# Mark the reflections
	out_image, high_coords = mark_reflections(original_image, out_image, high_coords, width, height, rgb_limit)
			
	# Pad the marked reflection
	if padding_radius > 0:
		out_image = pad_marked_reflections(original_image, out_image, high_coords, width, height, padding_radius)

	# Fill the marked areas with colors
	out_image = fill_marked_areas(original_image, out_image, high_coords, width, height)

	# Save and return the image
	masked_image = scipy.misc.toimage(out_image, cmin=0.0, cmax=0.0)
	masked_image.save(image_path)
	return masked_image


def mark_reflections(original_image, out_image, high_coords, width, height, rgb_limit):
	"""
	This is step 1/3 of the algorithm - the marking of reflections
	
	It loops through the image, and for every pixel exceeding the RGB limit,
	it marks the pixel blue

	At the end, it returns the updated image
	"""

	# Convert it to np array of uint8 before sending to weave
	rgb_limit_np = np.array(rgb_limit, dtype=np.uint8)

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
		#define HIGH_COORDS(i, j) (high_coords_tmp[i * width + j])

		// Copy from the arguments to the arrays
		memcpy(out_array_tmp, out_image, width * height * 3);
		memcpy(img_array_tmp, original_image, width * height * 3);
		memcpy(high_coords_tmp, high_coords, width * height);
		memcpy(rgb_limit_tmp, rgb_limit_np, 3);


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
		memcpy(out_image, out_array_tmp, width * height * 3);
		memcpy(high_coords, high_coords_tmp, width * height);

		free(out_array_tmp);
		free(img_array_tmp);
		free(high_coords_tmp);
	"""
	io = ["original_image", "out_image", "high_coords", "width", "height", "rgb_limit_np"]
	weave.inline(code, io, extra_compile_args=['-O0'])

	return out_image, high_coords



def pad_marked_reflections(original_image, out_image, high_coords, width, height, padding_radius):
	"""
	This is step 2/3 of the algorithm - the padding of the marked areas

	It iterates over the image, and for every marked (blue) pixel, it padds 'padding_radius' 
	number of pixels in a box around it
	By doing this, every marked pixel will get a padding "field" around itself, making it possible
	to have a low rgb_limit while still get big enough marked areas

	Ath the end, it returns the updated image
	"""

	code = r"""
		// img_array: The original image
		// out_array: The output image
		// high_coords: A mask, 1 = above rgb limit, 0 = under rgb limit

		uint8_t *out_array_tmp = (uint8_t *)malloc(height * width * 3);
		uint8_t *img_array_tmp = (uint8_t *)malloc(height * width * 3);
		uint8_t *high_coords_tmp = (uint8_t *)malloc(height * width);

		#define IMG_ARRAY(i, j, k) img_array_tmp[(i * width * 3) + (j * 3) + k]
		#define OUT_ARRAY(i, j, k) out_array_tmp[(i * width * 3) + (j * 3) + k]
		#define HIGH_COORDS(i, j) high_coords_tmp[(i * width) + j]

		// Copy from the arguments to the arrays
		memcpy(out_array_tmp, out_image, width * height * 3);
		memcpy(img_array_tmp, original_image, width * height * 3);
		memcpy(high_coords_tmp, high_coords, width * height);

		// Expand in the y-axis
		for (int i = 0; i < height; i++)
		{
			for (int j = 0; j < width; j++)
			{
				
				// Upwards
				for (int k = 0; k < padding_radius; k++)
				{
					if (HIGH_COORDS(i, j) == 1 && i - k > 0 && HIGH_COORDS((i-k), j) == 0)
					{
						if (IMG_ARRAY((i-k), j, 0) > 15 || IMG_ARRAY((i-k), j, 1) > 15 || IMG_ARRAY((i-k), j, 2) > 15)
						{
							OUT_ARRAY((i-k), j, 0) = 0;
							OUT_ARRAY((i-k), j, 1) = 0;
							OUT_ARRAY((i-k), j, 2) = 255;
						}

						// To the right
						for (int l = 0; l < padding_radius; l++)
						{
							if (j + l < width && HIGH_COORDS((i-k), (j+l)) == 0)
							{
								if (IMG_ARRAY((i-k), (j+l), 0) > 15 || IMG_ARRAY((i-k), (j+l), 1) > 15 || IMG_ARRAY((i-k), (j+l), 2) > 15)
								{
									OUT_ARRAY((i-k), (j+l), 0) = 0;
									OUT_ARRAY((i-k), (j+l), 1) = 0;
									OUT_ARRAY((i-k), (j+l), 2) = 255;
								}
							}
						}


						// To the left
						for (int l = 0; l < padding_radius; l++)
						{
							if (j - l > 0 && HIGH_COORDS((i-k), (j-l)) == 0)
							{
								if (IMG_ARRAY((i-k), (j-l), 0) > 15 || IMG_ARRAY((i-k), (j-l), 1) > 15 || IMG_ARRAY((i-k), (j-l), 2) > 15)
								{
									OUT_ARRAY((i-k), (j-l), 0) = 0;
									OUT_ARRAY((i-k), (j-l), 1) = 0;
									OUT_ARRAY((i-k), (j-l), 2) = 255;
								}
							}
						}
					}
				}


				// Downwards
				for (int k = 0; k < padding_radius; k++)
				{
					if (HIGH_COORDS(i, j) == 1 && i + k < height && HIGH_COORDS((i+k), j) == 0)
					{
						if (IMG_ARRAY((i+k), j, 0) > 15 || IMG_ARRAY((i+k), j, 1) > 15 || IMG_ARRAY((i+k), j, 2) > 15)
						{
							OUT_ARRAY((i+k), j, 0) = 0;
							OUT_ARRAY((i+k), j, 1) = 0;
							OUT_ARRAY((i+k), j, 2) = 255;
						}


						// To the right
						for (int l = 0; l < padding_radius; l++)
						{
							if (j + l < width && HIGH_COORDS((i+k), (j+l)) == 0)
							{
								if (IMG_ARRAY((i+k), (j+1), 0) > 15 || IMG_ARRAY((i+k), (j+1), 1) > 15 || IMG_ARRAY((i+k), (j+1), 2) > 15)
								{
									OUT_ARRAY((i+k), (j+l), 0) = 0;
									OUT_ARRAY((i+k), (j+l), 1) = 0;
									OUT_ARRAY((i+k), (j+l), 2) = 255;
								}
							}
						}


						// To the left
						for (int l = 0; l < padding_radius; l++)
						{
							if (j - l > 0 && HIGH_COORDS((i+k), (j-l)) == 0)
							{
								if (IMG_ARRAY((i+k), (j-1), 0) > 15 || IMG_ARRAY((i+k), (j-1), 1) > 15 || IMG_ARRAY((i+k), (j-1), 2) > 15)
								{
									OUT_ARRAY((i+k), (j-l), 0) = 0;
									OUT_ARRAY((i+k), (j-l), 1) = 0;
									OUT_ARRAY((i+k), (j-l), 2) = 255;
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
					if (HIGH_COORDS(i, j) == 1 && j - k > 0 && HIGH_COORDS(i, (j-k)) == 0)
					{
						if (IMG_ARRAY(i, (j-k), 0) > 15 || IMG_ARRAY(i, (j-k), 1) > 15 || IMG_ARRAY(i, (j-k), 2) > 15)
						{
							OUT_ARRAY(i, (j-k), 0) = 0;
							OUT_ARRAY(i, (j-k), 1) = 0;
							OUT_ARRAY(i, (j-k), 2) = 255;
						}
					}
				}

				// Downwards
				for (int k = 0; k < padding_radius; k++)
				{
					if (HIGH_COORDS(i, j) == 1 && j + k < width && HIGH_COORDS(i, (j+k)) == 0)
					{
						if (IMG_ARRAY(i, (j+k), 0) > 15 || IMG_ARRAY(i, (j+k), 1) > 15 || IMG_ARRAY(i, (j+k), 2) > 15)
						{
							OUT_ARRAY(i, (j+k), 0) = 0;
							OUT_ARRAY(i, (j+k), 1) = 0;
							OUT_ARRAY(i, (j+k), 2) = 255;
						}
					}
				}
			}
		}
		
		memcpy(out_image, out_array_tmp, width * height * 3);

		free(out_array_tmp);
		free(img_array_tmp);
		free(high_coords_tmp);
	"""
	io = ["original_image", "out_image", "high_coords", "width", "height", "padding_radius"]
	weave.inline(code, io, extra_compile_args=['-O3'])

	return out_image



def fill_marked_areas(original_image, out_image, high_coords, width, height):
	"""
	This is step 3/3 of the algorithm - filling of the marked and padded areas

	It loops through the image, and for every marked/blue pixel, it replaces it with a new color
	For the new color, it tries to find a pixel on the left and on the right, and then fill in a gradient line

	So for every pixel it finds, it finds the color on the left, the color on the right (first non-marked pixel),
	and creates a gradient scale which it uses for all the blue pixels side-by-side to the right, until a non-marked pixel is found

	At the end, it returns the updated image
	"""

	code = r"""
		// img_array: The original image
		// out_array: The output image
		// high_coords: A mask, 1 = above rgb limit, 0 = under rgb limit

		uint8_t *out_array_tmp = (uint8_t *)malloc(height * width * 3);
		uint8_t *img_array_tmp = (uint8_t *)malloc(height * width * 3);
		uint8_t *high_coords_tmp = (uint8_t *)malloc(height * width);

		#define IMG_ARRAY(i, j, k) img_array_tmp[i * width * 3 + j * 3 + k]
		#define OUT_ARRAY(i, j, k) out_array_tmp[i * width * 3 + j * 3 + k]
		#define HIGH_COORDS(i, j) high_coords_tmp[i * width + j]

		#define EQUALS(array, i, j, r, g, b) (array[i * width * 3 + j * 3 + 0] == r && array[i * width * 3 + j * 3 + 1] == g && array[i * width * 3 + j * 3 + 2] == b)
		#define HIGHER_OR(array, i, j, r, g, b) (array[i * width * 3 + j * 3 + 0] > r || array[i * width * 3 + j * 3 + 1] > g || array[i * width * 3 + j * 3 + 2] > b)
		#define LOWER_OR(array, i, j, r, g, b) (array[i * width * 3 + j * 3 + 0] < r || array[i * width * 3 + j * 3 + 1] < g || array[i * width * 3 + j * 3 + 2] < b)

		// Copy from the arguments to the arrays
		memcpy(out_array_tmp, out_image, width * height * 3);
		memcpy(img_array_tmp, original_image, width * height * 3);
		memcpy(high_coords_tmp, high_coords, width * height);

		// Go through every pixel
		for (int i = 0; i < height; i++)
		{
			for (int j = 0; j < width; j++)
			{	
				// Find a relevant pixel to copy for every pixel in the image
				int found_color = 0;
				unsigned char rgb_left[3] = {0};
				unsigned char rgb_right[3] = {0};
				int number_of_pixels = 0;

				// If it's a blue pixel (a marked bright pixel)
				if EQUALS(out_array_tmp, i, j, 0, 0, 255)
				{
					if (!found_color) 
					{
						// Find an appropiate color/pixel to the left
						int cur_pos = j-1;
						while (1)
						{
							if (HIGHER_OR(out_array_tmp, i, cur_pos, 15, 15, 15) && !EQUALS(out_array_tmp, i, cur_pos, 0, 0, 255))
							{
								rgb_left[0] = OUT_ARRAY(i, cur_pos, 0);
								rgb_left[1] = OUT_ARRAY(i, cur_pos, 1);
								rgb_left[2] = OUT_ARRAY(i, cur_pos, 2);
								break;
								
							} else if (LOWER_OR(img_array_tmp, i, cur_pos, 15, 15, 15) || cur_pos == 0)
							{
								rgb_left[0] = 0;
								rgb_left[1] = 0;
								rgb_left[2] = 0;
								break;
							}

							cur_pos--;
						}
						

						// Find an appropiate color/pixel to the right
						cur_pos = j;
						int righty_tighty = 1;
						while(1) {
							cur_pos++;
							number_of_pixels++;

							if LOWER_OR(img_array_tmp, i, cur_pos, 15, 15, 15)
							{
								break;
							}
	
							if EQUALS(out_array_tmp, i, cur_pos, 0, 0, 255)
							{
								continue;
							}

							righty_tighty--;

							if (righty_tighty == 0)
							{
								rgb_right[0] = OUT_ARRAY(i, cur_pos, 0);
								rgb_right[1] = OUT_ARRAY(i, cur_pos, 1);
								rgb_right[2] = OUT_ARRAY(i, cur_pos, 2);
								break;
							}
						}
						found_color = 1;
					}
					if (rgb_right[0] == 0 && rgb_right[1] == 0 && rgb_right[2] == 0)
					{
						OUT_ARRAY(i, j, 0) = rgb_left[0];
						OUT_ARRAY(i, j, 1) = rgb_left[1];
						OUT_ARRAY(i, j, 2) = rgb_left[2];
					
					} else {

						for (int k = 0; k < number_of_pixels; k++)
						{
							if (rgb_left[0] == 0 && rgb_left[1] == 0 && rgb_left[2] == 0)
							{
								OUT_ARRAY(i, (j+k), 0) = OUT_ARRAY(i-1, (j+5), 0) + (int) ((((float)(k+1) / (float)number_of_pixels) * (float)(rgb_right[0] - OUT_ARRAY(i-1, (j+5), 0))));
								OUT_ARRAY(i, (j+k), 1) = OUT_ARRAY(i-1, (j+5), 1) + (int) ((((float)(k+1) / (float)number_of_pixels) * (float)(rgb_right[1] - OUT_ARRAY(i-1, (j+5), 1))));
								OUT_ARRAY(i, (j+k), 2) = OUT_ARRAY(i-1, (j+5), 2) + (int) ((((float)(k+1) / (float)number_of_pixels) * (float)(rgb_right[2] - OUT_ARRAY(i-1, (j+5), 2))));	
							
							} else {
								OUT_ARRAY(i, (j+k), 0) = rgb_left[0] + (int) ((((float)(k+1) / (float)number_of_pixels) * (float)(rgb_right[0] - rgb_left[0])));
								OUT_ARRAY(i, (j+k), 1) = rgb_left[1] + (int) ((((float)(k+1) / (float)number_of_pixels) * (float)(rgb_right[1] - rgb_left[1])));
								OUT_ARRAY(i, (j+k), 2) = rgb_left[2] + (int) ((((float)(k+1) / (float)number_of_pixels) * (float)(rgb_right[2] - rgb_left[2])));
							}
						}

						j += number_of_pixels - 1;
					}
					
				}
			}
		}

		memcpy(out_image, out_array_tmp, width * height * 3);

		free(out_array_tmp);
		free(img_array_tmp);
		free(high_coords_tmp);
	"""
	io = ["original_image", "out_image", "high_coords", "width", "height"]
	weave.inline(code, io, extra_compile_args=['-O3'])


	return out_image