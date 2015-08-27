"""
Script for tuning face_detector
"""
from image_processor import FaceDetectorProcessor, CropImageProcessor
from face_detector import FaceDetector
import sys
from pyimage import pipeline
import pdb
from skimage import io
import cv2
import matplotlib.pyplot as plt
import numpy as np
import requests
import pickle
from pymongo import MongoClient


def profile_face_clf(img_lst, cascade_file, scale_factor, min_neighbors, min_size):
    """Classifies face based on profile image

    :param img_lst: list of image objects with profile image
    :param cascade_file, scale_factor, min_neighbors, min_size: tuning parameters
    :return pred_lst: list of predictions (face or not)
    """
    pred_lst = []

    i = 0

    for img_obj in img_lst:

        image = img_obj['face_img']
        
        face_detector = FaceDetector(cascade_file, scale_factor, min_neighbors, 
                                     min_size)
        face_detector_processor = FaceDetectorProcessor()
        face_detector_processor.detector = face_detector
        cropped_face, face_in_square = face_detector_processor.process_image(image)

        i += 1
        print "Inserting prediction result ", i
    
        pred_lst.append(face_in_square)

    return pred_lst


def tune_profile_face_clf(img_d):
    """Performs tuning on CropImageProcessor and FaceDetector

    :param img_d: image dictionary
    :return:
    """
    cascade_files_list = ['haarcascade_frontalface_default.xml', 
                          'haarcascade_frontalface_alt.xml',
                          'haarcascade_frontalface_alt2.xml',
                          'haarcascade_frontalface_alt_tree.xml',
                          'haarcascade_profileface.xml']

    scale_factor_list = [1.01, 2, 3]
                 
    min_neighbors_list = [1, 5, 9] 

    min_size_list = [(i,i) for i in np.arange(0, 60, 20)]

    crop_radius_list = [100, 150, 200]

    grid = {'cascade_file': cascade_files_list,
           'scale_factor': scale_factor_list,
           'min_neighbors': min_neighbors_list,
           'min_size': min_size_list,
           'crop_radius': crop_radius_list}

    img_lst = list(img_d.itervalues())
    grid_search_results = []

    client = MongoClient()
    db = client['instagram']
    table = db['profile_face_tuning']

    for cascade_file in cascade_files_list:
        for scale_factor in scale_factor_list:
            for min_neighbors in min_neighbors_list:
                for min_size in min_size_list:
                    pred_lst = profile_face_clf(img_lst, cascade_file, 
                                                scale_factor, min_neighbors, 
                                                min_size)

                    d = {'cascade_file': cascade_file,
                         'scale_factor': scale_factor,
                         'min_neighbors': min_neighbors,
                         'min_size': min_size,
                         'pred_lst': pred_lst}
                    
                    print "Inserting results into MongoDB"
                    table.insert(d)


def tagged_face_clf(img_lst, cascade_file, scale_factor, min_neighbors, min_size,
                    crop_radius):
    """Classifies face based on full image and crop position

    :param img_lst: list of image objects with full image and crop 
    position information
    :param cascade_file, scale_factor, min_neighbors, min_size,
    crop_radius: tuning parameters
    :return pred_lst: list of predictions (face or not)
    """
    pred_lst = []

    i = 0

    for img_obj in img_lst:

        image = img_obj['full_img']
        
        if image == None:
            face_in_square = None

        else:
            pos_x = img_obj['crop_pos'][0]
            pos_y = img_obj['crop_pos'][1]

            height, width, channels = image.shape

            x_coord = float(pos_x) * width
            y_coord = float(pos_y) * height

            crop_processor = CropImageProcessor((x_coord, y_coord), 
                                                 tagged_radius=crop_radius)
            cropped_square = crop_processor.process_image(image)
            face_detector = FaceDetector(cascade_file, scale_factor, min_neighbors, 
                                         min_size)
            face_detector_processor = FaceDetectorProcessor()
            face_detector_processor.detector = face_detector
            cropped_face, face_in_square = face_detector_processor.process_image(cropped_square)

            i += 1
            print "Inserting prediction result", i
        
        pred_lst.append(face_in_square)

    return pred_lst


def tune_tagged_face_clf(img_d):
    """Performs tuning on CropImageProcessor and FaceDetector

    :param img_d: image dictionary
    :return:
    """
    cascade_files_list = ['haarcascade_frontalface_default.xml', 
                          'haarcascade_frontalface_alt.xml',
                          'haarcascade_frontalface_alt2.xml',
                          'haarcascade_frontalface_alt_tree.xml',
                          'haarcascade_profileface.xml']

    scale_factor_list = [1.01, 2, 3]
                 
    min_neighbors_list = [1, 5, 9] 

    min_size_list = [(i,i) for i in np.arange(0, 60, 20)]

    crop_radius_list = [100, 150, 200]

    grid = {'cascade_file': cascade_files_list,
           'scale_factor': scale_factor_list,
           'min_neighbors': min_neighbors_list,
           'min_size': min_size_list,
           'crop_radius': crop_radius_list}

    img_lst = list(img_d.itervalues())
    grid_search_results = []

    client = MongoClient()
    db = client['instagram']
    table = db['tagged_face_tuning']

    for cascade_file in cascade_files_list:
        for scale_factor in scale_factor_list:
            for min_neighbors in min_neighbors_list:
                for min_size in min_size_list:
                    for crop_radius in crop_radius_list:
                        pred_lst = tagged_face_clf(img_lst, cascade_file, 
                                                   scale_factor, min_neighbors, 
                                                   min_size, crop_radius)

                        d = {'cascade_file': cascade_file,
                             'scale_factor': scale_factor,
                             'min_neighbors': min_neighbors,
                             'min_size': min_size,
                             'crop_radius': crop_radius,
                             'pred_lst': pred_lst}
                        
                        print "Inserting results into MongoDB"
                        table.insert(d)


