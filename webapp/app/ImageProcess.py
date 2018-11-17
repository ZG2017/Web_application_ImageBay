from wand.image import Image
import os
from app import sql
import boto3
from app import config

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# save path info in database
def DBImageSave(userName,thumbnail,original,trans_a,trans_b,trans_c):
    cnx = sql.get_db()
    cursor = cnx.cursor()
    query = ''' INSERT INTO user2Images (userName, Thumbnail, original, trans_a, trans_b, trans_c)
                       VALUES (%s,%s,%s,%s,%s,%s)
    '''
    cursor.execute(query,(userName,thumbnail,original,trans_a,trans_b,trans_c))
    cnx.commit()
    sql.close_db()

# check if file is a image file
def allowed_file(filename):
    return filename.split(".")[-1] in ALLOWED_EXTENSIONS

# save images to local file system
def ImageTransSave(username,filePath,fileName):
    with Image(filename = os.path.join(filePath,fileName)) as img:
        # with img.clone() as i:
        path_origin = os.path.join(filePath,fileName)
        # i.save(filename=path_origin)
        upload_to_s3(path_origin,config.s3_bucketname, '%s/%s' % (username, fileName))
        os.remove(path_origin)
        path_origin = os.path.join(config.S3_ADDRESS,'%s/%s' % (username, fileName))
        with img.clone() as i:
            i.resize(width = 150,height = 100)
            path_thumbnail = os.path.join(filePath,"thumbnail_"+fileName)
            i.save(filename=path_thumbnail)
            upload_to_s3(path_thumbnail,config.s3_bucketname,'%s/%s' % (username, "thumbnail_"+fileName))
            os.remove(path_thumbnail)
            path_thumbnail = os.path.join(config.S3_ADDRESS,'%s/%s' % (username, "thumbnail_"+fileName))

        with img.clone() as i:
            i.modulate(brightness=100, saturation=300, hue=100)
            path_a = os.path.join(filePath, "a_" + fileName)
            i.save(filename=path_a)
            upload_to_s3(path_a,config.s3_bucketname,'%s/%s' % (username, "a_"+fileName))
            os.remove(path_a)
            path_a = os.path.join(config.S3_ADDRESS,'%s/%s' % (username, "a_"+fileName))

        with img.clone() as i:
            i.modulate(brightness=100, saturation=100, hue=50)
            path_b = os.path.join(filePath, "b_" + fileName)
            i.save(filename=path_b)
            upload_to_s3(path_b,config.s3_bucketname,'%s/%s' % (username, "b_"+fileName))
            os.remove(path_b)
            path_b = os.path.join(config.S3_ADDRESS,'%s/%s' % (username, "b_"+fileName))

        with img.clone() as i:
            i.modulate(brightness=80, saturation=0, hue=100)
            path_c = os.path.join(filePath, "c_" + fileName)
            i.save(filename=path_c)
            upload_to_s3(path_c,config.s3_bucketname,'%s/%s' % (username, "c_"+fileName))
            os.remove(path_c)
            path_c = os.path.join(config.S3_ADDRESS,'%s/%s' % (username, "c_"+fileName))
        os.rmdir(filePath)
    return path_origin,path_thumbnail,path_a,path_b,path_c

def upload_to_s3(filepath, bucketname, filename,acl="public-read"):
    s3 = boto3.client('s3',**config.aws_connection_args)
    s3.upload_file(filepath, bucketname, filename, ExtraArgs={'ACL':acl})
