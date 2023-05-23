#!/usr/bin/env python3
# coding: utf-8

from datetime import timedelta
import hashlib
import sqlite3

from flask import (Flask, Response, redirect, render_template, request,
                   session)

sqlite_dbfile = "./vulnerable.db"
login_admin_password = "LoveSushi"

app = Flask(__name__, template_folder="templates", static_folder="templates/assets")
app.config["SECRET_KEY"] = "0000000000000000000000000000000000000000000000000000000000000000"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=1)
app.config["SESSION_COOKIE_PATH"] = "/"
app.config["SESSION_COOKIE_SECURE"] = True
app.jinja_env.auto_reload = True

@app.after_request
def add_header(resp):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    resp.headers['Cache-Control'] = 'public, max-age=0'
    return resp

@app.route(
    "/login",
    methods=["GET", "POST"]
)
async def login():
    status_code: int = 200
    message: str = None

    if request.method == "POST":
        username: str = request.form.get("username", type=str)
        password: str = request.form.get("password", type=str)

        # ignore root user
        if username == "root":
            return redirect("/")

        connection = sqlite3.connect(sqlite_dbfile)
        cursor = connection.cursor()

        result = False
        try:
            # Table作成
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS account(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT
                );
            """)
            # 試験用adminアカウント作成
            cursor.execute("""
                INSERT OR IGNORE INTO account(id, username, password)
                VALUES (1, 'admin', '{:s}');
            """.format(hashlib.sha256(login_admin_password.encode("utf-8")).hexdigest()))

            #**** ダメな実装 ****
            cursor.execute("""
                SELECT * FROM account WHERE username = '{:s}' AND password = '{:s}' LIMIT 1;
            """.format(username, hashlib.sha256(password.encode("utf-8")).hexdigest()))

            fetch_row = cursor.fetchone()
            # 雑な判定
            if fetch_row is not None and len(fetch_row) > 0:
                result = True
                username = fetch_row[1]

            connection.commit()
        finally:
            cursor.close()
            connection.close()

        if result == True:
            session["username"] = username
            return redirect("/")
        else:
            status_code = 401
            message = "Login failure"
    else:
        if "username" in session:
            return redirect("/")

    return Response(render_template(
            "login.html",
            message=message
        ), status=status_code)

@app.route(
    "/logout"
)
async def logout():
    session.pop("username", None)
    session.clear()
    return redirect("/")

@app.route(
    "/"
)
async def dashboard():
    if "username" not in session:
        return redirect("/login")

    return render_template(
            "index.html",
            username=session["username"]
        )

@app.errorhandler(404)
def error_404(error):
    return Response(render_template("error_404.html"), status=404)


if __name__ == "__main__":
    app.run(port=8080, debug=True)
