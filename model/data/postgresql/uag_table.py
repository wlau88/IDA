"""
Script for extracting the userid_age_gender (UAG) table from the 
age and gender table in MongoDB. Stores the userid_age_gender (UAG) table 
in PostgreSQL. 
"""
from pymongo import MongoClient 
import psycopg2
import sys
import pdb
import numpy as np

def create_UAG_table_in_sql(sql_cursor):
    """Create the UAG table

    :param sql_cursor: cursor to the UAG table in PostgreSQL
    :return:
    """
    sql_cursor.execute('''DROP TABLE IF EXISTS uag_complete;''')
    sql_cursor.execute(
        '''CREATE TABLE uag_complete (
            _id integer PRIMARY KEY,    
            user_id varchar(50),
            age_bucket varchar(20),
            age_avg varchar(20),
            gender_bucket varchar(20),
            source varchar(30));
        ''')


def fill_UAG_table_in_sql(mongo_age_gender_table, sql_cursor):
    """Consolidate the age_gender information from the age_gender table in MongoDB 
    and fill in the UAG table in PostgreSQL 

    :param mongo_table: the age_gender table in MongoDB
    :param sql_cursor: cursor to the UAG table in PostgreSQL
    :return:
    """
    userid_list = []
    for age_gender_record in mongo_age_gender_table.find():
        userid_list.append(age_gender_record['id'])

    unique_userid_list = list(set(userid_list))

    # pdb.set_trace()
    error_log = []

    _id = 0
    for userid in unique_userid_list:
        #fields to be filled in
        final_age_pred_list = []
        final_gender_pred_list = []
        final_source_list = ''
        #first look for tagged pic record
        try:
            # pdb.set_trace()
            tagged_record = mongo_age_gender_table.find({'$and': [{'id': userid}, 
                                                        {'type': 'tagged_pic'}]})[0]
            # pdb.set_trace()
            # if len(list(tagged_record)) > 1:
            #     print "Duplicate userid and type"
            #     error_log.append((userid, 'tagged_record > 1'))

            # else:
            for age_pred in tagged_record['age_predictions']:
                final_age_pred_list.append(age_pred)
            for gender_pred in tagged_record['gender_predictions']:
                final_gender_pred_list.append(gender_pred)
            final_source_list += 'tagged_pic'
            
        except Exception, e:
            # pdb.set_trace()
            print "Exception: ", str(e)
            print "No tagged pic for this userid: ", userid
        #now look for profile pic record
            try:
                # pdb.set_trace()
                profile_record = mongo_age_gender_table.find({'$and': [{'id': userid}, 
                                                             {'type': 'profile_pic'}]})[0]
                # test = list(profile_record)
                # pdb.set_trace()

                # if len(list(profile_record)) > 1:
                #     print "Duplicate userid and type"
                #     error_log.append(userid)

                # else:
                if len(profile_record['age_prediction']) == 8:
                    #correct
                    age_pred = profile_record['age_prediction']
                    #twice the weight
                    final_age_pred_list.append(age_pred)
                    final_age_pred_list.append(age_pred)
                else:
                    #incorrect
                    print "Age predictions of profile pic corrupted"
                    error_log.append((userid, 'age_pred of profile pic corrupted'))
                if len(profile_record['gender_prediction']) == 2:
                    #correct
                    gender_pred = profile_record['gender_prediction']
                    #twice the weight
                    final_gender_pred_list.append(gender_pred)
                    final_gender_pred_list.append(gender_pred)
                else:
                    #incorrect
                    print "Gender predictions of profile pic corrupted"
                    error_log.append((userid, 'gender_pred of profile pic corrupted'))
                final_source_list += 'profile_pic'

            except Exception, e:
                # pdb.set_trace()
                print "Exception: ", str(e)
                print "No profile pic for this userid: ", userid
                continue

        age_buckets = ['(0, 2)','(4, 6)','(8, 12)','(15, 20)','(25, 32)',
                      '(38, 43)','(48, 53)','(60, 100)']
        age_floats = [1., 5., 10., 17.5, 28.5, 40.5, 51.5, 80]
        
        gender_buckets = ['Male','Female']

        if len(final_age_pred_list) == 1:
            age_bucket = age_buckets[np.array(final_age_pred_list).argmax()]
            age_avg = np.dot(final_age_pred_list, age_floats)

        elif len(final_age_pred_list) > 1:
            final_age_pred = np.array(final_age_pred_list).mean(axis=0)
            age_bucket = age_buckets[final_age_pred.argmax()]
            age_avg = np.dot(final_age_pred, age_floats)

        if len(final_gender_pred_list) == 1:
            gender_bucket = gender_buckets[np.array(final_gender_pred_list).argmax()]

        elif len(final_gender_pred_list) > 1:
            final_gender_pred = np.array(final_gender_pred_list).mean(axis=0)
            gender_bucket = gender_buckets[final_gender_pred.argmax()]

        # pdb.set_trace()
        user_id = userid
        age_bucket = str(age_bucket)
        age_avg = str(age_avg)
        gender_bucket = str(gender_bucket)
        source = str(final_source_list)

        # pdb.set_trace()
        _id += 1
        sql_cursor.execute(
            '''INSERT INTO uag_complete VALUES (%d, '%s', '%s', '%s', '%s', '%s');'''\
            % (_id, user_id, age_bucket, age_avg, gender_bucket, source))
        print "Inserting record for userid: ", user_id

        # pdb.set_trace()

if __name__ == '__main__':
    """
    Command line execution

    """
    mongo_client = MongoClient(port=6969)

    age_gender_table = mongo_client['instagram_143915599715772']['age_gender']

    conn = psycopg2.connect(dbname='instagram', user='postgres')
    sql_cursor = conn.cursor()
    print 'PostgreSQL Connection established'

    create_UAG_table_in_sql(sql_cursor)
    print 'Created UAG table'

    fill_UAG_table_in_sql(age_gender_table, sql_cursor)
    print 'Filled UAG table'

    conn.commit()
    conn.close()
    print 'PostgreSQL Connection closed'

