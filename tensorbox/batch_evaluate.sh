#!/bin/bash

python evaluate.py --weights ../Trained/Model5_r_sgd_no-neg/Model5_r_sgd_no-neg_2017_04_21_17.30/save.ckpt-500000 --test_idl ../Data/Model5_r_test.json --gpu 0 > Model5_r_sgd_no-neg_500k_eval.txt
python evaluate.py --weights ../Trained/Model5_r_sgd_no-neg/Model5_r_sgd_no-neg_2017_04_21_17.30/save.ckpt-100000 --test_idl ../Data/Model5_r_test.json --gpu 0 > Model5_r_sgd_no-neg_100k_eval.txt
python evaluate.py --weights ../Trained/Model5_r_sgd_no-neg/Model5_r_sgd_no-neg_2017_04_21_17.30/save.ckpt-200000 --test_idl ../Data/Model5_r_test.json --gpu 0 > Model5_r_sgd_no-neg_200k_eval.txt
python evaluate.py --weights ../Trained/Model5_r_sgd_no-neg/Model5_r_sgd_no-neg_2017_04_21_17.30/save.ckpt-300000 --test_idl ../Data/Model5_r_test.json --gpu 0 > Model5_r_sgd_no-neg_300k_eval.txt
python evaluate.py --weights ../Trained/Model5_r_sgd_no-neg/Model5_r_sgd_no-neg_2017_04_21_17.30/save.ckpt-400000 --test_idl ../Data/Model5_r_test.json --gpu 0 > Model5_r_sgd_no-neg_400k_eval.txt
