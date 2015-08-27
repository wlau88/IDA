"""
Script for extracting media metadata table in MongoDB, doing age and gender 
classification using the classes in the caffe_classifier and image_classifier
scripts, and loading the age_gender table into MongoDB. age_gender table: user_id,
age_predictions, gender_predictions
"""
from pymongo import MongoClient, errors
import model.classifier.caffe_classifier
import model.classifier.image_classifier
import cv2
import sys
import pdb
import multiprocessing as mp
import pickle
import math


def multiprocess_image_clf(client, database, age_gender_table, image_classifier_age, image_classifier_gender, 
   metadata_list):
  """Classifies the profile photo(s) and tagged faces associated with the
  image metadata

  :param mongo_client: MongoDB client to use
  :param img_age_clf: Age image classifier to use
  :param img_gender_clf: list(Gender image clas)sifier to use 
  :param img_metadata: list of metadata id's
  """
   # = package

  metadata_table = database['metadata']
  i = 0
  for metadata_id in metadata_list:
    flag = metadata_table.find_one({'id': metadata_id})
    try: 
        flag['completed']
    except KeyError:
        i += 1
        print i
        # pdb.set_trace()
        if len(list(metadata_table.find({'id': metadata_id}))) > 1:
            # pdb.set_trace()
            "print metadata_id not unique!!"
            break

        metadata = list(metadata_table.find({'id': metadata_id}))[0]

        #getting age and gender of the user_id of the profile photo
        user_id = metadata['user']['id']
        
        if not age_gender_table.find_one({'$and': [{'id': user_id}, {'type': 'profile_pic'}]}):
        #go through detection only if the user_id is not already in db

            try:
                raw_age_prediction = image_classifier_age.classify_profile_photo(metadata)[0]
                raw_gender_prediction = image_classifier_gender.classify_profile_photo(metadata)[0]

                _, source, age_prediction = raw_age_prediction
                _, _, gender_prediction = raw_gender_prediction

                doc = {'id': user_id, 'type': 'profile_pic', 
                       'age_prediction': list(age_prediction.astype(float)),
                       'gender_prediction': list(gender_prediction.astype(float)), 
                       'source': source}

                try:
                    print "Inserting profile pic classification of user_id: " + user_id
                    # pdb.set_trace()
                    age_gender_table.insert(doc)
                except errors.DuplicateKeyError:
                    print "Duplicate"

            except Exception, e:
                print "No face found"
                print str(e)

        #getting age and gender of the tagged user_id's in the tagged photo
        if len(metadata['users_in_photo']) > 0:
        #go through only if there are tagged spots in the photo
            raw_age_predictions = image_classifier_age.classify_tagged_photo(metadata)
            raw_gender_predictions = image_classifier_gender.classify_tagged_photo(metadata)

            for raw_age_pred, raw_gender_pred in zip(sorted(raw_age_predictions), 
                                             sorted(raw_gender_predictions)):
                user_id, source, age_prediction = raw_age_pred                                             
                _, _, gender_prediction = raw_gender_pred

                if not age_gender_table.find_one({'$and': [{'id': user_id}, 
                                                           {'type': 'tagged_pic'}]}):
                #if there are no tagged_pic classification for user_id, start one
                    doc = {'id': user_id, 'type': 'tagged_pic',
                           'age_predictions': [list(age_prediction.astype(float))],
                           'gender_predictions': [list(gender_prediction.astype(float))],
                           'source': [source]}

                    try:
                        print "Inserting tagged pic classification \
                               of user_id: " + user_id
                        age_gender_table.insert(doc)
                    except errors.DuplicateKeyError:
                        print "Duplicate"

                else: #i.e. there are tagged_pic classification for user_id
                    print "Updating tagged pic classification of user_id: " \
                          + user_id
                    age_gender_table.update({'$and': [{'id': user_id}, 
                                            {'type': 'tagged_pic'}]},
                                            {'$push': {'age_predictions': list(age_prediction.astype(float))}})
                    age_gender_table.update({'$and': [{'id': user_id}, 
                                            {'type': 'tagged_pic'}]},
                                            {'$push': {'gender_predictions': list(gender_prediction.astype(float))}})
                    age_gender_table.update({'$and': [{'id': user_id}, 
                                            {'type': 'tagged_pic'}]},
                                            {'$push': {'source': source}})

        print "Marking metadata_id " + metadata['id'] + " complete"
        metadata_table.update({'id': metadata_id}, {'$set': {'completed': True}})



def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

if __name__ == '__main__':
    """Command line execution

    :param n_cores: number of cores available 
    :param metadata_list: list of metadata_id's
    :return:
    """
    metadata_list_fname = sys.argv[1]
    n_cores = int(sys.argv[2])
    # missed_metadata_id_list = []

    with open(metadata_list_fname, 'r') as f:
        metadata_list = pickle.load(f)
        # pdb.set_trace()

    chunk_size = int(math.ceil(float(len(metadata_list))/n_cores))

    chunk_gen = chunks(metadata_list, chunk_size)

    args_list = []
    for i in xrange(n_cores):
      #setting up database cursors
        client = MongoClient(host='ip-172-31-12-7.ec2.internal', port=6969)
        database = client['instagram_143915599715772'] #TO BE CHANGED
        age_gender_table = database['age_gender']
        #setting up age and gender classifier, image classifier defaults to face detector
        clf_age = caffe_classifier.CaffeAgeNet()
        clf_gender = caffe_classifier.CaffeGenderNet()
        image_classifier_age = image_classifier.InstagramImageClassifier(clf_age.predict_proba)
        image_classifier_gender = image_classifier.InstagramImageClassifier(clf_gender.predict_proba)
        args_list.append((client, database, age_gender_table, image_classifier_age,
                          image_classifier_gender, next(chunk_gen)))
        # pdb.set_trace()

    processes = [mp.Process(target=multiprocess_image_clf, args=(i)) for i in args_list]

    for p in processes:
        p.start()

    for p in processes:
        p.join()
   
