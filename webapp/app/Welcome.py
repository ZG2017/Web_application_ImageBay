from flask import render_template, url_for,send_file
from app import webapp

# weclome page
#@webapp.route("/welcome")
@webapp.route("/",methods=["GET"])
def Welcome():
    #imageURL = url_for("static",filename = "background1.jpg")
    return render_template("welcome.html", title = "ImageBay")