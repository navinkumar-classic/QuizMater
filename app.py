from flask import Flask, render_template, redirect, url_for, request, session
from model import db,User,Admin,Subject,Chapter,Quiz,Questions,Scores
from controller.auth_controller import auth_bp
from controller.user_controller import user_bp
from controller.admin_controller import admin_bp

from datetime import datetime
  
app = Flask(__name__, instance_relative_config=True)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SECRET_KEY"] = "hsgdjsgdjasdbbanv"

db.init_app(app)

with app.app_context():
    db.create_all()

    admins = Admin.query.all()
    flag = True
    for admin in admins:
        if admin.username == "admin":
            flag = False
    if flag:
        db.session.add(Admin(username = "admin", 
                            password = "admin123", 
                            fullname = "Navin Kumar"))
        db.session.commit()

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__": 
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=False)