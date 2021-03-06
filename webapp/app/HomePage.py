from flask import render_template, url_for, request, redirect, session
from werkzeug.utils import secure_filename
from app import webapp
from wand.image import Image
import os
from app import sql
from app import ImageProcess
from app import config

# show personal homepage
@webapp.route("/homepage", methods=['GET', 'POST'])
def HomePage():
    images = []
# check if user info are valid and sub
    if "error" in session:
        error = session["error"]
    else:
        error = None
        session["error"] = None
    if session["authenticated"]:
        cnx = sql.get_db()
        cursor = cnx.cursor()
        query = "SELECT * FROM user2Images WHERE userName = %s"
        cursor.execute(query,(session["username"],))

        row = cursor.fetchall()
        sql.close_db()
        if row == None:
            return render_template("homepage.html",title = session["username"],images = images, error = error)
        lens = len(row)
        print(row)
        for i in range(lens):
            # file_name = row[i][1].split("/")[-1]
            images.append(row[i][1])
        print(images)
        return render_template("homepage.html",title = session["username"],images = images, error = error)
    else:
        session["error"] = "unauthenticated log In"
        return redirect(url_for("SignIn"))
    
# upload a new image
@webapp.route("/homepage/upload", methods=['GET', 'POST'])
def UpLoad():
    if 'my_file' not in request.files:
        session["error"] = "didn't receive any file please try again!"
        return redirect(url_for('HomePage'))
    myFile = request.files["my_file"]
    cnx = sql.get_db()
    cursor = cnx.cursor()
    query = "SELECT * FROM user2Images WHERE userName = %s AND original = %s"
    myFile_link = config.S3_ADDRESS + session['username'] + '/' + myFile.filename
    cursor.execute(query,(session["username"], myFile_link))
    row = cursor.fetchone()
    sql.close_db()
    if row != None:
        session["error"] = "Image with same name has already been uploaded!"
        return redirect(url_for("HomePage"))
    if myFile.filename == '':
        session["error"] = "No file selected"
        return redirect(url_for('HomePage'))
    if myFile and ImageProcess.allowed_file(myFile.filename):
        userPath = os.path.join(webapp.config['UPLOAD_FOLDER'],session["username"])
        if not os.path.exists(userPath):
            os.makedirs(userPath)
        filename = secure_filename(myFile.filename)
        path_original = os.path.join(userPath,filename)
        myFile.save(path_original)
        path_origin, path_thumbnail,path_a,path_b,path_c = ImageProcess.ImageTransSave(session['username'],userPath, filename)
        ImageProcess.DBImageSave(session["username"],path_thumbnail,path_origin,path_a,path_b,path_c)
        session["error"] = None
        return redirect(url_for('HomePage')) 
    else:
        session["error"] = "can not recognize the file, please reupload"
        return redirect(url_for("HomePage"))
