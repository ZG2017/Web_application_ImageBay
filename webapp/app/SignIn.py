from flask import render_template, session, url_for, request, redirect
from app import webapp
from app import sql
import hashlib
import base64
import os

# add salt and hash the password
def Pwd2Hash(password,salt=None):
    password = password.encode()
    if not salt:
        salt = base64.b64encode(os.urandom(32))
    else:
        salt = salt.encode()
    hashInput = hashlib.sha256(salt+password).hexdigest()
    return hashInput,salt

# show signin page
@webapp.route("/signin",methods=['GET','POST'])
def SignIn():
    username = None
    error = None
    #imageURL = url_for("static",filename = "background2.jpg")
    if "username" in session:
        username = session["username"]
    if "resubmit" in session and session["resubmit"]:
        if "error" in session:
            error = session["error"]
            session["error"] = None

    session["resubmit"] = False
    return render_template("signin.html",title = "ImageBay",username=username,error=error)

# check if input info are valid and add login to homepage if it is 
@webapp.route("/signin_submit",methods=['POST'])
def SignInSubmit():
    cnx = sql.get_db()
    cursor = cnx.cursor()
    user_name = request.form["username"]
    query = "SELECT * FROM userInfo WHERE userName = %s"
    cursor.execute(query,(user_name,))
    row = cursor.fetchone()

    if row == None:
        session["resubmit"] = True
        session["error"] = "username don't exsist!"
        return redirect(url_for("SignIn"))

    currentUser = {"username":row[0],"pwd":row[2],"salt":row[3]}

    if "username" in request.form and request.form["username"] == currentUser["username"] \
    and "password" in request.form and Pwd2Hash(request.form["password"],currentUser["salt"])[0] == currentUser["pwd"]:
        session['authenticated'] = True
        session["username"] = request.form["username"]
        session["error"] = None
        return redirect(url_for("HomePage"))
    
    if 'username' in request.form:
        session["username"] = request.form["username"]

    session["resubmit"] = True
    session["error"] = "username or password incorrect!"
    return redirect(url_for("SignIn"))
