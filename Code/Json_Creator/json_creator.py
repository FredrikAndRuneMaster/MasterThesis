#!/usr/bin/env python

import os
import sys
from PIL import Image
from PIL import ImageEnhance
import numpy as np
import json
import subprocess
from scipy import weave
import argparse

sys.path.append("../Filters/")
from masking_reflections import mask_reflections

feature_data = []

project_name = ""
train_root = ""
test_root = ""
dest = ""

enable_enhance_filter = False
enable_rotate = False
enable_brightness = False
enable_masking = False

class Image_object(object):
	img = 0
	name = ""
	coords = 0
	x_size = 0
	y_size = 0

	# The class "constructor" - It's actually an initializer 
	def __init__(self, img, name, coords, x_size, y_size):
		self.img = img
		self.name = name
		self.coords = coords
		self.x_size = x_size
		self.y_size = y_size


def rotate(img_obj_list, image_folder, full_save_path):
	"""
	Takes a list of images bla bla bla... fixed later. Prob by Fredrik since he experiences fysical pain because of things like this
	"""

	if not enable_rotate:
		return img_obj_list

	return_list = []

	for img_obj in img_obj_list:
		print "Performing rotation on %s" % img_obj.name
		
		img90 = img_obj.img.rotate(90)
		img180 = img_obj.img.rotate(180)
		img270 = img_obj.img.rotate(270)

		img90_name = img_obj.name[:-4] + "_r90.png"
		img180_name = img_obj.name[:-4] + "_r180.png"
		img270_name = img_obj.name[:-4] + "_r270.png"

		img90.save(full_save_path + os.sep + img90_name)
		img180.save(full_save_path + os.sep + img180_name)
		img270.save(full_save_path + os.sep + img270_name)

		feature_dict90 = {}
		feature_dict180 = {}
		feature_dict270 = {}

		sub_dict90 = {}
		sub_dict180 = {}
		sub_dict270 = {}

		sub_list90 = []
		sub_list180 = []
		sub_list270 = []

		img90_coords = []
		img180_coords = []
		img270_coords = []

		img90_coords.append(img_obj.coords[2] + 0.0)
		img90_coords.append(img_obj.coords[3] + 0.0)
		img90_coords.append(img_obj.x_size - img_obj.coords[1] + 0.0)
		img90_coords.append(img_obj.x_size - img_obj.coords[0] + 0.0)

		sub_dict90['x1'] = img90_coords[0]
		sub_dict90['x2'] = img90_coords[1]
		sub_dict90['y1'] = img90_coords[2]
		sub_dict90['y2'] = img90_coords[3]

		img180_coords.append(img_obj.x_size - img_obj.coords[1] + 0.0)
		img180_coords.append(img_obj.x_size - img_obj.coords[0] + 0.0)
		img180_coords.append(img_obj.y_size - img_obj.coords[3] + 0.0)
		img180_coords.append(img_obj.y_size - img_obj.coords[2] + 0.0)

		sub_dict180['x1'] = img180_coords[0]
		sub_dict180['x2'] = img180_coords[1]
		sub_dict180['y1'] = img180_coords[2]
		sub_dict180['y2'] = img180_coords[3]

		img270_coords.append(img_obj.y_size - img_obj.coords[3] + 0.0)
		img270_coords.append(img_obj.y_size - img_obj.coords[2] + 0.0)
		img270_coords.append(img_obj.coords[0] + 0.0)
		img270_coords.append(img_obj.coords[1] + 0.0)

		sub_dict270['x1'] = img270_coords[0]
		sub_dict270['x2'] = img270_coords[1]
		sub_dict270['y1'] = img270_coords[2]
		sub_dict270['y2'] = img270_coords[3]


		"""
		sub_dict180['x1'] = x_size - img_obj.coords[1] + 0.0
		sub_dict180['x2'] = x_size - img_obj.coords[0] + 0.0
		sub_dict180['y1'] = y_size - img_obj.coords[3] + 0.0
		sub_dict180['y2'] = y_size - img_obj.coords[2] + 0.0

		sub_dict270['x1'] = y_size - img_obj.coords[3] + 0.0
		sub_dict270['x2'] = y_size - img_obj.coords[2] + 0.0
		sub_dict270['y1'] = img_obj.coords[0] + 0.0
		sub_dict270['y2'] = img_obj.coords[1] + 0.0
		"""

		#sub_list.append(sub_dict)
		sub_list90.append(sub_dict90)
		sub_list180.append(sub_dict180)
		sub_list270.append(sub_dict270)

		#feature_dict['image_path'] = image_folder + "/" + image_file + "-" + filename.split("_")[-2] + ".png"
		feature_dict90['image_path'] = image_folder + "/" + img90_name
		feature_dict180['image_path'] = image_folder + "/" + img180_name
		feature_dict270['image_path'] = image_folder + "/" + img270_name

		#feature_dict['rects'] = sub_list
		feature_dict90['rects'] = sub_list90
		feature_dict180['rects'] = sub_list180
		feature_dict270['rects'] = sub_list270

		#feature_data.append(feature_dict)
		feature_data.append(feature_dict90)
		feature_data.append(feature_dict180)
		feature_data.append(feature_dict270)

		return_list.append(Image_object(img90, img90_name, img90_coords, img_obj.y_size, img_obj.x_size))
		return_list.append(Image_object(img180, img180_name, img180_coords, img_obj.x_size, img_obj.y_size))
		return_list.append(Image_object(img270, img270_name, img270_coords, img_obj.y_size, img_obj.x_size))
		return_list.append(img_obj)

	return return_list 


