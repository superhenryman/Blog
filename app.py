from flask import Flask, jsonify, render_template, redirect, request, abort
import psycopg2
import logging
import os
import time
import html
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
database_url = os.getenv("DATABASE_URL")
ADMIN_PASSWORD = os.getenv("PASSWORD")
ADMIN_USERNAME = os.getenv("USERNAME")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")  # Set a strong secret key

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route("/adminlogin")
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        username = clean(form.username)
        password = clean(form.password)
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            return redirect("/adminPostPlace")
        else:
            return render_template("admin_login.html", form=form, error="Invalid Password and/or Username")
    return render_template("admin_login.html", form=form)



def clean(text: str) -> str:
    return str(html.escape(text, quote=True))

def get_connection():
    retry_count = 5
    for i in range(retry_count):
        try:
            conn = psycopg2.connect(database_url)
            return conn
        except Exception as e:
            logging.error(f"Attempt {i} failed: {e}")
            time.sleep(2 ** i)
    raise Exception("I can't connect :(")

def init_db():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS blog_posts(
                    id SERIAL PRIMARY KEY,
                    post TEXT NOT NULL           
                )""")
            conn.commit()
            cursor.close()
    except Exception as e:
        logging.error(f"Error occured in init_db(): {e}")

init_db()

def require_password():
    if request.headers.get('X-API-KEY') != ADMIN_PASSWORD:
        abort(403)


@app.route("/retrieveposts")
def get_posts():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM blog_posts ORDER BY id ASC")
            rows = cursor.fetchall()
            conn.commit()
            cursor.close()
        return jsonify(rows)
    except Exception as e:
        logging.error(f"Error occured in get_posts(): {e}")
        return jsonify({
            "error": "Could not retrieve posts."
        })


if __name__ == "__main__": app.run(debug=True) # turn off debug later