def add_crop_position_info(img_d, metadata_list):
    """Adds crop position information to the image dictionary

    :param img_d: image dictionary
    :param metadata_list: list containing crop position metadata
    :return: image dictionary with crop position information 
    """ 
    #make metadata_d with standard resolution photo url as key
    crop_pos_d = dict()
    for i in metadata_list:
        url = i['images']['standard_resolution']['url']
        for j in i['users_in_photo']:
            position = (j['position']['x'], j['position']['y'])
            user_id = j['user']['id']
            k = (url, user_id)
            crop_pos_d[k] = position

    for fname, v in img_d.iteritems():
        k = fname
        pic_url = k[k.rindex('hp'):].replace('@', '/')
        user_id = k[:k.rindex('hp')]
        url = 'https://scontent.cdninstagram.com/' + pic_url

        imageFile = requests.get(url).content
        
        if imageFile == 'Content not found':
            print "Image not found"
            img_d[fname]['full_img'] = None

        else:
            fout = open('temp_img.jpg', 'w')
            fout.write(imageFile)
            fout.close()

            image = cv2.imread('temp_img.jpg')
            img_d[fname]['full_img'] = image

        img_d[fname]['crop_pos'] = crop_pos_d[(url, user_id)]
        img_d[fname]['img_url'] = url

    return img_d


def check_img_d(img_d):
    """Checks the integrity of image dictionary

    :param img_d: image dictionary
    :return:
    """
    for k,v in img_d.iteritems():
        if v['face'] == True:
            print v['gender'], v['age'], v['face']
        else:
            print v['face']
        io.imshow(v['face_img'])
        plt.show()


if __name__ == '__main__':
    """
    Command line execution

    :param model: model to tune
    :param male_folder: folder of male images with age as subfolder
    :param female_folder: folder of male images with age as subfolder
    :param main_folder: folder with face and not_face as subfolder
    :return:
    """
    # pdb.set_trace()
    model = sys.argv[1]
    male_folder = sys.argv[2]
    female_folder = sys.argv[3]
    main_folder = sys.argv[4]

    #dictionary of image information
    img_d = dict()
    age_bucket = ['adult', 'child', 'senior']

    male_pipe = pipeline.ImagePipeline(male_folder)
    male_pipe.read(['all'])
    male_pipe._vectorize_labels()
    flatten_male_pipe_fnames = [item for sublist in male_pipe.img_names2 for item in sublist]
    flatten_male_imgs = [item for sublist in male_pipe.img_lst2 for item in sublist]
    male_age_labels = male_pipe.labels

    for fname, label, img in zip(flatten_male_pipe_fnames, male_age_labels, 
                                 flatten_male_imgs):
        img_d[fname] = dict()
        img_d[fname]['gender'] = 'male'
        img_d[fname]['age'] = age_bucket[label]
        img_d[fname]['face'] = True
        img_d[fname]['face_img'] = img

    female_pipe = pipeline.ImagePipeline(female_folder)
    female_pipe.read(['all'])
    female_pipe._vectorize_labels()
    flatten_female_pipe_fnames = [item for sublist in female_pipe.img_names2 for item in sublist]
    flatten_female_imgs = [item for sublist in female_pipe.img_lst2 for item in sublist]
    female_age_labels = female_pipe.labels

    for fname, label, img in zip(flatten_female_pipe_fnames, female_age_labels,
                                 flatten_female_imgs):
        img_d[fname] = dict()
        img_d[fname]['gender'] = 'female'
        img_d[fname]['age'] = age_bucket[label]
        img_d[fname]['face'] = True
        img_d[fname]['face_img'] = img

    main_pipe = pipeline.ImagePipeline(main_folder)
    main_pipe.read(['all'])
    main_pipe._vectorize_labels()
    flatten_main_pipe_fnames = [item for sublist in main_pipe.img_names2 for item in sublist]
    flatten_main_imgs = [item for sublist in main_pipe.img_lst2 for item in sublist]

    for fname, img in zip(flatten_main_pipe_fnames, flatten_main_imgs):
        img_d[fname] = dict()
        img_d[fname]['face'] = False
        img_d[fname]['face_img'] = img

    # check_img_d(img_d)

    #adding crop position information
    with open('sf_location_id_lst_media_metadata_8_3_2015_dict_with_usersinphoto_4946outof5010_notkeyedin.pkl', 'r') as f:
        metadata_list = list(pickle.load(f))

    if model == 'tagged_photos':
        img_d_wcrop = add_crop_position_info(img_d, metadata_list)
        gs_tagged_photos_results = tune_tagged_face_clf(img_d_wcrop)
    
        # with('gs_tagged_photos_results.pkl', 'w') as f:
        #     pickle.dump(gs_tagged_photos_results, f)

    elif model == 'profile_photos':
        #check validity of pipe
        # pdb.set_trace()
        gs_profile_photos_results = tune_profile_face_clf(img_d)

        # with('gs_profile_photos_results.pkl', 'w') as f:
        #     pickle.dump(gs_profile_photos_results, f)


    