#def brightness(image, polyp_coords, image_name, image_folder, full_save_path):
def brightness(img_obj_list, image_folder, full_save_path):
	"""
	Takes an image as argument and produces various levels of brightness versions, saving them to disk and adding them to
	the json data

	Should only be used on images with polyps
	"""

	if not enable_brightness:
		return img_obj_list

	return_list = []

	for img_obj in img_obj_list:
		print "Performing brightness on %s" % img_obj.name
		img1 = ImageEnhance.Brightness(img_obj.img)
		img2 = ImageEnhance.Brightness(img_obj.img)
		img3 = ImageEnhance.Brightness(img_obj.img)
		
		img1_name = img_obj.name[:-4] + "_b033.png"
		img2_name = img_obj.name[:-4] + "_b066.png"
		img3_name = img_obj.name[:-4] + "_b133.png"

		img1.enhance(0.33).save(full_save_path + os.sep + img1_name)
		img2.enhance(0.66).save(full_save_path + os.sep + img2_name)
		img3.enhance(1.33).save(full_save_path + os.sep + img3_name)

		feature_dict033 = {}
		feature_dict066 = {}
		feature_dict133 = {}
		sub_dict = {}
		sub_list = []

		sub_dict['x1'] = img_obj.coords[0] + 0.0
		sub_dict['x2'] = img_obj.coords[1] + 0.0 
		sub_dict['y1'] = img_obj.coords[2] + 0.0
		sub_dict['y2'] = img_obj.coords[3] + 0.0

		sub_list.append(sub_dict)

		feature_dict033['image_path'] = image_folder + "/" + img1_name
		feature_dict066['image_path'] = image_folder + "/" + img2_name
		feature_dict133['image_path'] = image_folder + "/" + img3_name
		
		feature_dict033['rects'] = sub_list
		feature_dict066['rects'] = sub_list
		feature_dict133['rects'] = sub_list

		feature_data.append(feature_dict033)
		feature_data.append(feature_dict066)
		feature_data.append(feature_dict133)

		return_list.append(Image_object(img1, img1_name, img_obj.coords, img_obj.x_size, img_obj.y_size))
		return_list.append(Image_object(img2, img2_name, img_obj.coords, img_obj.x_size, img_obj.y_size))
		return_list.append(Image_object(img3, img3_name, img_obj.coords, img_obj.x_size, img_obj.y_size))
		return_list.append(img_obj)

	return return_list 


