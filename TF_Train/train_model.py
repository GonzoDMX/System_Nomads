import os
import argparse
from argparse import ArgumentParser
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd

import tensorflow as tf
from tensorflow import keras

from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras import layers
from tensorflow.keras.preprocessing import image
import pathlib

# Don't print extraneous warnings
tf.get_logger().setLevel('ERROR')

epoch_count = 200
batch_size = 16
v_ratio = 0.5
img_height = 250
img_width = 250

num_classes = 2


def load_dataset(path):
	data_dir = pathlib.Path(path)

	train_datagen = keras.preprocessing.image.ImageDataGenerator(
		# Normalize images
		#rescale=1./255,
		validation_split=v_ratio)


	train_dataset = train_datagen.flow_from_directory(
		data_dir,
		subset='training',
		class_mode='categorical',
		target_size=(img_height, img_width),
		batch_size=batch_size,
		shuffle=True)

	valid_dataset = train_datagen.flow_from_directory(
		data_dir,
		subset='validation',
		class_mode='categorical',
		target_size=(img_height, img_width),
		batch_size=batch_size,
		shuffle=True)
	return train_dataset, valid_dataset


def build_model():
	imagenet_model = keras.applications.ResNet50(
		weights='imagenet',
		include_top=False,
		input_shape=(img_height, img_width, 3))

	# The Imagenet Model is pre-trained
	# Thus we don't train it on our images
	for layer in imagenet_model.layers:
		layer.trainable = False

	# Add custom layers on top of ResNet
	global_avg_pooling = keras.layers.GlobalAveragePooling2D()(imagenet_model.output)
	output = keras.layers.Dense(
		num_classes,
		activation='sigmoid'
		)(global_avg_pooling)

	face_model = keras.models.Model(
		inputs=imagenet_model.input,
		outputs=output,
		name='ResNet50')
	
	# Display the model layers
	#face_model.summary()
	return face_model

def train_model(train_dataset, valid_dataset, model):
	# ModelCheckpoint to save model in case of interrupting the learning process
	checkpoint = ModelCheckpoint(
		"trained_model.h5",
		monitor="val_loss",
		mode="min",
		save_best_only=True,
		verbose=1)

	# EarlyStopping to find best model with a large number of epochs
	earlystop = EarlyStopping(
		monitor='val_loss',
		restore_best_weights=True,
		# Patience:If loss doe not improve after # epochs stop training
		patience=3,
		verbose=1)

	callbacks = [earlystop, checkpoint]

	model.compile(
		loss='categorical_crossentropy',
		optimizer=keras.optimizers.Adam(learning_rate=0.0001),
		metrics=['accuracy'])


	history = model.fit(
		train_dataset,
		epochs=epoch_count,
		callbacks=callbacks,
		validation_data=valid_dataset)
	return history

def graph_training_results(hist):
	acc = hist.history['accuracy']
	val_acc = hist.history['val_accuracy']

	loss = hist.history['loss']
	val_loss = hist.history['val_loss']

	epochs_range = range(epoch_count)

	plt.figure(figsize=(8, 8))
	plt.subplot(1, 2, 1)
	plt.plot(epochs_range, acc, label='Training Accuracy')
	plt.plot(epochs_range, val_acc, label='Validation Accuracy')
	plt.legend(loc='lower right')
	plt.title('Training and Validation Accuracy')

	plt.subplot(1, 2, 2)
	plt.plot(epochs_range, loss, label='Training Loss')
	plt.plot(epochs_range, val_loss, label='Validation Loss')
	plt.legend(loc='upper right')
	plt.title('Training and Validation Loss')
	plt.show()

def validate_path(p):
	if not os.path.isdir(p):
		raise argparse.ArgumentTypeError("{0} does not exist".format(p))
	return p

if __name__ == "__main__":
	parser = ArgumentParser(description="Target dataset.")
	parser.add_argument("-d", "--dataset",
		dest="datapath", required=True, type=validate_path,
		help="dataset dir path", metavar="DIR")
	args = parser.parse_args()
	
	# Don't print extraneous warnings
	tf.get_logger().setLevel('ERROR')

	train_dataset, valid_dataset = load_dataset(args.datapath)
	model = build_model()
	history = train_model(train_dataset, valid_dataset, model)
	graph_training(history)
	model.save("model.h5")
