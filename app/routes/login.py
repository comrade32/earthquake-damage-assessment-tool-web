from flask import Blueprint, request, jsonify, render_template, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from flask_bcrypt import Bcrypt
import pymysql
import datetime
from app.blocklist import BLOCKLIST

login_bp = Blueprint("login", __name__)
bcrypt = Bcrypt()  # Initialize once in app factory

@login_bp.route("/", methods=["GET"])
def login_page():
    return render_template("login.html")

@login_bp.route("/api/login", methods=["POST"])
def login_api():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    conn = pymysql.connect(
        host=current_app.config["DB_HOST"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
        db=current_app.config["DB_NAME"],
        port=current_app.config["DB_PORT"]
    )
    try:
        with conn.cursor() as cursor:
            sql = "SELECT password,status FROM users WHERE username=%s"
            cursor.execute(sql, (username,))
            row = cursor.fetchone()

            if row is None:
                return jsonify({"success": False, "message": "User not found"}), 404

            stored_hash, status = row

            if not bcrypt.check_password_hash(stored_hash, password):
                return jsonify({"success": False, "message": "Invalid credentials"}), 401

            if status.lower() != "active":   # or status != 1 if using int
                return jsonify({
                    "success": False,
                    "message": "Your account is currently inactive. Please contact the system administrator to activate your account or for further assistance."
                }), 403

            expires = datetime.timedelta(minutes=current_app.config["ACCESS_TOKEN_EXPIRE_MINUTES"])
            token = create_access_token(identity=username, expires_delta=expires)
            return jsonify({"success": True, "token": token})
    finally:
        conn.close()
    #         stored_hash = row[0]

    #         if bcrypt.check_password_hash(stored_hash, password):
    #             expires = datetime.timedelta(minutes=current_app.config["ACCESS_TOKEN_EXPIRE_MINUTES"])
    #             token = create_access_token(identity=username, expires_delta=expires)
    #             return jsonify({"success": True, "token": token})
    #         else:
    #             return jsonify({"success": False, "message": "Invalid credentials"}), 401
    # finally:
    #     conn.close()


@login_bp.route("/api/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]  # Get the unique identifier of the JWT
    BLOCKLIST.add(jti)      # Add it to the blocklist
    return jsonify({"msg": "Successfully logged out"}), 200


@login_bp.route('/api/auth-check', methods=['GET'])
@jwt_required()
def auth_check():
    current_user = get_jwt_identity()
    return jsonify({"logged_in_as": current_user}), 200


@login_bp.route('/api/get_user_id', methods=['GET'])
@jwt_required()
def get_user_id():
    user_id = get_jwt_identity()
    return jsonify({"user_id": user_id})