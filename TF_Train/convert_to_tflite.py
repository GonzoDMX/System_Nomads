"""
	Created by: Andrew O'Shei
	
	Info:
	This program converts a Keras inference model to Tensorflow Lite
"""

import tensorflow as tf
import os
import argparse
from argparse import ArgumentParser


def convert_model(path):
	model = tf.keras.models.load_model(path)

	# Convert the model.
	converter = tf.lite.TFLiteConverter.from_keras_model(model)
	tflite_model = converter.convert()

	# Save the model.
	with open('model.tflite', 'wb') as f:
	  f.write(tflite_model)



def validate_file(f):
	if not os.path.exists(f):
		raise argparse.ArgumentTypeError("{0} does not exist".format(f))
	return f


if __name__ == "__main__":

    parser = ArgumentParser(description="Target Keras model.")
    parser.add_argument("-i", "--input", dest="filename", required=True, type=validate_file,
                        help="input file", metavar="FILE")
    args = parser.parse_args()
    print("Converting " + args.filename + " to TF Lite...")
    try:
    	convert_model(args.filename)
    except Exceptiopn as e:
    	print(e)
