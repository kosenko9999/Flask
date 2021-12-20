import csv
import io
from flask import Flask, render_template, url_for, request, redirect, send_file,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta, date
import json

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
        test = Log.query.filter_by(id_book=each.id_book).order_by(Log.date_action.desc()).first()
        if test is None:
            available_books.append(each)
        elif test.action == "Returned":
            available_books.append(each)
    print(available_books)

    if request.method == "POST":
        book = request.form["books"]
        user = request.form["users"]
        id_book = Books.query.filter_by(Title=book).first()
        print(id_book)
        print(id_book.id_book)
        record = Log(id_book=id_book.id_book, id_user=user, Title=book,  action="Given")
        try:
            db.session.add(record)
            db.session.commit()
        except Exception as e:
            print(e)
            return "При выдачи книги произошла ошибка"
        return redirect("/")
    else:
        return render_template("give_book.html", available_books=available_books,  available_user=available_user)


@app.route("/accept_book", methods=["POST", "GET"])
def accept_books():
    available_books = Books.query.all()
    available_user = Users.query.all()

    if request.method == "POST":
        book = request.form["books"]
        user = request.form["users"]
        id_book = Books.query.filter_by(Title=book).first()
        record = Log(id_book=id_book.id_book, id_user=user, Title=book, action="Returned")
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
    current_user = 214
    start_date = "1901-01-01"
    end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    type_of_log = "Given"
    if request.method == "POST":
        current_user = request.form.get("users")
        end_date = request.form["end"]
        start_date = request.form["start"]
        table_given_books = get_table_log(current_user, type_of_log, start_date, end_date)
        try:
            return render_template("log_given_book.html", table_given_books=table_given_books,
                                   available_user=available_user, current_user=current_user, start_date=start_date,
                                   end_date=end_date, type_of_log=type_of_log)
        except Exception as e:
            return "При формировании журнала была ошибка"
    else:
        table_given_books = get_table_log(current_user, type_of_log, start_date, end_date)
        return render_template("log_given_book.html", table_given_books=table_given_books, current_user=current_user,
                               available_user=available_user, start_date=start_date, end_date=end_date,
                               type_of_log=type_of_log)


@app.route("/log_returned_book", methods=["POST", "GET"])
def log_returned_book():
    available_user = Users.query.all()
    current_user = 214
    start_date = "1901-01-01"
    end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    type_of_log = "Returned"
    if request.method == "POST":
        current_user = request.form.get("users")
        end_date = request.form["end"]
        start_date = request.form["start"]
        table_given_books = get_table_log(current_user, type_of_log, start_date, end_date)
        try:
            return render_template("log_returned_book.html", table_given_books=table_given_books,
                                   available_user=available_user, current_user=current_user, start_date=start_date,
                                   end_date=end_date, type_of_log=type_of_log)
        except Exception as e:
            return "При формировании журнала была ошибка"
    else:
        table_given_books = get_table_log(current_user, type_of_log, start_date, end_date)
        return render_template("log_returned_book.html", table_given_books=table_given_books, current_user=current_user,
                               available_user=available_user, start_date=start_date, end_date=end_date,
                               type_of_log=type_of_log)


@app.route("/download", methods=["POST"])
def download_file():
    format_data = request.form.get("format_downloaded_file")
    current_user = request.form.get("users")
    end_date = request.form["end"]
    start_date = request.form["start"]
    type_of_log = request.form["type_of_log"]
    print(type_of_log)
    table_given_books = get_table_log(current_user, type_of_log, start_date, end_date)
    data_for_download = table_given_books[0:15]
    if format_data == "JSON":
        json_list = []
        for each in data_for_download:
            # Формируем данные для json
            dict_data = {"id_book": each.id_book, "id_user": each.id_user, "Title": each.Title, "action": each.action}
            json_list.append(dict_data)
        with open('test_file.json', 'w', encoding="utf-8") as file:
            json.dump(json_list, file, indent=4)
        return send_file('test_file.json', as_attachment=True)
    else:
        # Формируем данные для CSV
        with open('test_file.csv', 'w', encoding="utf-8", newline='') as file:
            header = []
            counter = 0
            file_writer = csv.DictWriter(file, delimiter=',', fieldnames=header)
            for each in data_for_download:
                print(each)
                # Получаем список ключей
                if counter == 0:
                    for i in each.__dict__.keys():
                        if i != "_sa_instance_state":
                            header.append(i)
                        else:
                            continue
                    counter += 1
                    file_writer.writeheader()
                file_writer.writerow({"id_book": each.id_book, "date_action": each.date_action, "id_user": each.id_user, "Title": each.Title, "action": each.action})
        return send_file('test_file.csv', as_attachment=True)


@app.route("/upload", methods=["POST"])
def upload():
    available_user = Users.query.all()
    upload_format = request.form.get("format_uploaded_file")
    print("Формат " + upload_format)
    if request.files:
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

app.run(debug=True)
