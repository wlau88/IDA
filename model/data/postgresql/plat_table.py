"""
Script for extracting the photo_location_action_time (PLAT) from the 
media metadata table in MongoDB. Stores the photo_location_action_time (PLAT) table 
in PostgreSQL. 
"""
from pymongo import MongoClient 
import psycopg2
import sys
import pdb

def create_PLAT_table_in_sql(sql_cursor):
    """Create the PLAT table

    :param sql_cursor: cursor to the PLAT table in PostgreSQL
    :return:
    """
    sql_cursor.execute('''DROP TABLE IF EXISTS plat;''')
    sql_cursor.execute(
        '''CREATE TABLE plat (
            _id integer PRIMARY KEY,    
            photo_id varchar(50),
            lat varchar(20),
            lng varchar(20),
            user_id varchar(50),
            action varchar(10),
            time varchar(15));
        ''')


def fill_PLAT_table_in_sql(mongo_metadata_table, sql_cursor):
    """Extract the media information from the metadata table in MongoDB and 
    fill in the PLAT table in PostgreSQL 

    :param mongo_table: the locations table in MongoDB
    :param sql_cursor: cursor to the PLAT table in PostgreSQL
    :return:
    """
    _id = 0

    for media_metadata in mongo_metadata_table.find():
        try:
            # pdb.set_trace()
            photo_id = media_metadata['id']
            lat = '%.7f' % media_metadata['location']['latitude']
            lng = '%.7f' % media_metadata['location']['longitude']
            time = media_metadata['created_time']

            #getting owner
            _id += 1
            user_id = media_metadata['user']['id']
            sql_cursor.execute(
                '''INSERT INTO plat VALUES (%d, '%s', '%s', '%s', '%s', '%s', '%s');'''\
                % (_id, photo_id, lat, lng, user_id, 'own', time))

            #getting liker user_id's
            if len(media_metadata['likes']['data']) == 0:
                pass
            else:
                for like in media_metadata['likes']['data']:
                    _id += 1
                    user_id = like['id']
                    sql_cursor.execute(
                        '''INSERT INTO plat VALUES (%d, '%s', '%s', '%s', '%s', '%s', '%s');'''\
                        % (_id, photo_id, lat, lng, user_id, 'liked', time))

            #getting commenter user_id's
            if len(media_metadata['comments']['data']) == 0:
                pass
            else:
                for comment in media_metadata['comments']['data']:
                    _id += 1
                    user_id = comment['from']['id']
                    sql_cursor.execute(
                        '''INSERT INTO plat VALUES (%d, '%s', '%s', '%s', '%s', '%s', '%s');'''\
                        % (_id, photo_id, lat, lng, user_id, 'commented', time))

            #getting tagged user_id's
            if len(media_metadata['users_in_photo']) == 0:
                pass
            else:
                for tagged_user in media_metadata['users_in_photo']:
                    _id += 1
                    user_id = tagged_user['user']['id']
                    sql_cursor.execute(
                        '''INSERT INTO plat VALUES (%d, '%s', '%s', '%s', '%s', '%s', '%s');'''\
                        % (_id, photo_id, lat, lng, user_id, 'tagged', time))
                
                print "Inserting record"
        except Exception, e:
            print "Exception: ", str(e)
            print "@photo_id: ", photo_id
            # pdb.set_trace()


if __name__ == '__main__':
    """
    Command line execution

    """
    mongo_client = MongoClient(port=6969)

    metadata_table = mongo_client['instagram_143915599715772']['metadata']
    # pdb.set_trace()
    
    conn = psycopg2.connect(dbname='instagram', user='postgres')
    sql_cursor = conn.cursor()
    print 'PostgreSQL Connection established'

    create_PLAT_table_in_sql(sql_cursor)
    print 'Created PLAT table'

    fill_PLAT_table_in_sql(metadata_table, sql_cursor)
    print 'Filled PLAT table'

    conn.commit()
    conn.close()
    print 'PostgreSQL Connection closed'
