from abc import ABCMeta, abstractmethod

class BaseImageClassifier(object):
	"""Abstract class for an ImageClassifier

	Parameters:
	-----------
	"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def classify(self, x, *args):
		"""Abstract classify method

		:param x: feature to be classified
		:return: classification result
		"""
		pass