def scan_for_features(image, filename, image_folder, image_file):
	"""
	Scans each .tiff file for polyp locations marked in white, and if found, appends it to the global array
	which is later writtin in JSON format
	- filename: name on the .tiff file
	- image_folder: Folder where the .png images are
	- image_file: Name of the .png file, which should be in image_path
	"""
	# Open the image and initialize the numpy array
	img = Image.open(filename)
	img_array = np.array(img)

	# Initialize the 4 coordinates (x low, x high, y low, y high)
	coords = np.array([sys.maxint, -sys.maxint - 1, sys.maxint, -sys.maxint - 1])

	# X and Y dimensions of the image
	x_size = img_array.shape[1]
	y_size = img_array.shape[0]


	# Check every pixel, and set the coords
	code = r"""
		unsigned char tempData[y_size][x_size];
		long tempCoords[4];

		memcpy(tempData[0], img_array, x_size * y_size * sizeof(char));
		memcpy(tempCoords, coords, 4 * sizeof(long));

		for (int y = 0; y < y_size; y++)
		{
			for (int x = 0; x < x_size; x++)
			{
			
				if (tempData[y][x] != 0)
				{
					if (x < tempCoords[0])
					{
						tempCoords[0] = x;
					}

					if (x > tempCoords[1])
					{
						tempCoords[1] = x;
					}

					if (y < tempCoords[2])
					{
						tempCoords[2] = y;
					}

					if (y > tempCoords[3])
					{
						tempCoords[3] = y;
					}
				}
			
			}
		}

		memcpy(coords, tempCoords, 4 * sizeof(long));
	"""
	io = ["img_array", "coords", "x_size", "y_size"]
	weave.inline(code, io)

	# No coords were found, which means no polyp
	# Exit if we're generating the training file
	if coords[0] == sys.maxint:
		if "train" in image_folder:
			return
	
		coords[0] = -1		
		coords[1] = -1		
		coords[2] = -1		
		coords[3] = -1	
	
	# A polyp was found, append the correct data to the global feature_data
	feature_dict = {}
	sub_dict = {}
	sub_list = []

	if "test" in image_folder:
		# Don't put coordinates if they dont exist
		if coords[0] != -1:
			sub_dict['x1'] = coords[0] + 0.0
			sub_dict['x2'] = coords[1] + 0.0 
			sub_dict['y1'] = coords[2] + 0.0
			sub_dict['y2'] = coords[3] + 0.0

			sub_list.append(sub_dict)
			
		#feature_dict['image_path'] = image_folder + "_filtered" + "/" + image_file + "-" + filename.split("_")[-2] + ".png"
		feature_dict['image_path'] = image_folder + "/" + image_file + "-" + filename.split("_")[-2] + ".png"
		feature_dict['rects'] = sub_list

		feature_data.append(feature_dict)

	else:
		if coords[0] != -1:
			image_name = image_file + "-" + filename.split("_")[-2] + ".png"

			#img0 = Image.open(dest + image_folder + "/" + image_name)
			img0 = image

			#brightness(img0, coords, image_name, image_folder, dest + image_folder)

			test_list = [Image_object(img0, image_name, coords, x_size, y_size)]
			#test_list.append(Image_object(img0, image_name[:-4] + "second_edition.png", coords))

			test_list = rotate(test_list, image_folder, dest + image_folder)
			test_list = brightness(test_list, image_folder, dest + image_folder)

			sub_dict['x1'] = coords[0] + 0.0
			sub_dict['x2'] = coords[1] + 0.0
			sub_dict['y1'] = coords[2] + 0.0
			sub_dict['y2'] = coords[3] + 0.0

			sub_list.append(sub_dict)
			feature_dict['image_path'] = image_folder + "/" + image_file + "-" + filename.split("_")[-2] + ".png"
			feature_dict['rects'] = sub_list
			feature_data.append(feature_dict)

		else:
			feature_dict['image_path'] = image_folder + "/" + image_file + "-" + filename.split("_")[-2] + ".png"
			feature_dict['rects'] = sub_list

			feature_data.append(feature_dict)


	# Print out the image path and coords for the found polyo
	#print feature_dict['image_path'] + " || coords (%d, %d)  (%d, %d)" % (coords[0], coords[1], coords[2], coords[3])



