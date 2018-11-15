from flask import render_template, redirect, url_for, request, session
from app import webapp
import random
from app import sql
from app import config
import boto3

# to delete all data in mysql database
@webapp.route("/sql_del",methods = ["GET","POST"])
def Del():
    # delete S3
    cnx = sql.get_db()
    cursor = cnx.cursor()
    query_0 = "SELECT userName FROM userInfo"
    cursor.execute(query_0)
    row = cursor.fetchall()
    name_list = []
    for i in range(len(row)):
        name_list.append(row[i][0])
    delete_only(name_list)    
    # delete mysql
    
    query_1 = "DELETE FROM user2Images"
    query_2 = "DELETE FROM userInfo"
    cursor.execute(query_1)
    cursor.execute(query_2)

    session['error'] = 'all data in database has been deleted!'
    return redirect(url_for('manager'))


def delete_only(user_list):
    for i in user_list:
        s3 = boto3.resource('s3')
        bucket = s3.Bucket(config.s3_bucketname)

        objects_to_delete = []
        filename = i+'/'
        for obj in bucket.objects.filter(prefix = filename):
            objects_to_delete.append({'Key': obj.key})

        bucket.delete_objects(
            Delete={
                'Objects': objects_to_delete
            }
        )