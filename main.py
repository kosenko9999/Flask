import csv
import io
from flask import Flask, render_template, url_for, request, redirect, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
import json
import pandas as pd
from pandas import Series, DataFrame
import pandas.io.sql as sql
import sqlite3

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)

ALLOWED_EXTENSIONS = {'json', 'csv'}

UPLOAD_FOLDER = 'D:/Flask_Lesson/static/file/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


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
    id_log = db.Column(db.Integer, primary_key=True)
    id_book = db.Column(db.Integer, nullable=False)
    date_action = db.Column(db.DateTime, default=datetime.utcnow)
    id_user = db.Column(db.String(100), nullable=False)
    Title = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(100))


def get_table_log(id_user, action, start_date, end_date):
    table_given_books = Log.query.filter_by(id_user=id_user).filter_by(action=action).filter(
    Log.date_action > start_date).filter(Log.date_action < end_date).order_by(
    Log.date_action.desc()).all()
    return table_given_books


@app.route("/")
def main_page():
    return render_template("index.html")


@app.route("/reports", methods=["GET", "POST"])
def report_page():
    return render_template("report.html")


@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    return render_template("add_user.html")


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    return render_template("add_book.html")


@app.route("/give_book", methods=["POST", "GET"])
def give_books():
    return render_template("give_book.html")


@app.route("/accept_book", methods=["POST", "GET"])
def accept_books():
    return render_template("accept_book.html")


@app.route("/log_given_book", methods=["POST", "GET"])
def log_given_book():
    return render_template("log_given_book.html")


@app.route("/log_returned_book", methods=["POST", "GET"])
def log_returned_book():
    return render_template("log_returned_book.html")


@app.route("/upload", methods=["POST"])
def upload():
    available_user = Users.query.all()
    upload_format = request.form.get("format_uploaded_file")
    print("Формат " + upload_format)
    if request.files["uploaded_file"]:
        file = request.files["uploaded_file"]
        stream = io.StringIO(file.read().decode("UTF8"), newline=None)

        if upload_format == "JSON":
            data = json.load(stream)
            for i in data:
                record = Log(id_book=i['id_book'], id_user=i['id_user'], Title=i['Title'], action=i['action'])
                try:
                    db.session.add(record)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    return "При добавление пользователя произошла ошибка"
        else:
            #csv_input = csv.reader(stream)
            csv_input=csv.DictReader(stream)
            counter = 0
            for row in csv_input:
                record = Log(action=row['action'], date_action=datetime.fromisoformat(row['date_action']),
                             id_user=row['id_user'], Title=row['Title'], id_book=row['id_book'])
                try:
                    db.session.add(record)
                    db.session.commit()
                except Exception as e:
                    print(e)
                    return "При добавление пользователя произошла ошибка"
        return redirect("/log_given_book")


@app.route('/api/books/<int:id_book>', methods=['GET'])
def get_book(id_book):
    books = Books.query.filter_by(id_book=id_book)
    serialized = []
    for each in books:
        serialized.append({
            "id_book": each.id_book,
            "Author": each.Author,
            "Title": each.Title,
        })
    return jsonify(serialized)


@app.route('/api/books', methods=['POST'])
def add_new_book():
    new_request = request.json
    author = new_request["Author"]
    title = new_request["Title"]
    existing_book = Books.query.filter_by(Author=author).filter_by(Title=title).first()
    if existing_book is None:
        book = Books(Author=author, Title=title)
        try:
            db.session.add(book)
            db.session.commit()
        except Exception as e:
            print(e)
        books = Books.query.filter_by(Author=author).filter_by(Title=title)
        serialized = []
        for each in books:
            serialized.append({
                # "id_book": each.id_book,
                "Author": each.Author,
                "Title": each.Title,
            })
        return jsonify(serialized), 200
    else:
        return f"books {title} already exist", 400


@app.route('/api/users/<int:id_user>', methods=['GET'])
def get_user(id_book):
    books = Books.query.filter_by(id_book=id_book)
    serialized = []
    for each in books:
        serialized.append({
            "id_book": each.id_book,
            "Author": each.Author,
            "Title": each.Title,
        })
    return jsonify(serialized)


@app.route('/api/users', methods=['POST'])
def add_new_user():
    new_request = request.json
    name = new_request["Name"]
    surname = new_request["Surname"]
    email = new_request["Email"]
    print(name)
    print(surname)
    existing_users = Users.query.filter_by(Name=name).filter_by(Surname=surname).filter_by(Email=email).first()
    print(existing_users)
    if existing_users is None:
        user = Users(Name=name, Surname=surname, Email=email)
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            print(e)
            return "При добавление пользователя произошла ошибка"
        users = Users.query.filter_by(Name=name).filter_by(Surname=surname).filter_by(Email=email)
        print(users)
        serialized = []
        for each in users:
            serialized.append({
                # "id_user": each.id_user,
                "Name": each.Name,
                "Surname": each.Surname,
                "Email": each.Email
            })
        return jsonify(serialized), 200
    else:
        return f"user {name} {surname} already exist", 400



