from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)


class Mylibrary(db.Model):
    id_user = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Surname = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return '<Mylibrary %r>' % self.title


class Books(db.Model):
    id_book = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(100), nullable=False)
    Author = db.Column(db.String(100), nullable=False)
    Available = db.Column(db.String(100))

    #def __repr__(self):
        #return '<Books %r>' % self.Title


class Log(db.Model):
    id_book = db.Column(db.Integer, primary_key=True)
    date_action = db.Column(db.DateTime, default=datetime.utcnow)
    id_user = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(100))

    def __init__(self, id_book, id_user,action):
        self.id_book = id_book
        self.id_user = id_user
        self.action = action


@app.route("/")
def hello_world():
    return render_template("index.html")


@app.route("/list_users")
def books():
    list_user = Mylibrary.query.first()
    return render_template("list_users.html", list_user=list_user)


@app.route("/add_user", methods=["POST", "GET"])
def add_user():
    if request.method == "POST":
        Name = request.form["name"]
        Surname = request.form["surname"]
        Email = request.form["email"]

        user = Mylibrary(Name=Name, Surname=Surname, Email=Email)

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
        Author = request.form["author"]
        Title = request.form["title"]
        book = Books(Author=Author, Title=Title, Available=True)

        try:
            db.session.add(book)
            db.session.commit()
        except Exception as e:
            print(e)
            return "При добавление пользователя произошла ошибка"

        return redirect("/")
    else:
        return render_template("add_book.html")


@app.route("/available_books")
def show_available_books():
    available_books = Books.query.all()
    print(available_books)
    return render_template("available_books.html", available_books=available_books)


@app.route("/give_book", methods=["POST", "GET"])
def give_books():
    all_books = Books.query.all()
    available_user = Mylibrary.query.all()
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
        print(book)
        try:
            db.session.add(record)
            db.session.commit()
        except Exception as e:
            print(e)
            return "При выдачи книги произошла ошибка"

        return redirect("/")
    else:
        return render_template("give_book.html", available_books =available_books,  available_user=available_user)


@app.route("/accept_book", methods=["POST", "GET"])
def accept_books():
    available_books = Books.query.all()
    available_user = Mylibrary.query.all()
    if request.method == "POST":
        book = request.form["books"]
        user = request.form["users"]

        record = Log(id_book=book, id_user=user, action="Returned")

        try:
            db.session.add(record)
            db.session.commit()
        except Exception as e:
            print(e)
            return "При выдачи книги произошла ошибка"

        return redirect("/")
    else:
        return render_template("accept_book.html", available_books=available_books, available_user=available_user)


app.run(debug=True)
