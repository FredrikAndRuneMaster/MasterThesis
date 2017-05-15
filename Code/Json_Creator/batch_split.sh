#!/bin/bash
python json_creator.py Model5_plain_no-neg /home/fredrik/TensorFlow/Data/ /home/fredrik/TensorFlow/Models/Model5_no_neg/Train/ /home/fredrik/TensorFlow/Models/Model5_no_neg/Test
python json_creator.py Model5_plain_low-neg /home/fredrik/TensorFlow/Data/ /home/fredrik/TensorFlow/Models/Model5_low_neg/Train/ /home/fredrik/TensorFlow/Models/Model5_low_neg/Test

python json_creator.py Model5_r_no-neg /home/fredrik/TensorFlow/Data/ /home/fredrik/TensorFlow/Models/Model5_no_neg/Train/ /home/fredrik/TensorFlow/Models/Model5_no_neg/Test -r
python json_creator.py Model5_r_low-neg /home/fredrik/TensorFlow/Data/ /home/fredrik/TensorFlow/Models/Model5_low_neg/Train/ /home/fredrik/TensorFlow/Models/Model5_low_neg/Test -r

python json_creator.py Model5_rm_no-neg /home/fredrik/TensorFlow/Data/ /home/fredrik/TensorFlow/Models/Model5_no_neg/Train/ /home/fredrik/TensorFlow/Models/Model5_no_neg/Test -r -m
python json_creator.py Model5_rm_low-neg /home/fredrik/TensorFlow/Data/ /home/fredrik/TensorFlow/Models/Model5_low_neg/Train/ /home/fredrik/TensorFlow/Models/Model5_low_neg/Test -r -m

python json_creator.py Model5_rf_no-neg /home/fredrik/TensorFlow/Data/ /home/fredrik/TensorFlow/Models/Model5_no_neg/Train/ /home/fredrik/TensorFlow/Models/Model5_no_neg/Test -r -f
python json_creator.py Model5_rf_low-neg /home/fredrik/TensorFlow/Data/ /home/fredrik/TensorFlow/Models/Model5_low_neg/Train/ /home/fredrik/TensorFlow/Models/Model5_low_neg/Test -r -f

python json_creator.py Model5_rmf_no-neg /home/fredrik/TensorFlow/Data/ /home/fredrik/TensorFlow/Models/Model5_no_neg/Train/ /home/fredrik/TensorFlow/Models/Model5_no_neg/Test -r -m -f
python json_creator.py Model5_rmf_low-neg /home/fredrik/TensorFlow/Data/ /home/fredrik/TensorFlow/Models/Model5_low_neg/Train/ /home/fredrik/TensorFlow/Models/Model5_low_neg/Test -r -m -f
