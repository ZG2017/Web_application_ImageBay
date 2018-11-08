from wand.image import Image
import os
from app import sql
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

# check if file is a image file
def allowed_file(filename):
    return filename.split(".")[-1] in ALLOWED_EXTENSIONS

# save images to local file system
def ImageTransSave(filePath,fileName):
    with Image(filename = os.path.join(filePath,fileName)) as img:
        with img.clone() as i:
            i.resize(width = 150,height = 100)
            path_thumbnail = os.path.join(filePath,"thumbnail_"+fileName)
            i.save(filename=path_thumbnail)
        with img.clone() as i:
            i.modulate(brightness = 100, saturation = 170, hue = 100)
            path_a = os.path.join(filePath,"a_"+fileName)
            i.save(filename=path_a)
        with img.clone() as i:
            i.modulate(brightness = 100, saturation = 100, hue = 50)
            path_b = os.path.join(filePath,"b_"+fileName)
            i.save(filename=path_b)
        with img.clone() as i:
            i.modulate(brightness = 80, saturation = 0, hue = 100)
            path_c = os.path.join(filePath,"c_"+fileName)
            i.save(filename=path_c)
    return path_thumbnail,path_a,path_b,path_c