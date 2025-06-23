from flask import Flask, render_template, redirect, url_for, request, session, Blueprint
from model import db,User,Admin,Subject,Chapter,Quiz,Questions,Scores

from datetime import datetime

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/") 
def home():   

    warning = request.args.get("warning")

    if warning is None:
        return render_template("login_page.html",warning = "") 
    else:
        return render_template("login_page.html",warning = warning) 
    
@auth_bp.route("/register",methods = ['GET','POST'])
def register():

    if request.method == "POST":

        users = User.query.all()    
        for user in users:
            if(user.username == request.form["username"]):

                return render_template("register.html",warning = "Username is already taken")


        dob = datetime.strptime(request.form["dob"], "%Y-%m-%d").date()
        
        db.session.add(User(username = request.form["username"], 
                            password = request.form["password"], 
                            fullname = request.form["fullname"], 
                            qualification = request.form["qualification"].lower(),
                            dob = dob))
        db.session.commit()

        return redirect(url_for("auth.home")) 
    
    return render_template("register.html",warning = "")

@auth_bp.route("/exit")
def exit():
    session.clear()

    return redirect(url_for("auth.home"))