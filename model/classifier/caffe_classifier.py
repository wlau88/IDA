from base_classifier import BaseClassifier
import os
import numpy as np
import caffe


class CaffeAgeNet(BaseClassifier):
    """Age prediction class using a Caffe Convolutional
    Neural Network (CNN)

    The class wraps the Caffe CNN

    The user will need to provide the path of the model and the
    configuration. The parameters are defaulted to a pretrained 
    network

    The pretrained CNN is provided from the research of: 
    Gil Levi and Tal Hassner, "Age and Gender Classification Using 
    Convolutional Neural Networks," IEEE Workshop on Analysis and Modeling 
    of Faces and Gestures (AMFG), at the IEEE Conf. on Computer Vision 
    and Pattern Recognition (CVPR), Boston, June 2015

    Parameters:
    -----------
    - model_path: path to the caffe model
    - config_path: path to the configuration
    - mean_img_path: path to the mean image
    - age_list: list of tuples of age buckets, defaults to  
    ['(0, 2)','(4, 6)','(8, 12)','(15, 20)','(25, 32)',
    '(38, 43)','(48, 53)','(60, 100)']  

    """
    def __init__(self, model_path='age_net.caffemodel', 
                 config_path='deploy_age.prototxt',
                 mean_img_path='mean.binaryproto',
                 age_list=['(0, 2)','(4, 6)','(8, 12)','(15, 20)',
                 '(25, 32)','(38, 43)','(48, 53)','(60, 100)']):
        self.model_path = model_path
        self.config_path = config_path
        self.mean_img_path = mean_img_path
        self._set_up_model()
        self.age_list = age_list


    def _set_up_model(self):
        """Ensure the model inputs are valid
        
        :return:
        """
        cwd = os.path.dirname(__file__) #gets current directory

        #gets model, config and mean image info from caffe_model folder
        model_path = os.path.join(cwd, 'caffe_model', self.model_path)
        config_path = os.path.join(cwd, 'caffe_model', self.config_path)
        mean_img_path = os.path.join(cwd, 'caffe_model', self.mean_img_path)
        
        #check for validity of path inputs
        if not os.path.exists(model_path):
            err_msg = '%s does not exist!' % self.model_path
            err_msg.format(self.model_path)
            raise IOerror(err_msg)

        if not os.path.exists(config_path):
            err_msg = '%s does not exist!' % self.config_path
            err_msg.format(self.config_path)
            raise IOerror(err_msg)

        if not os.path.exists(model_path):
            err_msg = '%s does not exist!' % self.mean_img_path
            err_msg.format(self.mean_img_path)
            raise IOerror(err_msg)

        age_net_model = model_path
        age_net_config = config_path
        proto_data = open(mean_img_path, "rb").read()
        a = caffe.io.caffe_pb2.BlobProto.FromString(proto_data)
        age_net_mean_img  = caffe.io.blobproto_to_array(a)[0]

        self.age_net = caffe.Classifier(age_net_config, age_net_model,
                                        mean=age_net_mean_img,
                                        channel_swap=(2,1,0),
                                        raw_scale=255,
                                        image_dims=(256, 256))


    def fit(self, x, y):
        """Dummy method to override BaseClassifier fit method

        """
        pass


    def predict(self, image):
        """Predict the age of the face in the image

        :param image: image of face to predict age (numpy array)
        :return: the predicted age bucket

        """
        prediction = self.age_net.predict([image])
        return self.age_list[prediction[0].argmax()]


    def predict_proba(self, image):
        """The probability of the age prediction of the face in the image

        :param image: image of face to predict age (numpy array)
        :return: the probability of the prediction for each age bucket in the
        model

        """
        prediction = self.age_net.predict([image])
        return prediction[0]


class CaffeGenderNet(BaseClassifier):
    """Gender prediction class using a Caffe Convolutional
    Neural Network (CNN)

    The class wraps the Caffe CNN

    The user will need to provide the path of the model and the
    configuration. The parameters are defaulted to a pretrained 
    network

    The pretrained CNN is provided from the research of: 
    Gil Levi and Tal Hassner, "Age and Gender Classification Using 
    Convolutional Neural Networks," IEEE Workshop on Analysis and Modeling 
    of Faces and Gestures (AMFG), at the IEEE Conf. on Computer Vision 
    and Pattern Recognition (CVPR), Boston, June 2015

    Parameters:
    -----------
    - model_path: path to the caffe model
    - config_path: path to the configuration
    - mean_img_path: path to the mean image
    - gender_list: list of tuples of age buckets, defaults to ['Male','Female']  

    """
    def __init__(self, model_path='gender_net.caffemodel', 
                 config_path='deploy_gender.prototxt',
                 mean_img_path='mean.binaryproto',
                 gender_list=['Male', 'Female']):
        self.model_path = model_path
        self.config_path = config_path
        self.mean_img_path = mean_img_path
        self._set_up_model()
        self.gender_list = gender_list


    def _set_up_model(self):
        """Ensure the model inputs are valid
        
        :return:
        """
        cwd = os.path.dirname(__file__) #gets current directory

        #gets model, config and mean image info from caffe_model folder
        model_path = os.path.join(cwd, 'caffe_model', self.model_path)
        config_path = os.path.join(cwd, 'caffe_model', self.config_path)
        mean_img_path = os.path.join(cwd, 'caffe_model', self.mean_img_path)
        
        #check for validity of path inputs
        if not os.path.exists(model_path):
            err_msg = '%s does not exist!' % self.model_path
            err_msg.format(self.model_path)
            raise IOerror(err_msg)

        if not os.path.exists(config_path):
            err_msg = '%s does not exist!' % self.config_path
            err_msg.format(self.config_path)
            raise IOerror(err_msg)

        if not os.path.exists(model_path):
            err_msg = '%s does not exist!' % self.mean_img_path
            err_msg.format(self.mean_img_path)
            raise IOerror(err_msg)

        gender_net_model = model_path
        gender_net_config = config_path
        proto_data = open(mean_img_path, "rb").read()
        a = caffe.io.caffe_pb2.BlobProto.FromString(proto_data)
        gender_net_mean_img  = caffe.io.blobproto_to_array(a)[0]

        self.gender_net = caffe.Classifier(gender_net_config, gender_net_model,
                                           mean=gender_net_mean_img,
                                           channel_swap=(2,1,0),
                                           raw_scale=255,
                                           image_dims=(256, 256))


    def fit(self, x, y):
        """Dummy method to override BaseClassifier fit method

        """
        pass


    def predict(self, image):
        """Predict the age of the face in the image

        :param image: image of face to predict age (numpy array)
        :return: the predicted age bucket

        """
        prediction = self.gender_net.predict([image])
        return self.gender_list[prediction[0].argmax()]


    def predict_proba(self, image):
        """The probability of the age prediction of the face in the image

        :param image: image of face to predict age (numpy array)
        :return: the probability of the prediction for each age bucket in the
        model

        """
        prediction = self.gender_net.predict([image])
        return prediction[0]
