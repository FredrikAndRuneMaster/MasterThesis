import tensorflow as tf
import os
import json
import subprocess
from scipy.misc import imread, imresize
from scipy import misc

from train import build_forward
from utils import googlenet_load
from utils.annolist import AnnotationLib as al
from utils.train_utils import add_rectangles, rescale_boxes, add_rectangles_confidence

import cv2
import argparse

min_conf_val = 0.0

def get_image_dir(args):
	weights_iteration = int(args.weights.split('-')[-1])
	expname = '_' + args.expname if args.expname else ''
	image_dir = '%s/images_%s_%d%s' % (os.path.dirname(args.weights), os.path.basename(args.test_idl)[:-4], weights_iteration, expname)
	return image_dir

def get_results(args, H):
	
	false_pos = [0, 0, 0, 0, 0, 0, 0, 0, 0]
	false_neg = [0, 0, 0, 0, 0, 0, 0, 0, 0]
	true_pos = [0, 0, 0, 0, 0, 0, 0, 0, 0]
	true_neg = [0, 0, 0, 0, 0, 0, 0, 0, 0]

	min_conf_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]

	tf.reset_default_graph()
	x_in = tf.placeholder(tf.float32, name='x_in', shape=[H['image_height'], H['image_width'], 3])
	googlenet = googlenet_load.init(H)
	if H['use_rezoom']:
		pred_boxes, pred_logits, pred_confidences, pred_confs_deltas, pred_boxes_deltas = build_forward(H, tf.expand_dims(x_in, 0), googlenet, 'test', reuse=None)
		grid_area = H['grid_height'] * H['grid_width']
		pred_confidences = tf.reshape(tf.nn.softmax(tf.reshape(pred_confs_deltas, [grid_area * H['rnn_len'], 2])), [grid_area, H['rnn_len'], 2])
		if H['reregress']:
			pred_boxes = pred_boxes + pred_boxes_deltas
	else:
		pred_boxes, pred_logits, pred_confidences = build_forward(H, tf.expand_dims(x_in, 0), googlenet, 'test', reuse=None)
	saver = tf.train.Saver()
	with tf.Session() as sess:
		sess.run(tf.initialize_all_variables())
		saver.restore(sess, args.weights)

		pred_annolist = al.AnnoList()

		true_annolist = al.parse(args.test_idl)
		data_dir = os.path.dirname(args.test_idl)
		
		if min_conf_val != 0.0:
			image_dir_falsepos = get_image_dir(args) + '_false_positive'
			image_dir_falseneg = get_image_dir(args) + '_false_negative'
			image_dir_truepos = get_image_dir(args) + '_true_positive'
			image_dir_trueneg = get_image_dir(args) + '_true_negative'

			subprocess.call('mkdir -p %s' % image_dir_falsepos, shell=True)
			subprocess.call('mkdir -p %s' % image_dir_falseneg, shell=True)
			subprocess.call('mkdir -p %s' % image_dir_truepos, shell=True)
			subprocess.call('mkdir -p %s' % image_dir_trueneg, shell=True)

			print "Saving images based on min conf value " + str(min_conf_val)
		else:
			print "Not saving images"
		
		for i in range(len(true_annolist)):
			true_anno = true_annolist[i]
			orig_img = imread('%s/%s' % (data_dir, true_anno.imageName))[:,:,:3]
			img = imresize(orig_img, (H["image_height"], H["image_width"]), interp='cubic')
			feed = {x_in: img}
			(np_pred_boxes, np_pred_confidences) = sess.run([pred_boxes, pred_confidences], feed_dict=feed)
			pred_anno = al.Annotation()
			pred_anno.imageName = true_anno.imageName
			new_img, rects, best_confidence = add_rectangles_confidence(H, [img], np_pred_confidences, np_pred_boxes,
											use_stitching=True, rnn_len=H['rnn_len'], min_conf=min_conf_val, tau=args.tau)
		
			pred_anno.rects = rects
			pred_anno.imagePath = os.path.abspath(data_dir)
			pred_anno = rescale_boxes((H["image_height"], H["image_width"]), pred_anno, orig_img.shape[0], orig_img.shape[1])
			pred_annolist.append(pred_anno)
			
			basename = os.path.basename(true_anno.imageName) [:-4]

			for j in range(len(min_conf_values)):
				if rects and best_confidence > min_conf_values[j]:
					if len(true_anno.rects) == 0:
						false_pos[j] += 1
						if min_conf_val == min_conf_values[j]:
							imname = '%s/%s_%0.6f.png' % (image_dir_falsepos, basename, best_confidence)

					else:
						true_pos[j] += 1
						if min_conf_val == min_conf_values[j]:
							imname = '%s/%s_%0.6f.png' % (image_dir_truepos, basename, best_confidence)
						
				else:
					if len(true_anno.rects) == 0:
						true_neg[j] += 1
						if min_conf_val == min_conf_values[j]:
							imname = '%s/%s_%0.6f.png' % (image_dir_trueneg, basename, best_confidence)
						
					else:
						false_neg[j] += 1
						if min_conf_val == min_conf_values[j]:
							imname = '%s/%s_%0.6f.png' % (image_dir_falseneg, basename, best_confidence)
			
			if min_conf_val != 0.0:            
				misc.imsave(imname, new_img)
			
			if i % 25 == 0:
				print(i)

	total_negative = true_neg[0] + false_pos[0]
	total_positive = true_pos[0] + false_neg[0]

	for k in range(len(min_conf_values)):
		print('Min_conf: %d%% TN: %d, FP: %d, Neg %%: %0.2f/%0.2f, TP: %d, FN: %d, Pos %%: %0.2f/%0.2f' % (
			int(min_conf_values[k]*100),
			true_neg[k],
			false_pos[k],
			float(float(true_neg[k])/float(total_negative)) * 100,
			float(float(false_pos[k])/float(total_negative)) * 100,
			true_pos[k], false_neg[k],
			float(float(true_pos[k])/float(total_positive)) * 100,
			float(float(false_neg[k])/float(total_positive)) * 100))        
	return pred_annolist, true_annolist

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--weights', required=True)
	parser.add_argument('--expname', default='')
	parser.add_argument('--test_idl', required=True)
	parser.add_argument('--gpu', default=0)
	parser.add_argument('--logdir', default='output')
	parser.add_argument('--iou_threshold', default=0.5, type=float)
	parser.add_argument('--tau', default=0.25, type=float)
	parser.add_argument('--min_conf', default=0.0, choices=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9], type=float)

	args = parser.parse_args()
	os.environ['CUDA_VISIBLE_DEVICES'] = str(args.gpu)
	hypes_file = '%s/hypes.json' % os.path.dirname(args.weights)
	with open(hypes_file, 'r') as f:
		H = json.load(f)
	expname = args.expname + '_' if args.expname else ''
	pred_idl = '%s.%s%s' % (args.weights, expname, os.path.basename(args.test_idl))
	true_idl = '%s.gt_%s%s' % (args.weights, expname, os.path.basename(args.test_idl))
	
	global min_conf_val
	min_conf_val = args.min_conf

	pred_annolist, true_annolist = get_results(args, H)
	#pred_annolist.save(pred_idl)
	#true_annolist.save(true_idl)

	'''
	try:
		rpc_cmd = './utils/annolist/doRPC.py --minOverlap %f %s %s' % (args.iou_threshold, true_idl, pred_idl)
		print('$ %s' % rpc_cmd)
		rpc_output = subprocess.check_output(rpc_cmd, shell=True)
		print(rpc_output)
		txt_file = [line for line in rpc_output.split('\n') if line.strip()][-1]
		output_png = '%s/results.png' % get_image_dir(args)
		plot_cmd = './utils/annolist/plotSimple.py %s --output %s' % (txt_file, output_png)
		print('$ %s' % plot_cmd)
		plot_output = subprocess.check_output(plot_cmd, shell=True)
		print('output results at: %s' % plot_output)
	except Exception as e:
		print(e)
	'''

if __name__ == '__main__':
	main()
