from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3
import random
import string
import os
import re
import dns.resolver
from werkzeug.security import generate_password_hash, check_password_hash

def generate_secret(length: int = 40) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", generate_secret())

DB_PATH = "data.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                email TEXT,
                password TEXT
            );
        """)
        conn.commit()

init_db()

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

def is_email_syntax(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def domain_has_mail(domain):
    try:
        dns.resolver.resolve(domain, 'MX', lifetime=5)
        return True
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers, dns.exception.Timeout):
        try:
            dns.resolver.resolve(domain, 'A', lifetime=5)
            return True
        except Exception:
            return False
    except Exception:
        return False

def is_email_valid(email):
    if not is_email_syntax(email):
        return False
    domain = email.split('@')[-1]
    return domain_has_mail(domain)

@app.route("/submit_registration", methods=["POST"])
def submit_registration():
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not username or not email or not password:
        return render_template("index.html", message="Заполните все поля.")

    if not is_email_valid(email):
        return render_template("index.html", message="Неверный или несуществующий email домен.")

    hashed = generate_password_hash(password)

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO data (username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed)
            )
            conn.commit()
    except sqlite3.IntegrityError:
        return render_template("index.html", message="Пользователь уже существует.")

    return render_template("index.html", message="Регистрация прошла успешно.")

@app.route("/login", methods=["GET"])
def login_page():
    return render_template("Enter.html")

@app.route("/submit_login", methods=["POST"])
def login_user():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        return render_template("Enter.html", message="Заполните все поля.")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM data WHERE username = ?", (username,))
        row = cursor.fetchone()

    if row is None:
        return render_template("Enter.html", message="Неверный логин или пароль.")

    user_id, user_name, stored_hash = row

    if check_password_hash(stored_hash, password):
        session["user_id"] = user_id
        session["username"] = user_name
        return redirect(url_for("profile"))
    else:
        return render_template("Enter.html", message="Неверный логин или пароль.")

@app.route("/profile", methods=["GET"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("profile.html", username=session.get("username"))

@app.route("/logout", methods=["GET"])
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)