def handle_folder(dirname, image_folder):
	"""
	Have reached a subfolder, where a .wmv could be located
	- Check if there is a .wmv file
		- If there isn't, return
	- Check if an outpit folder exists
		- If it doesn't, create one
	- Should have a .wmv file and output folder now, so split the video
	- Iterate over all .tiff files in the GT folder, and call scan_for_features on each
	"""

	# Check if a .wmv file exists
	image_file = ""
	for filename in os.listdir(dirname):
		if ".wmv" == filename[-4:]:
			image_file = filename
	
	# No .wmv file, return and traverse to next folder
	if image_file == "":
		return

	# Create the folder name
	if dest[-1] == os.sep:
		folder_name = dest + image_folder
	else:
		folder_name = dest + os.sep + image_folder

	# Create if it doesn't exist
	if not os.path.exists(folder_name):
		os.mkdir(folder_name)

	# Create the input and output image paths
	input_image = dirname + "/" + image_file
	output_image = folder_name + "/" + image_file[:-4] + "-%d.png"

	# Split the video into frames in the output folder
	split_frames_command = "ffmpeg -i " + input_image + " " + output_image
	result = subprocess.Popen(split_frames_command, shell=True, stdout=subprocess.PIPE)
	out, err = result.communicate()
	if err is not None:
		print "Error: Something happened during the splitting of frames"

	# Call scan_for_features for every *.tif in GT-folder
	# for filename in sorted(os.listdir(dirname + "/" + "GT/"), key=lambda t: int(t.split("_")[-2])):
	for filename in os.listdir(dirname + "/" + "GT/"):
    		
		# Find the path to the image
		image_path = folder_name + "/" + image_file[:-4] + "-" + filename.split("_")[-2] + ".png"

		# Mask the reflections - it opens the image from the path and returns a masked image
		image = mask_reflections(enable_masking, image_path)

		# Do the image enhancement
		if enable_enhance_filter:
			print "Enhance filtering image " + image_path
			
			command = "../Image_enhancement/single_image " + image_path
			result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
			out, err = result.communicate()
			if err is not None:
				print "Error: Something happened during the application of enhancement filter"
			
			image = Image.open(image_path)

		
		# Scan for features (and atm do the rotation and brightness)
		scan_for_features(image, dirname + "/" + "GT/" + filename, image_folder, image_file[:-4])



def traverse_path(target, image_folder):
	"""
	Traverses the path
	"""

	def walk_function (arg, dirname, fnames):
		"""
		Here we are interested in all subfolders
		except final deepest GT folder
		"""
		if "GT" == dirname.split("/")[-1]:
			return

		handle_folder(dirname, image_folder)
		
	os.path.walk(target, walk_function, None)


def apply_filter(in_folder, out_folder):
	"""
	Applies an enhancement filter on all images in the folder_name
	"""
	command = "../Image_enhancement/main " + in_folder + " " + out_folder
	result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
	out, err = result.communicate()
	if err is not None:
		print "Error: Something happened during the application of enhancement filter"


if __name__ == "__main__":
	'''
	1. arg - project name
	2. arg - train data root
	3. arg - test data root
	4. arg - destination root

	'''
	# Initialize the parser
	parser = argparse.ArgumentParser(description="A helper script for generating json files for TensorBox")

	# Add mandatory arguments
	parser.add_argument("project_name", help="the name of the project, appended on the training and test files")
	parser.add_argument("destionation_path", help="the the path of the destionation where the files will be placed in")
	parser.add_argument("training_data_root", help="the the path to the root where the training data is")
	parser.add_argument("test_data_root", help="the the path to the root where the test data is")

	# Add options
	parser.add_argument("-f", "--filter_images", action="store_true", help="flag to enable enhancement filtering of the images")
	parser.add_argument("-r", "--rotate_images", action="store_true", help="rotate each image containing a polyp 90, 180 and 270 degrees to improve training")
	parser.add_argument("-b", "--brightness", action="store_true", help="produce 3 additional copies of all polyp pictures with various brightness levels")
	parser.add_argument("-m", "--masking", action="store_true", help="mask the white spots/glares on the images")

	# Parse the provided arguments
	args = parser.parse_args()

	project_name = args.project_name
	dest = args.destionation_path
	train_root = args.training_data_root
	test_root = args.test_data_root

	enable_enhance_filter = args.filter_images
	enable_rotate = args.rotate_images
	enable_brightness = args.brightness
	enable_masking = args.masking

	# Do the training data
	print "Working on trainging data ..."
	traverse_path(train_root, project_name + "_train_images")
	with open(dest + project_name + '_train.json', 'w') as outfile:
		json.dump(feature_data, outfile, sort_keys=True, indent=2, ensure_ascii=False)


	# Empty the feature_data
	feature_data = []

	# Do the test data
	print "Working on test data ..."
	traverse_path(test_root, project_name + "_test_images")
	with open(dest + project_name + '_test.json', 'w') as outfile:
		json.dump(feature_data, outfile, sort_keys=True, indent=2, ensure_ascii=False)
	
	print "Finished ;)"

	# TODO:
	# - Clean up (remove old stuff, better comments etc.)
	# - Build the enhannce filter on start-up (run the build_single_image.sh)