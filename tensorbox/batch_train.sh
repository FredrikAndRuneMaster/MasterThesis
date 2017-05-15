#!/bin/bash
python train.py --hypes hypes/Model5_plain_sgd_no-neg.json --logdir ../Trained/Model5_plain_sgd_no-neg/ --gpu 0
python train.py --hypes hypes/Model5_plain_adam_no-neg.json --logdir ../Trained/Model5_plain_adam_no-neg/ --gpu 0
