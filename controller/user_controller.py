from flask import Flask, render_template, redirect, url_for, request, session, Blueprint, jsonify
from model import db, User, Admin, Subject, Chapter, Quiz, Questions, Scores 
from sqlalchemy import func
import statistics

from datetime import datetime
import pytz

user_bp = Blueprint("user", __name__)

def get_indian_timestamp():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S')

@user_bp.route("/user-login",methods = ['POST'])
def user_login(): 

    if request.method == "POST":
    
        users = User.query.all()    
        for user in users:
            if request.form["username"] == user.username and request.form["password"] == user.password:
                session["logged_in"] = True
                session["username"] = user.username
                session["user_id"] = user.user_id
                session["admin"] = False

                print("Session after login:", session)

                return redirect(url_for("user.user"))  

        return redirect(url_for("auth.home",warning = "Username or Password is incorrect")) 

@user_bp.route("/user",methods = ['GET'])
def user(): 
    
    if session.get("logged_in") and not session.get("admin"):

        popup = request.args.get("popup")
        search = request.args.get("search")
        quizId = request.args.get("quiz_id")
        chapters_dict = {chapter.chapter_id: chapter.name for chapter in Chapter.query.all()}
        subject_dict = {chapter.chapter_id: chapter.subject.name for chapter in Chapter.query.join(Subject).all()}
        result = db.session.query(Quiz.quiz_id, func.count(Questions.question_id)).join(Questions).group_by(Quiz.quiz_id).all()
        number_question ={quiz_id: question_count for quiz_id, question_count in result}

        current_time = get_indian_timestamp()
        started = {}
        current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')

        for quiz in Quiz.query.all():

            if quiz.date > current_time:
                started[quiz.quiz_id] = False
            else:
                started[quiz.quiz_id] = True

        print(started)

        if popup == "viewuser":

            return render_template("view_user.html", quizzes = Quiz.query.all(), numberQuestions = number_question, quiz_id = quizId, chapterD = chapters_dict, subjectD = subject_dict)
        
        if popup == "viewquiz":

            return render_template("quiz_page.html",quiz_id = quizId, quizzes = Quiz.query.all(), numberQuestions = number_question, questions = Questions.query.all())
        
        if popup == "search":

            quiz_search = Quiz.query.filter(Quiz.name.ilike(f"%{search}%")).all()
            chapter_ids_query = Quiz.query.join(Chapter).filter(Chapter.name.ilike(f"%{search}%"))
            subject_ids_query = Quiz.query.join(Chapter).join(Subject).filter(Subject.name.ilike(f"%{search}%"))

            final_query = list(set(quiz_search) | set(chapter_ids_query) | set(subject_ids_query))
            
            return render_template("user.html", quizzes = final_query, numberQuestions = number_question, type="quiz", started = started)  


        return render_template("user.html", quizzes = Quiz.query.all(), numberQuestions = number_question, type="quiz", started = started)  

    return redirect(url_for("auth.home",warning = ""))

@user_bp.route("/switchviewuser",methods = ['POST'])
def switch_view_user():

    return redirect(url_for("user.user", popup = "viewuser", quiz_id = request.form["quiz_id"]))

@user_bp.route("/switchquiz",methods = ['POST'])
def switch_quiz():

    return redirect(url_for("user.user", popup = "viewquiz", quiz_id = request.form["quiz_id"]))

@user_bp.route("/switchbackuser",methods = ['POST'])
def switch_back_user():

    return redirect(url_for("user.user", popup = ""))

@user_bp.route("/calculatescore",methods = ['POST'])
def calculate_score():

    if request.method == 'POST':

        user_id = session["user_id"]

        answer_list = []
        questions_id_list = []
        score = 0
        for question in Questions.query.all():

            if str(question.quiz_id) == str(request.form["quiz_id"]):

                if request.form.get("q" + str(question.question_id)) is not None:
                    questions_id_list.append(str(question.question_id))
                    answer_list.append(str(request.form["q" + str(question.question_id)]))

                    if(str(question.answer) == str(request.form["q" + str(question.question_id)])):
                        score += 1
                
                else:
                    questions_id_list.append(str(question.question_id))
                    answer_list.append("N")

        db.session.add(Scores(quiz_id = request.form["quiz_id"],
                              score = score,
                              user_id = user_id,
                              question_ids = ",".join(questions_id_list),
                              answers = ",".join(answer_list),
                              timestamp = get_indian_timestamp()))
        db.session.commit()

        return redirect(url_for("user.user"))          

#
#
#
#

