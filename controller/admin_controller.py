from flask import Flask, render_template, redirect, url_for, request, session, Blueprint, jsonify
from model import db, User, Admin, Subject, Chapter, Quiz, Questions, Scores
import statistics
from datetime import datetime
from sqlalchemy import func

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin-login",methods = ['POST'])
def admin_login():  

    if request.method == "POST":
    
        admins = Admin.query.all()    
        for admin in admins:
            if request.form["username"] == admin.username and request.form["password"] == admin.password:
                session["logged_in"] = True
                session["username"] = admin.username
                session["admin"] = True

                return redirect(url_for("admin.admin"))  

        return redirect(url_for("auth.home",warning = "Username or Password is incorrect")) 

@admin_bp.route("/admin",methods = ['GET'])
def admin():

    if session.get("logged_in") and session.get("admin"):

        popup = request.args.get("popup")
        warningMessage = request.args.get("warning")
        subjectId = request.args.get("subject_id")
        chapterId = request.args.get("chapter_id")
        search = request.args.get("search")
        
        if popup == "addsubject":

            if warningMessage is None:
                return render_template("add_subject.html",warning = "") 
            else:
                return render_template("add_subject.html",warning = warningMessage) 
            
        if popup == "addchapter":

            if warningMessage is None:
                return render_template("add_chapter.html",warning = "",subject_id=subjectId) 
            else:
                return render_template("add_chapter.html",warning = warningMessage,subject_id=subjectId) 
        
        if popup == "editchapter":

            if warningMessage is None:
                return render_template("edit_chapter.html",warning = "",chapter_id=chapterId,chapters=Chapter.query.all()) 
            else:
                return render_template("edit_chatper.html",warning = warningMessage,chapter_id=chapterId,chapters=Chapter.query.all()) 
            
        if popup == "editsubject":

            if warningMessage is None:
                return render_template("edit_subject.html",warning = "",subject_id=subjectId,subjects=Subject.query.all()) 
            else:
                return render_template("edit_subject.html",warning = warningMessage,subject_id=subjectId,subjects=Subject.query.all())

        if popup == "search":

            subject_search = Subject.query.filter(Subject.name.ilike(f"%{search}%")).all() 
            chapter_search = Chapter.query.filter(Chapter.name.ilike(f"%{search}%")).all() 

            chapter_ids = [chapter.subject_id for chapter in chapter_search]

            if chapter_ids:  
                subject_chapter_search = Subject.query.filter(Subject.subject_id.in_(chapter_ids)).all()
            else:
                subject_chapter_search = []

            final_query = list(set(subject_search) | set(subject_chapter_search))

            return render_template("admin.html",subjects = final_query ,chapters=Chapter.query.all(),type="subject") 
        
        else:

            return render_template("admin.html",subjects=Subject.query.all(),chapters=Chapter.query.all(),type="subject")
    
    return redirect(url_for("auth.home"))

@admin_bp.route("/admin/summary")
def admin_summary():  
    if session.get("logged_in") and session.get("admin"): 
        chapters_dict = {chapter.chapter_id: chapter.name for chapter in Chapter.query.all()}

        return render_template("admin_summary.html", quizzes = Quiz.query.all(), chapterDic = chapters_dict)
    
    return redirect(url_for("auth.home"))

#
#
#
#

@admin_bp.route("/switchaddsub",methods = ['POST'])
def switchaddsub():
            
    return redirect(url_for("admin.admin",popup="addsubject"))

@admin_bp.route("/switcheditsub",methods = ['POST'])
def switcheditsub():
            
    return redirect(url_for("admin.admin",popup="editsubject",subject_id=request.form["subject_id"]))

@admin_bp.route("/switchbackadmin",methods = ['POST'])
def switchbackadmin():
            
    return redirect(url_for("admin.admin",popup=""))

@admin_bp.route("/add-subject",methods = ['POST'])
def add_subject():

    if request.method == "POST":
        print(request.form["subject"])
        print(request.form["description"])

        subjects = Subject.query.all()
        for subject in subjects:
            if(subject.name == request.form["subject"]):
                return redirect(url_for("admin.admin",popup="addsubject",warning="Subject Already Exists"))
        
        db.session.add(Subject(name = request.form["subject"], 
                            description = request.form["description"]))
        db.session.commit()

        return redirect(url_for("admin.admin",popup=""))
            
    return redirect(url_for("admin.admin"))

@admin_bp.route("/delsubject",methods = ['POST'])
def del_subject():

    if request.method == "POST":

        subject_id = request.form["subject_id"]

        subject = Subject.query.filter_by(subject_id=subject_id).first()
        if subject:
            db.session.delete(subject)
            db.session.commit()

        return redirect(url_for("admin.admin"))
    
@admin_bp.route("/editsubject",methods = ['POST'])
def edit_subject():

    if request.method == "POST":

        subject_id = request.form["subject_id"]

        subject = Subject.query.filter_by(subject_id=subject_id).first()
        if subject:
            subject.name = request.form["subject"]
            subject.description = request.form["description"]
            
            db.session.commit()

        return redirect(url_for("admin.admin"))

