import sys
sys.path.append('/usr/local/Cellar/opencv/2.4.11_1/lib/python2.7/site-packages/')
import cv2
import os
import time
from face_detector import FaceDetector
import numpy as np
import pdb


class ImageProcessor(object):
	"""Image processing base class

	Parameters:
	-----------
	"""

	def __init__(self):
		pass


	def process_image(self, image, *args):
		"""Returns the original image

		:param image: image as a numpy array
		:param args:
		:return: the input image
		"""
		return image


	def save_image(self, image):
		"""Saves the image to a temporary directory in the current
		working folder

		:param image: image as a numpy array
		"""
		path = os.path.dirname(__file__)
		path = os.path.join(path, 'tmp')
		if not os.path.exists(path):
			os.mkdir(path)
		fname = os.path.join(path, 'temp' + str(time.time()) + '.jpg')
		cv2.imwrite(fname, image)


class GrayscaleProcessor(ImageProcessor):
	"""Grayscale processing class extending the Image processing
	base class
	Parameters:
	-----------
	"""

	def __init__(self):
		pass


	def process_image(self, image):
		"""Returns the image grayscaled
		:param image: image as a numpy array
		:return: grayscaled image
		"""
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

		return gray


class CropImageProcessor(ImageProcessor):
	"""CropImage processing class extending the Image processing
	base class, crops image based on the center of tagged point and 
	radius of circle enclosed inside the square area
	Parameters:
	-----------
	tagged_center: center of tagged point
	tagged_radius: radius of crop area in pixels
	"""

	def __init__(self, tagged_center, tagged_radius):
		self.tagged_center = tagged_center
		self.tagged_radius = tagged_radius


	def process_image(self, image):
		"""Process the image by cropping the area defined by the 
		tagged_center and tagged_radius
		:param image: image as numpy array
		:return: cropped area of image
		"""
		h = 2 * self.tagged_radius
		w = 2 * self.tagged_radius
		x = self.tagged_center[0] - self.tagged_radius
		y = self.tagged_center[1] - self.tagged_radius

		cropped_face = image[y:y+h, x:x+w] 

		return cropped_face


class FaceDetectorProcessor(ImageProcessor):
	"""FaceDetector processing class extending the Image processing
	base class, attempts to determine if there is a face in the image

	Parameters:
	-----------
	cascade_file: path to the xml cascade classifier parameters

	"""

	def __init__(self, cascade_file='haarcascade_frontalface_default.xml'):
		self.detector = FaceDetector(cascade_file)
		self.preprocessor = GrayscaleProcessor()


	def process_image(self, image):
		"""Process the image by determining if there is a face

		:param image: image as numpy array
		:return: cropped face image, and boolean indicating whether 
		there is a face
		"""
		gray = self.preprocessor.process_image(image)

		face = self.detector.detect_face(gray)

		if len(face) == 0:
			return image, False

		x, y, w, h = face

		cropped_face = image[y:y+h, x:x+w] 

		return cropped_face, True


	def save_image(self, image, user_id, photo_id):
		"""Saves the image to a temporary directory in the current working 
		folder with a concatentation of user_id and photo_id as the filename

		:param image: image as a numpy array
		:param user_id: user_id of the face image
		:param photo_id: photo_id of the original instagram image has .jpg postfix
		:return: file path name
		"""
		path = os.path.dirname(__file__)
		path = os.path.join(path, 'tmp')
		if not os.path.exists(path):
			os.mkdir(path)
		fname = os.path.join(path, str(user_id) + str(photo_id))
		cv2.imwrite(fname, image)
		return fname