# Клиенту была выдана книга
@app.route('/api/log/book/given/<int:id_user>', methods=['POST'])
def give_book_user(id_user):
    book = request.args.get("book_title")
    user = id_user
    id_book = Books.query.filter_by(Title=book).first()
    record = Log(id_book=id_book.id_book, id_user=user, Title=book, action="Given")
    try:
        db.session.add(record)
        db.session.commit()
    except Exception as e:
        print(e)
    return "При выдачи книги произошла ошибка"
    given_book = Log.query.filter_by(action="Given")
    serialized = []
    for each in given_books:
        serialized.append({
            "id_book": each.id_book,
            "date_action": each.date_action,
            "id_user": each.id_user,
            "action": each.action,
            "Title": each.Title,
            "id_log": each.id_log
        })
    return jsonify(serialized)


# Клиент отдал книгу
@app.route('/api/log/book/returned/<int:id_user>', methods=['POST'])
def accept_book_user(id_user):
    book = request.args.get("book_title")
    user = id_user
    id_book = Books.query.filter_by(Title=book).first()
    record = Log(id_book=id_book.id_book, id_user=user, Title=book, action="Returned")
    try:
        db.session.add(record)
        db.session.commit()
    except Exception as e:
        print(e)
    return "При выдачи книги произошла ошибка"
    given_book = Log.query.filter_by(action="Returned")
    serialized = []
    for each in given_books:
        serialized.append({
            "id_book": each.id_book,
            "date_action": each.date_action,
            "id_user": each.id_user,
            "action": each.action,
            "Title": each.Title,
            "id_log": each.id_log
        })
    return jsonify(serialized)


#  Запросы для формирование журналов 
@app.route('/api/log/books/given/<int:id_user>', methods=['GET'])
def get_log_given_books(id_user):
    given_books = get_table_log(id_user, "Given", request.args.get("start_date"), request.args.get("end_date"))
    serialized = []
    for each in given_books:
        serialized.append({
            "id_book": each.id_book,
            "date_action": each.date_action,
            "id_user": each.id_user,
            "action": each.action,
            "Title": each.Title,
            "id_log": each.id_log
        })
    return jsonify(serialized)


@app.route('/api/log/books/returned/<int:id_user>', methods=['GET'])
def get_log_returned_books(id_user):
    returned_books = get_table_log(id_user, "Returned", request.args.get("start_date"), request.args.get("end_date"))
    serialized = []
    for each in returned_books:
        serialized.append({
            "id_book": each.id_book,
            "date_action": each.date_action,
            "id_user": each.id_user,
            "action": each.action,
            "Title": each.Title,
            "id_log": each.id_log
        })
    return jsonify(serialized)


# Получение списка доступных книг
@app.route('/api/log/available_book', methods=['GET'])
def get_available_books():
    all_books = Books.query.all()
    available_books = []
    for each in all_books:
        test = Log.query.filter_by(id_book=each.id_book).order_by(Log.date_action.desc()).first()
        if test is None:
            available_books.append(each)
        elif test.action == "Returned":
            available_books.append(each)
    print(available_books)
    serialized = []
    for each in available_books:
        serialized.append({
            "id_book": each.id_book,
            "Author": each.Author,
            "Title": each.Title
        })
    return jsonify(serialized)


@app.route('/api/log/returned/available_book', methods=['GET'])
def get_available_for_returning_book():
    all_books = Books.query.all()
    serialized = []
    for each in all_books:
        serialized.append({
            "id_book": each.id_book,
            "Author": each.Author,
            "Title": each.Title
        })
    return jsonify(serialized)


# Получение списка всех пользователей
@app.route('/api/log/users/all', methods=['GET'])
def get_all_users():
    all_users = Users.query.all()
    serialized = []
    for each in all_users:
        serialized.append({
            "id_user": each.id_user,
            "Name": each.Name,
            "Surname": each.Surname,
            "Email": each.Email
        })
    return jsonify(serialized)


# Получение айди book по Title
@app.route('/api/books/id', methods=['GET'])
def get_id_book():
    title = request.args.get("book_title")
    book = Books.query.filter_by(Title=title).first()
    if book is None:
        return "Book not found", 400
    else:
        serialized = {"id_book": book.id_book}
    return jsonify(serialized), 200


# Запрос для формирование отчета
@app.route('/api/reports', methods=['GET'])
def report_returned_books_by_users():
    filter_column = request.args.get("filter_column")
    isascending = request.args.get("isascending")
    conn = sqlite3.connect("test.db")
    dframe = sql.read_sql("SELECT Name,Surname,date_action,a.id_user as id_user,action,Title,"
                          "id_log FROM Log a join Users b on a.id_user = b.id_user  where date_action > '" + request.args.get("start_date")
                          + "' and date_action < '" + request.args.get("end_date") + "'", conn)

    grouped_given = dframe.groupby(["id_user", "Name", "Surname"], as_index=False)["action"].apply(lambda x: x[x == 'Given'].count())
    grouped_given.rename(columns={'action': 'count_given_book'}, inplace=True)
    grouped_returned = dframe.groupby(["id_user", "Name", "Surname"], as_index=False)["action"].apply(lambda x: x[x == 'Returned'].count())
    grouped_returned.rename(columns={'action': 'count_returned_book'}, inplace=True)
    grouped_returned["count_given_book"] = grouped_given["count_given_book"]
    sorted_dataframe = grouped_returned.sort_values(by=filter_column, ascending=eval(isascending))
    result = sorted_dataframe.to_json(orient="records")
    return jsonify(json.loads(result))


app.run(debug=True)
