from flask import Blueprint, request, jsonify, render_template, current_app
from flask_bcrypt import Bcrypt
import pymysql
import datetime

signup_bp = Blueprint("signup", __name__)
bcrypt = Bcrypt()  # Make sure to initialize in your app factory

@signup_bp.route("/signup", methods=["GET"])
def signup_page():
    return render_template("signup.html")

@signup_bp.route("/api/signup", methods=["POST"])
def signup_api():
    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    mobile = data.get("mobile")
    address = data.get("address")
    username = data.get("username")
    password = data.get("password")
    role = "user"
    organization_id = 1
    status = "inactive"

    if not all([name, email, role, username, password]):
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    # Hash password using Flask-Bcrypt and decode bytes to string
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    conn = pymysql.connect(
        host=current_app.config["DB_HOST"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
        db=current_app.config["DB_NAME"],
        port=current_app.config["DB_PORT"],
        cursorclass=pymysql.cursors.DictCursor
    )
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username=%s OR email=%s", (username, email))
            existing = cursor.fetchone()
            if existing:
                return jsonify({"success": False, "message": "Username or email already exists"}), 409

            sql = """
            INSERT INTO users (name, email, mobile, address, role, organization_id, username, password, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            cursor.execute(sql, (
                name, email, mobile, address, role, organization_id, username, hashed_password, status
            ))
            conn.commit()

            return jsonify({"success": True, "message": "User registered successfully"})
    finally:
        conn.close()