#
#
#
#

@admin_bp.route("/switchaddchap",methods = ['POST'])
def switchaddchap():
            
    return redirect(url_for("admin.admin",popup="addchapter",subject_id=request.form["subject_id"]))

@admin_bp.route("/switcheditchap",methods = ['POST'])
def switcheditchap():
            
    return redirect(url_for("admin.admin",popup="editchapter",chapter_id=request.form["chapter_id"]))

@admin_bp.route("/add-chapter",methods = ['POST'])
def add_chapter():

    if request.method == "POST":
        
        db.session.add(Chapter(subject_id = request.form["subject_id"],
                               name = request.form["subject"], 
                               description = request.form["description"]))
        db.session.commit()

        return redirect(url_for("admin.admin",popup=""))
            
    return redirect(url_for("admin.admin"))

@admin_bp.route("/delchapter",methods = ['POST'])
def del_chapter():

    if request.method == "POST":

        chapter_id = request.form["chapter_id"]

        chapter = Chapter.query.filter_by(chapter_id=chapter_id).first()
        if chapter:
            db.session.delete(chapter)
            db.session.commit()

        return redirect(url_for("admin.admin"))
    
@admin_bp.route("/editchapter",methods = ['POST'])
def edit_chapter():

    if request.method == "POST":

        chapter_id = request.form["chapter_id"]

        chapter = Chapter.query.filter_by(chapter_id=chapter_id).first()
        if chapter:
            chapter.name = request.form["subject"]
            chapter.description = request.form["description"]
            
            db.session.commit()

        return redirect(url_for("admin.admin"))
    
#
# 
# 
# 
    
@admin_bp.route("/admin/quiz")
def admin_quiz():  
    if session.get("logged_in") and session.get("admin"): 
        popup = request.args.get("popup")
        search = request.args.get("search")
        warningMessage = request.args.get("warning")
        subjectId = request.args.get("subject_id")
        chapterId = request.args.get("chapter_id")
        quizId = request.args.get("quiz_id")
        questionId = request.args.get("question_id")
        chapters_dict = {chapter.chapter_id: chapter.name for chapter in Chapter.query.all()}

        if popup == "addquiz":

            if warningMessage is None:
                return render_template("add_quiz.html",warning = "", chapters= Chapter.query.all()) 
            else:
                return render_template("add_quiz.html",warning = warningMessage, chapters= Chapter.query.all()) 
            
        elif popup == "addques":

            if warningMessage is None:
                return render_template("add_question.html",warning = "", chapters= Chapter.query.all(), quiz_id = quizId) 
            else:
                return render_template("add_question.html",warning = warningMessage, chapters= Chapter.query.all(), quiz_id = quizId) 
            
        elif popup == "editquiz":

            if warningMessage is None:
                return render_template("edit_quiz.html",warning = "", quizzes = Quiz.query.all(), quiz_id = quizId, chapters= Chapter.query.all()) 
            else:
                return render_template("edit_quiz.html",warning = warningMessage, quizzes = Quiz.query.all(), quiz_id = quizId, chapters= Chapter.query.all()) 
            
        elif popup == "editques":

            if warningMessage is None:
                return render_template("edit_question.html",warning = "", questions = Questions.query.all(), question_id = questionId, chapters= Chapter.query.all()) 
            else:
                return render_template("edit_question.html",warning = warningMessage, questions = Questions.query.all(), question_id = questionId, chapters= Chapter.query.all())
            
        elif popup == "search":

            quiz_search = Quiz.query.filter(Quiz.name.ilike(f"%{search}%")).all()
            chapter_ids_query = Quiz.query.join(Chapter).filter(Chapter.name.ilike(f"%{search}%"))
            subject_ids_query = Quiz.query.join(Chapter).join(Subject).filter(Subject.name.ilike(f"%{search}%"))

            final_query = list(set(quiz_search) | set(chapter_ids_query) | set(subject_ids_query))


            return render_template("admin_quiz.html", quizzes = final_query, chapterDic = chapters_dict, questions = Questions.query.all(), type="quiz")

        else:

            return render_template("admin_quiz.html", quizzes = Quiz.query.all(), chapterDic = chapters_dict, questions = Questions.query.all(), type="quiz")
    
    return redirect(url_for("auth.home"))

@admin_bp.route("/switchaddquiz",methods = ['POST'])
def switchaddquiz():
            
    return redirect(url_for("admin.admin_quiz",popup="addquiz"))

@admin_bp.route("/switcheditquiz",methods = ['POST'])
def switcheditquiz():
            
    return redirect(url_for("admin.admin_quiz",popup="editquiz",quiz_id=request.form["quiz_id"]))

@admin_bp.route("/switchbackquiz",methods = ['POST'])
def switchbackquiz():
            
    return redirect(url_for("admin.admin_quiz",popup=""))

