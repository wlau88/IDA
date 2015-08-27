from image_processor import FaceDetectorProcessor, CropImageProcessor
from face_detector import FaceDetector
from base_image_classifier import BaseImageClassifier
import numpy as np
import caffe
import requests
import cv2

import pdb


class InstagramImageClassifier(BaseImageClassifier):
    """Classify an Instagram image using the image_processor for 
    preprocessing then using the given classifier for classification

    Parameters:
    -----------
    image_processor: an ImageProcessor that processes the image
    clf: a classifier that classifies the image

    """
    def __init__(self, clf, image_processor=FaceDetectorProcessor()):
        self._image_processor = image_processor
        self._clf = clf


    def classify(self, x):
        """Dummy method to override BaseImageClassifier classify method

        """
        pass


    def classify_tagged_photo(self, image_metadata):
        """Classifies faces in a tagged photo

        Uses the CropImageProcessor to crop the image, passes it on to
        the image_processor then use the clf to classify the image

        :param image_metadata: metadata of the image 
        :return: classification result ([] if 'Content not found')

        """
        imageFile = requests.get(image_metadata['images']\
                                 ['standard_resolution']['url']).content
        
        if imageFile == 'Content not found':
            return []

        fout = open('temp.jpg', 'w')
        fout.write(imageFile)
        fout.close()

        image = cv2.imread('temp.jpg')
        height, width, channels = image.shape 
        users_tagged = image_metadata['users_in_photo']

        url = image_metadata['images']['standard_resolution']['url']
        try:
            photo_id = url[url.rindex('cdninstagram.com')+17:].replace('/', '@') 
        except:
            photo_id = url[url.rindex('https://')+9:].replace('/', '@') 

        markers_list = [] #list of tagged position markers
        clf_results = [] #list of classification results    

        for user in users_tagged:
            user_id = user['user']['id']

            y_coord = float(user['position']['y']) * height
            x_coord = float(user['position']['x']) * width

            crop_processor = CropImageProcessor((x_coord, y_coord), tagged_radius=100)
            cropped_square = crop_processor.process_image(image)
            cropped_face, face_in_square = self._image_processor.process_image(cropped_square)

            try:
                if face_in_square:
                    #stores it in directory
                    fname = self._image_processor.save_image(image=cropped_face, 
                                                             user_id=user_id,
                                                             photo_id=photo_id)
                    input_image = caffe.io.load_image(fname)
                    clf_results.append((user_id, photo_id, self._clf(input_image)))
            except Exception, e:
                print str(e)
                
        return clf_results


    def classify_profile_photo(self, image_metadata):
        """Classifies the face in a profile photo

        Uses the CropImageProcessor to crop the image, passes it on to
        the image_processor then use the clf to classify the image

        :param image_metadata: metadata of the image 
        :return: classification result ([] if 'Content not found')

        """
        url = image_metadata['user']['profile_picture']
        imageFile = requests.get(url).content
        
        if imageFile == 'Content not found':
            return []

        fout = open('temp.jpg', 'w')
        fout.write(imageFile)
        fout.close()

        image = cv2.imread('temp.jpg')
        height, width, channels = image.shape 

        photo_id = url[url.rindex('https://')+9:].replace('/', '@') 

        clf_results = [] #list of classification results    

        user_id = image_metadata['user']['id']

        #####Optimized parameters after model tuning
        face_detector = FaceDetector('haarcascade_frontalface_default.xml', 
                                     1.1, 1, (20,20))
        face_detector_processor = FaceDetectorProcessor()
        face_detector_processor.detector = face_detector

        self._image_processor = face_detector_processor
        #####

        cropped_face, face_in_square = self._image_processor.process_image(image)

        try:
            if face_in_square:
                #stores it in directory
                fname = self._image_processor.save_image(image=cropped_face, 
                                                         user_id=user_id,
                                                         photo_id=photo_id)
                input_image = caffe.io.load_image(fname)
                clf_results.append((user_id, photo_id, self._clf(input_image)))
        except Exception, e:
            print str(e)
                
        return clf_results