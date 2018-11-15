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
    delete()    # delete mysql
    
    query_1 = "DELETE FROM user2Images"
    query_2 = "DELETE FROM userInfo"
    cursor.execute(query_1)
    cursor.execute(query_2)

    session['error'] = 'all data in database has been deleted!'
    return redirect(url_for('manager'))


def delete():
    client = boto3.client('s3')
    paginator = client.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=config.s3_bucketname)

    delete_us = dict(Objects=[])
    for item in pages.search('Contents'):
        delete_us['Objects'].append(dict(Key=item['Key']))

        # flush once aws limit reached
        if len(delete_us['Objects']) >= 1000:
            client.delete_objects(Bucket=bucket, Delete=delete_us)
            delete_us = dict(Objects=[])

    # flush rest
    if len(delete_us['Objects']):
        client.delete_objects(Bucket=bucket, Delete=delete_us)