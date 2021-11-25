from flask import Flask, render_template, url_for, request, redirect, send_file
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)


class Users(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Surname = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(100), nullable=False)


class Books(db.Model):
    id_book = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(100), nullable=False)
    Author = db.Column(db.String(100), nullable=False)


class Log(db.Model):
    id_book = db.Column(db.Integer, primary_key=True)
    date_action = db.Column(db.DateTime, default=datetime.utcnow)
    id_user = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(100))


@app.route("/")
def main_page():
    return render_template("index.html")


@app.route("/add_user", methods=["POST", "GET"])
def add_user():
    if request.method == "POST":
        name = request.form["name"]
        surname = request.form["surname"]
        email = request.form["email"]
        user = Users(Name=name, Surname=surname, Email=email)
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            print(e)
            return "При добавление пользователя произошла ошибка"
        return redirect("/")
    else:
        return render_template("add_user.html")


@app.route("/add_book", methods=["POST", "GET"])
def add_book():
    if request.method == "POST":
        author = request.form["author"]
        title = request.form["title"]
        book = Books(Author=author, Title=title)
        try:
            db.session.add(book)
            db.session.commit()
        except Exception as e:
            print(e)
            return "При добавление книги произошла ошибка"
        return redirect("/")
    else:
        return render_template("add_book.html")


@app.route("/give_book", methods=["POST", "GET"])
def give_books():
    all_books = Books.query.all()
    available_user = Users.query.all()
    available_books = []

    for each in all_books:
        test = Log.query.filter_by(id_book=each.Title).order_by(Log.date_action.desc()).first()
        if test is None:
            available_books.append(each)
        elif test.action == "Returned":
            available_books.append(each)
    print(available_books)

    if request.method == "POST":
        book = request.form["books"]
        user = request.form["users"]
        record = Log(id_book=book, id_user=user, action="Given")
        try:
            db.session.add(record)
            db.session.commit()
        except Exception as e:
            print(e)
            return "При выдачи книги произошла ошибка"
        return redirect("/")
    else:
        return render_template("give_book.html", available_books=available_books,  available_user=available_user)


@app.route("/download")
def download_file():
    test = {'test_key': 'value_test'}
    with open('test_file.json', 'w') as file:
        json.dump(test, file, indent=4)

    return send_file('test_file.json', as_attachment=True)


@app.route("/accept_book", methods=["POST", "GET"])
def accept_books():
    available_books = Books.query.all()
    available_user = Users.query.all()
    if request.method == "POST":
        book = request.form["books"]
        user = request.form["users"]
        record = Log(id_book=book, id_user=user, action="Returned")
        try:
            db.session.add(record)
            db.session.commit()
        except Exception as e:
            print(e)
            return "При возрате книги произошла ошибка"

        return redirect("/")
    else:
        return render_template("accept_book.html", available_books=available_books, available_user=available_user)


@app.route("/log_given_book", methods=["POST", "GET"])
def log_given_book():
    available_user = Users.query.all()
    if request.method == "POST":
        user = request.form.get("users")
        end_date = request.form["end"]
        start_date = request.form["start"]
        table_given_books = Log.query.filter_by(id_user=user).filter_by(action="Given").filter(Log.date_action > start_date).filter(Log.date_action < end_date).order_by(
            Log.date_action.desc()).all()
        try:
            return render_template("log_given_book.html", table_given_books=table_given_books, available_user=available_user)
        except Exception as e:
            return "При формировании журнала была ошибка"
    else:
        return render_template("log_given_book.html",  available_user=available_user)


@app.route("/log_returned_book", methods=["POST", "GET"])
def log_returned_book():
    available_user = Users.query.all()
    if request.method == "POST":
        user = request.form.get("users")
        end_date = request.form["end"]
        start_date = request.form["start"]
        table_given_books = Log.query.filter_by(id_user=user).filter_by(action="Returned").filter(Log.date_action > start_date).filter(Log.date_action < end_date).order_by(
            Log.date_action.desc()).all()
        try:
            return render_template("log_returned_book.html", table_given_books=table_given_books, available_user=available_user)
        except Exception as e:
            return "При формировании журнала была ошибка"
    else:
        return render_template("log_returned_book.html",  available_user=available_user)


app.run(debug=True)
