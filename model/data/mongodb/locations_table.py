"""
Script for loading locations table into MongoDB using the InstagramMetadata 
class. locations table: location_id, lat, lng, location_name
"""
import instagram_metadata
import sys
import pdb

if __name__ == '__main__':
	"""
	Command line execution

	:param top_l: 1st and 2nd arg = (lat, lng) of the top left corner
    :param top_r: 3rd and 4th arg = (lat, lng) of the top right corner
    :param bottom_l: 5th and 6th arg = (lat, lng) of the bottom left corner
    :param bottom_r: 7th and 8th arg = (lat, lng) of the bottom right corner
    :param lat_interval: 9th arg = number of lat intervals
    :param lng_interval: 10th arg = number of lng intervals
    :param distance: 11th arg = distance to search within
	:return: 
	"""
	top_l = (float(sys.argv[1]), float(sys.argv[2])) 
	top_r = (float(sys.argv[3]), float(sys.argv[4]))
	bottom_l = (float(sys.argv[5]), float(sys.argv[6]))
	bottom_r = (float(sys.argv[7]), float(sys.argv[8]))
	lat_interval = int(sys.argv[9])
	lng_interval = int(sys.argv[10])
	distance = int(sys.argv[11])

	pdb.set_trace()

	ig_client = instagram_metadata.InstagramMetadata('instagram_api_info.txt')

	ig_client.get_locations_from_grid(top_l, top_r, bottom_l, bottom_r, 
                                	  lat_interval, lng_interval, 
                                	  distance)