@admin_bp.route("/add-quiz",methods = ['POST'])
def add_quiz():

    if request.method == "POST":

        quiz_datetime = datetime.strptime(request.form["time"], "%Y-%m-%dT%H:%M")
        
        db.session.add(Quiz(chapter_id = request.form["chapterid"],
                               name = request.form["quizname"], 
                               date = quiz_datetime,
                               time_in_mins = request.form["mins"]))
        db.session.commit()

        return redirect(url_for("admin.admin_quiz",popup=""))
            
    return redirect(url_for("admin.admin_quiz"))

@admin_bp.route("/delquiz",methods = ['POST'])
def del_quiz():

    if request.method == "POST":

        quiz_id = request.form["quiz_id"]

        quiz = Quiz.query.filter_by(quiz_id=quiz_id).first()
        if quiz:
            db.session.delete(quiz)
            db.session.commit()

        return redirect(url_for("admin.admin_quiz"))
    
@admin_bp.route("/edit-quiz",methods = ['POST'])
def edit_quiz():

    if request.method == "POST":

        quiz_id = request.form["quiz_id"]

        quiz = Quiz.query.filter_by(quiz_id=quiz_id).first()

        if quiz:
            quiz_datetime = datetime.strptime(request.form["time"], "%Y-%m-%dT%H:%M")

            quiz.chapter_id = request.form["chapterid"]
            quiz.name = request.form["quizname"]
            quiz.date = quiz_datetime
            quiz.time_in_mins = request.form["mins"]
            
            db.session.commit()

        return redirect(url_for("admin.admin_quiz"))
    
# 
#
#
#

@admin_bp.route("/switchaddques",methods = ['POST'])
def switchaddques():
            
    return redirect(url_for("admin.admin_quiz",popup="addques",quiz_id=request.form["quiz_id"]))

@admin_bp.route("/switcheditques",methods = ['POST'])
def switcheditques():
            
    return redirect(url_for("admin.admin_quiz",popup="editques",question_id=request.form["question_id"]))

@admin_bp.route("/add-question",methods = ['POST'])
def add_question():

    if request.method == "POST":
        
        db.session.add(Questions(quiz_id = request.form["quiz_id"],
                               question = request.form["question"], 
                               option_a = request.form["option-a"],
                               option_b = request.form["option-b"],
                               option_c = request.form["option-c"],
                               option_d = request.form["option-d"],
                               answer = request.form["answer"]))
        db.session.commit()

        return redirect(url_for("admin.admin_quiz",popup=""))
            
    return redirect(url_for("admin.admin_quiz"))

@admin_bp.route("/delques",methods = ['POST'])
def del_ques():

    if request.method == "POST":

        question_id = request.form["question_id"]

        question = Questions.query.filter_by(question_id=question_id).first()
        if question:
            db.session.delete(question)
            db.session.commit()

        return redirect(url_for("admin.admin_quiz"))
    
@admin_bp.route("/edit-ques",methods = ['POST'])
def edit_ques():

    if request.method == "POST":

        question_id = request.form["question_id"]

        question = Questions.query.filter_by(question_id=question_id).first()

        if question:
            question.question = request.form["question"]
            question.option_a = request.form["option-a"]
            question.option_b = request.form["option-b"]
            question.option_c = request.form["option-c"]
            question.option_d = request.form["option-d"]
            question.answer = request.form["answer"]
            
            
            db.session.commit()

        return redirect(url_for("admin.admin_quiz"))
    
#
#
#
#

@admin_bp.route("/search",methods = ['POST'])
def search():
    
    if request.method == 'POST':

        if request.form['type'] == 'subject':

            return redirect(url_for("admin.admin", search = request.form['search'], popup = "search"))
        
        elif request.form['type'] == 'quiz':

            return redirect(url_for("admin.admin_quiz", search = request.form['search'], popup = "search"))

#
#
#
#

@admin_bp.route("/quizdata")
def quiz_data():

    quizId = request.args.get("quiz_id")

    scores = Scores.query.filter_by(quiz_id = quizId).all()

    total_attempts = len(scores)
    if total_attempts == 0:

        json = {
            "total_attempts":0,
            "average":0,
            "stdev":0
        }

    else:
        percenList = [score.score*100/len(score.answers.split(",")) for score in scores]

        average = statistics.mean(percenList)
        if(len(scores) < 2):
            stdev = 0
        else:
            stdev = statistics.stdev(percenList)

        json = {
            "total_attempts":total_attempts,
            "average":average,
            "stdev":stdev
        }

    return jsonify(json)

@admin_bp.route("/histogram")
def histogram():

    quizId = request.args.get("quiz_id")
    scores = Scores.query.filter_by(quiz_id = quizId).all()
    bins = [0] * 10  

    if len(scores) == 0:
        pass

    else:

        percenList = [score.score*100/len(score.answers.split(",")) for score in scores]

        for mark in percenList:
                bin_index = min(int(mark) // 10, 9)  
                bins[bin_index] += 1

    json = {
        "labels": ["0-10","10-20","20-30","30-40","40-50","50-60","60-70","70-80","80-90","90-100"],
        "datasets": [{
            "label": "Number of Students",
            "data": bins
        }]
    }
    
    return jsonify(json)
