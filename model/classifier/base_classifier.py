from abc import ABCMeta, abstractmethod

class BaseClassifier(object):
	"""Abstract class for classifying age and gender

	Parameters:
	-----------
	"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def fit(self, x, y):
		"""Abstract fit method

		:param x: feature matrix as numpy array
		:param y: class labels as numpy array
		:return:
		"""
		pass


	@abstractmethod
	def predict(self, x):
		"""Abstract predict method to predict the classes

		:param x: feature matrix as numpy array
		:return:
		"""
		pass


	@abstractmethod
	def predict_proba(self, x):
		"""Abstract predict method to give the probabilities
		of the prediction of the classes

		:param x: feature matrix as numpy array
		:return:
		"""
		pass

