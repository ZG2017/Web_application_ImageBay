from flask import render_template, url_for, request, redirect, session, flash, send_file
from app import webapp
import os
from app import sql

# to show original image and 3 trans images
@webapp.route("/homepage/detail/<path:imgId>",methods = ["GET","POST"])
def imgDetail(imgId):
    if session["authenticated"]:
        path ="/".join(webapp.config["UPLOAD_FOLDER"].split("/")[:-1])
        images = []
        cnx = sql.get_db()
        cursor = cnx.cursor()
        query = "SELECT * FROM user2Images WHERE userName = %s AND Thumbnail = %s"
        cursor.execute(query,(session["username"],os.path.join(path,imgId)))
        row = cursor.fetchone()
        if row == None:
            flash("Can't find images, please reupload!")
            return redirect(url_for("HomePage"))
        for i in [2,3,4,5]:
            images.append(os.path.join(os.path.join("upload_images",session["username"]),row[i].split("/")[-1]))
        return render_template("imgdetail.html",title = session["username"],images = images)
    else:
        session["error"] = "unauthenticated log In"
        return redirect(url_for("SignIn"))
