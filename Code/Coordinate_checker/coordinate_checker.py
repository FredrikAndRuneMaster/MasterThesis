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
import json
import cv2

if __name__ == "__main__":
	'''
	1. arg - project name
	2. arg - train data root
	3. arg - test data root
	4. arg - destination root

	'''
	# Initialize the parser
	parser = argparse.ArgumentParser(description="A helper script for generating json files for TensorBox")

	parser.add_argument("json_file", help="Json file containing rectangle coordinates")
	parser.add_argument("out_folder", help="Folder to dump output to")

	# Parse the provided arguments
	args = parser.parse_args()

	
	json_file = args.json_file
	dest = args.out_folder

	"""	project_name = args.project_name
	dest = args.destionation_path
	train_root = args.training_data_root
	test_root = args.test_data_root
	enable_filter = args.filter_images
	enable_rotate = args.rotate_images
	enable_brightness = args.brightness
	"""

	"""	# Do the training data
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
	

	if enable_filter:
		# Apply enhancement filter for train images, replacing original images
		print "Applying filter for train images ..."
		apply_filter(dest + project_name + "_train_images/", dest + project_name + "_train_images/")

		# Apply enhancement filter for test images, replacing original images
		print "Applying filter for test images ..."
		apply_filter(dest + project_name + "_test_images/", dest + project_name + "_test_images/")

	print "Finished ;)"
	"""

	with open(json_file) as data_file:    
		data = json.load(data_file)

	print data[0]["image_path"]
	print json_file

	path = json_file.split("/M")[0]
	print path

	for image in data:
		img = cv2.imread(path + os.sep + image["image_path"],cv2.IMREAD_COLOR)
		cv2.rectangle(img,(int(image["rects"][0]["x1"]),int(image["rects"][0]["y1"])),(int(image["rects"][0]["x2"]),int(image["rects"][0]["y2"])),(0,255,0),4)

		#cv2.imshow('image',img)
		#cv2.waitKey(0)
		#cv2.destroyAllWindows()
		
		#sys.exit(1)
		#print image["image_path"]

		cv2.imwrite(dest + "S" + image["image_path"].split("/S")[1], img)

	# TODO:
	# - Clean up (remove old stuff, better comments etc.)
	# - Add option whether to use default or enhanced images for test and train