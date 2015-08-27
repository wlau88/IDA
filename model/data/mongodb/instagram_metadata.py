import requests
from base_metadata import BaseMetadata
from instagram.client import InstagramAPI
import os
import pdb
import numpy as np
from pymongo import MongoClient, errors
import time
from itertools import cycle


class InstagramMetadata(BaseMetadata):
    """Interacts with InstagramAPI to get metadata

    Loads metadata into MongoDB. Make sure MongoDB is running. Use "sudo
    mongod" in terminal

    Parameters:
    -----------
    - api_key_fname = filename containing api key token information, 
    specifically access token and client secret, in a text file. Each
    token should be on a seperate row in the format of access token
    and client secret separated by a comma

    """
    def __init__(self, api_key_fname):
        self._api_dict, self._api_tokens_dict = self._set_up_api_dict(api_key_fname)
        #_api_dict is a dictionary of api's
        #_api_tokens_dict is a dictionary of api access token and client secret
        client = MongoClient(port=6969)
        self.database = client['instagram_143915599715772'] #TO BE CHANGED
        self.location_table = self.database['location']
        self.metadata_table = self.database['metadata']


    def insert_into_mongodb(self, table, obj):
        """Inserts instagram object into MongoDB instagram database

        :param table: name of table, 'location' or 'metadata'
        :return:
        """
        if not self.database[table].find_one({'id': obj['id']}):
            try:
                print "Inserting obj " + obj['id']
                self.database[table].insert(obj)
            except errors.DuplicateKeyError:
                print "Duplicate"
        else:
            print "In collection already"


    def _set_up_api_dict(self, api_key_fname):
        """Ensure the api_key_fname is valid, set up the api_dict
        
        :param api_key_fname: file containing api key token info
        :return: tuple of dictionary of api's and dictionary of api access
        token and client secret
        """
        cwd = os.path.dirname(__file__) #gets current directory

        api_tokens_path = os.path.join(cwd, 'api_key_tokens', api_key_fname)
        
        #check for validity of path input
        if not os.path.exists(api_tokens_path):
            err_msg = '%s does not exist!' % api_key_fname
            err_msg.format(api_key_fname)
            # pdb.set_trace()
            raise IOerror(err_msg)

        api_dict, api_tokens_dict = dict(), dict() #1 indexing 
        i = 0

        with open(api_tokens_path, "r") as f:
            for line in f:
                i += 1
                [access_token, client_secret] = line.split(',')
                api_tokens_dict[i] = dict()
                api_tokens_dict[i]['access_token'] = access_token 
                api_tokens_dict[i]['client_secret'] = client_secret
                api_dict[i] = InstagramAPI(access_token=access_token, 
                                           client_secret=client_secret)

        return api_dict, api_tokens_dict


    def get_locations_from_grid(self, top_l, top_r, bottom_l, bottom_r,
                                lat_interval=10, lng_interval=10, 
                                distance=5000):
        """Get location_id's from a grid (rectangle). lng of top_l and bottom_l, 
        top_r and bottom_r should be the same, likewise for lat of bottom_r and 
        top_r, bottom_l and top_l. Stores them in the 'location' table in the 
        instagram MongoDB

        :param top_l: (lat, lng) of the top left corner
        :param top_r: (lat, lng) of the top right corner
        :param bottom_l: (lat, lng) of the bottom left corner
        :param bottom_r: (lat, lng) of the bottom right corner
        :param lat_interval: number of lat intervals, defaults to 10
        :param lng_interval: number of lng intervals, defaults to 10
        :param distance: distance to search within, defaults to 5000m
        :return: 
        """
        api_generator = cycle(list(self._api_dict.itervalues()))

        api = next(api_generator)

        for lat in np.linspace(bottom_r[0], top_r[0], lat_interval):
            for lng in np.linspace(top_l[1], top_r[1], lng_interval):
                try:
                    locations_covered = api.location_search(lat=lat, lng=lng, 
                                                            distance=distance)
                    if len(locations_covered) > 0:
                        for location in locations_covered:
                            location_d = location.__dict__
                            location_d['point'] = location_d['point'].__dict__
                            self.insert_into_mongodb('location', location_d)
                    continue
                except Exception, e:
                    print 'Exception: ', str(e)
                    print '@API client: ', api
                    print '@lat, lng: ', (lat, lng)
                    api = next(api_generator)
                    locations_covered = api.location_search(lat=lat, lng=lng, 
                                                            distance=distance)
                    if len(locations_covered) > 0:
                        for location in locations_covered:
                            self.insert_into_mongodb('location', location.__dict__)
                    continue


    def get_metadata_from_location_table(self, locations_list, index, min_timestamp):
        """Get metadata of photos tagged at the locations from the 
        location table. Stores them in the 'metadata' table in the 
        instagram MongoDB 

        :param locations_list: list of MongoDB locations from the locations table
        :param index: index of list to start to scrap from
        :param min_timestamp: return media metadata after this timestamp
        :return: list of missed locations in a tuple of index, location_id
        """
        api_tokens_generator = cycle(list(self._api_tokens_dict.itervalues()))
        locations = locations_list
        i = index
        missed_locations_list = []

        access_token = next(api_tokens_generator)['access_token']

        for location in locations[i:]:
            access_token = next(api_tokens_generator)['access_token']
            i += 1
            print i
            location_id = location['id']
            #check if medias of the location is less than 10 
            if len(list(self.metadata_table.find({'location.id': location_id}))) < 10:
                try:
                    r = requests.get('https://api.instagram.com/v1/locations/' + 
                                     location_id + '/media/recent?access_token=' + 
                                     access_token + '&min_timestamp=' + 
                                     min_timestamp)
                    try:
                        # pdb.set_trace()
                        for media_data in r.json()['data']:
                            self.insert_into_mongodb('metadata', media_data)
                    except Exception, e:
                        # pdb.set_trace()
                        print 'Exception: ', str(e)
                        print '@location_id: ', location_id
                        print '@time: ', str(time.time())
                        print '@index: ', i
                        missed_locations_list.append((i, location_id))
                        continue
                
                except Exception, e:
                    # pdb.set_trace()
                    print 'Exception: ', str(e)
                    print '@access_token: ', access_token 
                    print '@location_id: ', location_id
                    print '@time: ', str(time.time())
                    print 'next access token'
                    access_token = next(api_tokens_generator)['access_token']

                    r = requests.get('https://api.instagram.com/v1/locations/' + 
                                     location_id + '/media/recent?access_token=' + 
                                     access_token + '&min_timestamp=' + 
                                     min_timestamp)
                    try:
                        for media_data in r.json()['data']:
                            self.insert_into_mongodb('metadata', media_data)
                    except Exception, e:
                        print 'Exception: ', str(e)
                        print '@location_id: ', location_id
                        print '@time: ', str(time.time())
                        print '@index: ', i
                        missed_locations_list.append((i, location_id))
                        continue

        return missed_locations_list

