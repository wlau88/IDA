import sys
sys.path.append('/usr/local/Cellar/opencv/2.4.11_1/lib/python2.7/site-packages/')
import cv2
import os

class FaceDetector(object):
	"""Face detection class using openCV CascadeClassifier

	The FaceDetector class wraps the openCV CascadeClassifier. 

	The user will need to provide the path to an xml file with the cascade parameters.

	Parameters:
	-----------
	cascade_file: path to the xml cascade classifier parameters
	scale_factor: float specifying how much the image size is reduced at each image scale
	min_neighbors: int specifying how many neighbors are needed to retain a rectangle
	min_size: int specifying the minimum possible object size

	"""

	def __init__(self, cascade_file, scale_factor=1.1, 
				 min_neighbors=5, min_size=(20,20)):
		self.cascade_file = cascade_file
		self.cascade_classifier = None
		self._set_up_face_detector()

		#Face Detection Parameters
		self.scale_factor = scale_factor
		self.min_neighbors = min_neighbors
		self.min_size = min_size

	
	def _set_up_face_detector(self):
		"""Ensure the face detector input is valid
		
		:return:
		"""
		cwd = os.path.dirname(__file__) #gets current directory
		path = os.path.join(cwd, 'cascade_xmls', self.cascade_file) 
		#gets cascade_xml in cascade_xmls folder
		if not os.path.exists(path):
			err_msg = '%s does not exist!' % self.cascade_file
			err_msg.format(self.cascade_file)
			raise IOerror(err_msg)

		self.cascade_classifier = cv2.CascadeClassifier(path)


	def detect_face(self, image):
		"""Detect face in image

		:param image: image to detect face (numpy array)
		:return: list of tuples of (x, y, w, h) for the largest face found
		"""
		clf = self.cascade_classifier
		faces = clf.detectMultiScale(image,
									 scaleFactor=self.scale_factor,
									 minNeighbors=self.min_neighbors,
									 minSize=self.min_size,
									 flags=cv2.cv.CV_HAAR_SCALE_IMAGE)

		if len(faces) == 0:
			return []

		face_generator = iter(faces)
		largest_face = face_generator.next()
		largest_area = largest_face[2] * largest_face[3]
		for next_face in face_generator:
			next_area = next_face[2] * next_face[3]
			if next_area > largest_area:
				largest_area = next_area
				largest_face = next_face

		return largest_face