@user_bp.route("/user/score")
def user_score():  
    if session.get("logged_in") and  not session.get("admin"): 

        popup = request.args.get("popup")
        search = request.args.get("search")
        score_id = request.args.get("score_id")
        number_question ={score.score_id: len(score.answers.split(",")) for score in Scores.query.all()}

        if popup == "viewreport":

            score = Scores.query.filter_by(score_id=score_id).first()

            questions_id = score.question_ids.split(",")
            answers = score.answers.split(",")

            report = []

            for i in range(len(questions_id)):
                temp = {}
                question = Questions.query.filter_by(question_id = questions_id[i]).first()
                temp["question"] = question.question
                temp["correct"] = question.answer
                temp["answer"] = answers[i]
                temp["option_a"] = question.option_a
                temp["option_b"] = question.option_b
                temp["option_c"] = question.option_c
                temp["option_d"] = question.option_d
                report.append(temp)

            return render_template("score_report.html", report = report)
        
        if popup == "search":

            quiz_search = Quiz.query.filter(Quiz.name.ilike(f"%{search}%")).all()
            chapter_ids_query = Quiz.query.join(Chapter).filter(Chapter.name.ilike(f"%{search}%"))
            subject_ids_query = Quiz.query.join(Chapter).join(Subject).filter(Subject.name.ilike(f"%{search}%"))

            final_query = list(set(quiz_search) | set(chapter_ids_query) | set(subject_ids_query))

            quiz_ids = [quiz.quiz_id for quiz in final_query] 

            if quiz_ids:  
                score_search = Scores.query.filter(Scores.quiz_id.in_(quiz_ids)).all()
            else:
                score_search = [] 
            

            
            return render_template("user_score.html", scores=score_search, quizzes=Quiz.query.all(), user_id=session["user_id"], numberAnswers = number_question,type="score")


        return render_template("user_score.html", scores=Scores.query.all(), quizzes=Quiz.query.all(), user_id=session["user_id"], numberAnswers = number_question,type="score")
    
    return redirect(url_for("auth.home"))

@user_bp.route("/switchscorerep",methods = ['POST'])
def switch_score_report():

    return redirect(url_for("user.user_score", popup = "viewreport", score_id = request.form["score_id"]))

#
#
#
#

@user_bp.route("/user/summary")
def user_summary():  
    if session.get("logged_in") and not session.get("admin"): 
        return render_template("user_summary.html")
    
    return redirect(url_for("auth.home"))

#
#
#
#

@user_bp.route("/search-user",methods = ['POST'])
def search_user():
    
    if request.method == 'POST':

        if request.form['type'] == 'quiz':

            return redirect(url_for("user.user", search = request.form['search'], popup = "search"))
        
        elif request.form['type'] == 'score':

            return redirect(url_for("user.user_score", search = request.form['search'], popup = "search"))

#
#
#
#

@user_bp.route('/start_quiz', methods=['POST'])
def start_quiz():
    data = request.get_json()
    
    session["duration"] = int(data["min"]) * 60
    session["start_time"] = datetime.utcnow().isoformat()
    return jsonify({"message": "Quiz started", "start_time": session["start_time"]})

@user_bp.route('/time_remaining', methods=['GET'])
def time_remaining():
    start_time_str = session.get("start_time")
    
    if not start_time_str:
        return jsonify({"error": "Quiz not started"}), 400

    start_time = datetime.fromisoformat(start_time_str)
    elapsed_time = (datetime.utcnow() - start_time).total_seconds()
    remaining_time = max(0, session["duration"] - elapsed_time)
    
    return jsonify({"remaining_time": remaining_time})

#
#
#
#

@user_bp.route('/chart-data')
def chart_data():

    recent_scores = Scores.query.filter_by(user_id=session["user_id"]).order_by(Scores.timestamp.desc()).limit(5).all()

    label = []
    percentage = []

    for score in recent_scores:
        
        a = score.score
        b = len(score.answers.split(","))
        percentage.append(a*100/b)
        lab = Quiz.query.filter_by(quiz_id=score.quiz_id).first().name
        label.append(lab)

    data = {
        "labels": label,
        "datasets": [{
            "label": "Sales",
            "data": percentage
        }]
    }
    return jsonify(data)

@user_bp.route("/userStatistics")
def user_statistics():

    scores = Scores.query.filter_by(user_id = session["user_id"]).all()

    if len(scores) == 0:

        json = {
            "totalAttempts": 0,
            "average": 0,
            "stdev": 0
        }

    else:
        percenList = [score.score*100/len(score.answers.split(",")) for score in scores]
        average = statistics.mean(percenList)
        if(len(scores) < 2):
            stdev = 0
        else:
            stdev = statistics.stdev(percenList)

        json = {
            "totalAttempts": len(percenList),
            "average": average,
            "stdev": stdev
        }
    
    return jsonify(json)