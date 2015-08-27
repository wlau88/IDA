"""
Script for loading metadata table into MongoDB using the InstagramMetadata 
class. metadata table: photo_id, media_object
"""
import instagram_metadata
import sys
import pdb
import pickle
import time

if __name__ == '__main__':
	"""
	Command line execution

	:param min_timestamp: return media metadata after this timestamp (UNIX time)
	:return:
	"""
	locations_list_fname = sys.argv[1]
	index = int(sys.argv[2])
	min_timestamp = sys.argv[3]

	with open(locations_list_fname, 'r') as f:
		locations_list = pickle.load(f)

	ig_client = instagram_metadata.InstagramMetadata('instagram_api_info.txt')

	missed_locations_list = ig_client.get_metadata_from_location_table(locations_list, 
																	   index, min_timestamp)

	with open('missed_locations_list' + str(time.time()) + '.pkl', 'w') as f:
		pickle.dump(missed_locations_list, f)
		"Dumping missed locations"