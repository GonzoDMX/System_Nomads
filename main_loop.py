#!/usr/bin/env python3

"""
	Created by: Andrew O'Shei

	Demo for facial detection and identification on a Raspberry Pi 3B+

	Notes:
		A HC-SR04 Ultrasound Sensor is used to detect the presence of a person.
		If an object is detected within range, For demo purposes less than 10 cm,
		a photo is captured with the Raspberry Pi's camera. This photo is then
		processed using the OpenCV CascadeClassifier model in order to detect faces.
		If faces are present they are cropped from the initial photo and then each is
		individually processed by a ResNet50 Tensorflow Model that is trained to detect
		my face. Bounding boxes for detected faces and ID data are drawn on to the
		original photo and then it is saved to disk.
"""

import os
import sys
import signal
import subprocess
import glob
import time
from datetime import datetime
import numpy as np
import cv2 as cv
from picamera import PiCamera
from tflite_runtime.interpreter import Interpreter
from PIL import Image

import db_helper as db

# Set image params
img_height = 250
img_width = 250

im_path = 'tmp/tmp.jpg'

log_dir = 'photo_log/'

run_program = True

green = (30, 255, 10)
red = (20, 20, 255)

def camera_manager():
	bead = 0
	try:
		camera = PiCamera()
		img_file = open(im_path, 'wb')
		camera.start_preview()
		tmp = subprocess.call("./ultrason")
		if tmp == 0:
			camera.capture(img_file)
		img_file.close()
		camera.close()
		bead = 1
	except Exception as e:
		print(e)

	finally:
		return bead


def main_program():
	global run_program
	global im_path
	global img_height
	global img_width

	# Setup OpenCV
	face_detect = cv.CascadeClassifier(cv.data.haarcascades + 'haarcascade_frontalface_alt2.xml')

	# Setup Tensorflow Inference Model
	interpreter = Interpreter(model_path="model.tflite")
	interpreter.allocate_tensors()
	input_details = interpreter.get_input_details()
	output_details = interpreter.get_output_details()

	while run_program:
		is_andrew_present = False

		# Run Ultrasound Camera Loop
		tmp = camera_manager()

		if tmp:
			# Load captured image to memory
			cv_img = cv.imread(im_path)
			# Format the image for face detection
			gray = cv.cvtColor(cv_img, cv.COLOR_BGR2GRAY)
			# Detect if there are faces in the image
			faces = face_detect.detectMultiScale(gray, 1.1, 4)

			# For all faces in the image check if they're Andrew
			face_count = 0
			for (x, y, w, h) in faces:
				face_count += 1
				faces = cv_img[y:y+h, x:x+w]

				# Prepare individual face image for Tensorflow Inference
				faces = np.array(faces, dtype='float')
				faces = cv.resize(faces, (img_height, img_width), interpolation=cv.INTER_CUBIC)
				cv.imwrite('tmp/tmp_' + str(face_count) + '.jpg', faces)

				# Note: The write and read of the face image to and from disk is not very
				# efficient or necessary. However, I have I kept it for debug purposes
				tmp_img = Image.open('tmp/tmp_' + str(face_count) + '.jpg')
				tmp_img = np.array(tmp_img, dtype=np.float32)

				# Convert face image to input tensor for inference
				interpreter.set_tensor(input_details[0]['index'], tmp_img[None,:,:])
				interpreter.invoke()
				# Predict if the face is Andrew or No using the trained ResNet50
				output_data = interpreter.get_tensor(output_details[0]['index'])
				# Returns the % of confidence that it is Andrew's Face
				andrew = round(float(output_data[0][0]) * 100, 2)
				# Returns the % of confidence that it is not Andrew's Face
				not_andrew = round(float(output_data[0][1]) * 100, 2)
				print("Prediction: " + str(andrew) + ", " + str(not_andrew))
				# If its Andrew, do something, else do something else
				if andrew >= not_andrew:
					# print("Face " + str(face_count) + ": Andrew")
					cv.rectangle(cv_img, (x, y), (x+w, y+h), green, 2)
					cv.putText(cv_img,
						'Andrew: ' + str(andrew) + '%',
						(x, y-10),
						cv.FONT_HERSHEY_SIMPLEX,
						0.9, green, 2)
					is_andrew_present = True
				else:
					cv.rectangle(cv_img, (x, y), (x+w, y+h), red, 2)
					cv.putText(cv_img,
						'Intruder: ' + str(not_andrew) + '%',
						(x, y-10),
						cv.FONT_HERSHEY_SIMPLEX,
						0.9, red, 2)
					# print("Face " + str(face_count) + ": Not Andrew")

			# Write the photo with labeled faces to disk
			cv.imwrite('tmp/tmp_detect.jpg', cv_img)

			# Write file to log and write to SQLite DB
			d = datetime.today().strftime('%Y-%m-%d')
			t = datetime.today().strftime('%H:%M:%S')
			s = datetime.today().strftime('%s')
			log_file_name = d + '_im' + s + '.jpg'

			# Save image to database
			cv.imwrite(log_dir + log_file_name, cv_img)

			# Write to DB in format: Date, Time, Face Count, Was Andrew detected?, image file path
			db.insert_entry(d, t, face_count, is_andrew_present, log_file_name)
			time.sleep(3)

		else:
			# If there is an error with the Ultrasound end program
			print("There is an error with the Ultrasound Sensor.")
			sys.exit(1)


# If the system is shutting down
def stop_program(sig, frame):
	global run_program
	run_program = False


# Clean up files that are no longer needed
def clean_cache():
	f = glob.glob("tmp/tmp*.jpg")
	for file in f:
		os.remove(file)


# Provide canonical program entry point
if __name__ == "__main__":
	signal.signal(signal.SIGTERM, stop_program)
	main_program()
	# End program
	clean_cache()
	sys.exit(0)

