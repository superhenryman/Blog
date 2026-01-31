from flask import Flask, jsonify, render_template, request, abort, redirect, url_for, session
from flask_wtf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import psycopg2
import logging
import os
import time
import bleach

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
database_url = os.getenv("DATABASE_URL")
ADMIN_PASSWORD = os.getenv("PASSWORD")
ADMIN_USERNAME = os.getenv("USERNAME")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.secret_key = os.getenv("SECRET_KEY")
csrf = CSRFProtect()
csrf.init_app(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=True
)

def clean(text: str) -> str:
    return bleach.clean(text=text)

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
                    title TEXT NOT NULL,
                    post TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()           
                );""")
            conn.commit()
            cursor.close()
    except Exception as e:
        logging.error(f"Error occured in init_db(): {e}")

init_db()

def require_password():
    if request.headers.get('X-API-KEY') != ADMIN_PASSWORD:
        abort(403)

def insert_post(title, post) -> bool:
    with get_connection() as conn:
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO blog_posts (title, post) VALUES (%s, %s)", (title, post))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            conn.rollback()
            logging.error(f"Error in insert_post(): {e}")
            return False

def delete_post(id) -> bool:
    with get_connection() as conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM blog_posts WHERE id = %s", (id, ))
            conn.commit()
            cur.close()
            return True
        except Exception as e:
            conn.rollback()
            logging.error(f"Error in delete_post(): {e}")
            return False

@app.route("/fetch_posts", methods=["GET"])
def get_posts():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM blog_posts ORDER BY id DESC")
            rows = cursor.fetchall()
            cursor.close()
            columns = ['id', 'title', 'post', 'created_at']
            data = [dict(zip(columns, row)) for row in rows]
            return jsonify(data)
    except Exception as e:
        logging.error(f"Error occured in get_posts(): {e}")
        return jsonify({
            "error": "Could not retrieve posts."
        }), 500
    
@app.route("/", methods=["GET"])
def index(): return render_template("index.html")

@app.route("/admin_panel", methods=["GET"])
def admin_panel():
    if session.get("is_admin"):
        return render_template("admin_panel.html")
    else:
        return redirect(url_for("index"))
    
@app.route("/create_post", methods=["POST"])
@limiter.limit("1 per minute")
def create_post():
    if session.get("is_admin"):
        data = request.get_json()
        title = clean(data.get("title"))
        post = clean(data.get("post"))
        if insert_post(title, post): return jsonify({"success": True})
        else: return jsonify({ "success": False })
    else: abort(403)

@app.route("/login_check", methods=["POST"])
@csrf.exempt
@limiter.limit("5 per minute")
def login_check():
    data = request.json
    username = data.get("username", "")
    password = data.get("password", "")
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session["is_admin"] = True
        return jsonify({
            "success": True
        }), 200
    else:
        return jsonify({
            "success": False
        }), 401
    
@app.route("/admin_login")
def admin_login():
    if session.get("is_admin"):
        return redirect(url_for("admin_panel"))
    return render_template("admin_login.html")



if __name__ == "__main__": app.run() # turn off debug later
