from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    fullname = db.Column(db.String, nullable=False)
    qualification = db.Column(db.String, nullable=True)
    dob = db.Column(db.Date, nullable=False)

class Admin(db.Model):
    __tablename__ = "admin"
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    fullname = db.Column(db.String, nullable=False)

class Subject(db.Model):
    __tablename__ = "subject"
    subject_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False)
    
    chapters = db.relationship("Chapter", backref="subject", cascade="all, delete-orphan")

class Chapter(db.Model):
    __tablename__ = "chapter"
    chapter_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.subject_id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    
    quizzes = db.relationship("Quiz", backref="chapter", cascade="all, delete-orphan")

class Quiz(db.Model):
    __tablename__ = "quiz"
    quiz_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.chapter_id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    time_in_mins = db.Column(db.Integer, nullable=False)
    #remarks = db.Column(db.String, nullable=False)
    
    questions = db.relationship("Questions", backref="quiz", cascade="all, delete-orphan")
    scores = db.relationship("Scores", backref="quiz", cascade="all, delete-orphan")

class Questions(db.Model):
    __tablename__ = "questions"
    question_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.quiz_id", ondelete="CASCADE"), nullable=False)
    question = db.Column(db.String, nullable=False)
    option_a = db.Column(db.String, nullable=False)
    option_b = db.Column(db.String, nullable=False)
    option_c = db.Column(db.String, nullable=False)
    option_d = db.Column(db.String, nullable=False)
    answer = db.Column(db.String, nullable=False)

class Scores(db.Model):
    __tablename__ = "scores"
    score_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.quiz_id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    question_ids = db.Column(db.String, nullable=False)
    answers = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.String, nullable=False, default = db.func.current_timestamp())