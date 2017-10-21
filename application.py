from flask import Flask, redirect, render_template, request, session, url_for, json
from flask_session import Session
import sqlite3
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp

conn = sqlite3.connect('users.db')
db = conn.cursor()
db.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)')


app = Flask(__name__)
Session(app)

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


@app.route("/")
def main():
    return render_template("main.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        user_name = request.form['inputName']
        email = request.form['inputEmail']
        password = request.form['inputPassword']

        if len(user_name) < 1:
            return render_template("apology.html")

        if user_name and email and password:
            hashed_password = pwd_context.encrypt(password)
            result = db.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user_name, hashed_password))
            conn.commit()
            if not result:
                return render_template("signup.html")

            #session["user_id"] = result
            return redirect(url_for("profile"))
        else:

            return render_template("apology.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "GET":
        return render_template("signin.html")
    elif request.method == "POST":
        name = request.form['inputName']
        password = request.form['inputPassword']
        row = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])

        if len(row) != 1 or not pwd_context.verify(password, row[0]["hash"]):
            return render_template("apology.html")

        session["user_id"] = row[0]["id"]

        if name == row.get('username') and pwd_context.verify(password, row[0]["hash"]):
            return redirect(url_for("pofile"))
        else:
            return render_template("apology.html")


@app.route("/profile")
def profile():
    return render_template("profile.html")


if __name__ == "__main__":
    app.run()
