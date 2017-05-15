
import os
import sys
from PIL import Image
from PIL import ImageEnhance
import numpy as np
import json
import subprocess
from scipy import weave
import argparse

list_all = []

dict_ground_truth = {}
dict_detected_polyps = {}


def handle_folders(conf, folder_path, base_y):
	folders = ["TP", "FP", "TN", "FN"]

	for filename in sorted(os.listdir(folder_path + conf + "/TP"), key=lambda t: int(t.split("_")[2].split("-")[1])):
		frame_num = filename.split("_")[2].split("-")[1]
		list_all.append(int(frame_num))
		dict_ground_truth[frame_num] = base_y
		dict_detected_polyps[frame_num] = base_y + 1

	for filename in sorted(os.listdir(folder_path + conf + "/FP"), key=lambda t: int(t.split("_")[2].split("-")[1])):
		frame_num = filename.split("_")[2].split("-")[1]
		list_all.append(int(frame_num))
		dict_detected_polyps[frame_num] = base_y + 1

	for filename in sorted(os.listdir(folder_path + conf + "/TN"), key=lambda t: int(t.split("_")[2].split("-")[1])):
		frame_num = filename.split("_")[2].split("-")[1]
		list_all.append(int(frame_num))

	for filename in sorted(os.listdir(folder_path + conf + "/FN"), key=lambda t: int(t.split("_")[2].split("-")[1])):
		frame_num = filename.split("_")[2].split("-")[1]
		list_all.append(int(frame_num))
		dict_ground_truth[frame_num] = base_y


def print_to_files(conf):

	with open(conf + "-ground_truth.txt", "w") as ground_file:
		for key, value in sorted(dict_ground_truth.iteritems(), key=lambda t: int(t[0])):
			ground_file.write(str(key) + " " + str(value) + "\n")

	with open(conf + "-detected_polyps.txt", "w") as polyp_file:
		for key, value in sorted(dict_detected_polyps.iteritems(), key=lambda t: int(t[0])):
			polyp_file.write(str(key) + " " + str(value) + "\n")

	with open(conf + "-all.txt", "w") as all_file:
		for frame in sorted(list_all):
			all_file.write(str(frame) + " " + str(0) + "\n")



if __name__ == '__main__':

	parser = argparse.ArgumentParser(description="A helper script for generating json files for TensorBox")

	# Add mandatory arguments
	parser.add_argument("folder_path", help="Path of the folder which contains the TP, FP, TN and FN folders")

	# Parse the provided arguments
	args = parser.parse_args()
	folder_path = args.folder_path

	base_y = 1

	for conf in sorted(os.listdir(folder_path)):
		handle_folders(conf, folder_path, base_y)
		print_to_files(conf)

		list_all = []
		dict_detected_polyps = {}
		dict_ground_truth = {}
		base_y = base_y + 1



