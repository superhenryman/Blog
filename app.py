from flask import Flask, jsonify, render_template, request, abort, redirect
import psycopg2
import logging
import os
import time
import html
from security import verify_signature, sign_client_id

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)
database_url = os.getenv("DATABASE_URL")
ADMIN_PASSWORD = os.getenv("PASSWORD")
ADMIN_USERNAME = os.getenv("USERNAME")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

@app.route("/")
def index():
    return render_template("index.html")

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

def insert_post(post):
    with get_connection() as conn:
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO blog_posts (post) VALUES (%s)", (post, ))
            conn.commit()
            cur.close()
        except Exception as e:
            logging.error(f"Error in insert_post(): {e}")

@app.route("/posts")
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


@app.route("/adminlogin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        try:
            data = request.json
            if not data:
                return jsonify({"error": "Where's your JSON? did you forget it like how your dad forgot you?"})
            username = clean(data.get("username"))
            password = clean(data.get("password"))
            client_id = data.get("clientid")
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                return jsonify({
                    "result": sign_client_id(client_id)
                }), 200 # we return signature, and 200
            else:
                return jsonify({
                    "error": "Invalid Credentials, dumbass."
                }), 401
        except Exception as e:
            logging.error(f"Error occured in admin_login(), {e}")
            return jsonify({
                "error": str(e)
            }), 500
    else:
        return render_template("admin_login.html")

@app.route("/adminPostPlace", methods=["GET", "POST"])
def admin_post():
    try:
        data = request.json
        if not data: return jsonify({"error": "Where's your JSON? did you forget it like how your dad forgot you?"})
        content = clean(data.get("content"))
        client_id = data.get("client_id")
        signature = data.get("signature")
        if not verify_signature(client_id, signature):
            logging.error(f"Someone tried posting without a signature, therefore, their ip is {request.remote_addr}")
            return jsonify({
                "error": "Not authenticated."
            }), 401
        insert_post(post=content)
        return jsonify({
            "result": "success"
        }), 200
    except Exception as e:
        logging.error(f"Error occured in admin_post() {e}")
        return jsonify({
            "error": str(e)
        }), 500

@app.route("/verify_signature", methods=["POST"])
def verify():
    data = request.json
    client_id = data.get("clientid")
    signature = data.get("signature")
    return jsonify({
        "result": verify_signature(client_id, signature)
    })
if __name__ == "__main__": app.run(debug=True) # turn off debug later
