from flask import Blueprint, render_template, jsonify
from app.db import get_db
from flask_jwt_extended import jwt_required, get_jwt_identity
dashboard_bp = Blueprint("dashboard", __name__)

# API route to return dashboard counts as JSON
@dashboard_bp.route('/api/dashboard', methods=['GET'])
@jwt_required()
def dashboard_api():
    conn = get_db()
    user_id = get_jwt_identity()
    try:
        with conn.cursor() as cursor:
             # Get user_id using username
            sql_user_id = "SELECT id FROM users WHERE username=%s"
            cursor.execute(sql_user_id, (user_id,))
            row = cursor.fetchone()
            print(row)
            if not row:
                return jsonify({"success": False, "message": "User not found"}), 404
            user_id = row['id']
            print(user_id)
            sql = """
                SELECT 
                    u.name, u.email, u.mobile, u.address,
                    COUNT(DISTINCT i.id) AS total_insurance_count,
                    COUNT(DISTINCT c.id) AS total_claims_count,
                    COUNT(DISTINCT cpi.id) AS total_picture_tests,
                    COUNT(DISTINCT i.policy_number) AS total_policy_number,
                    SUM(cv.claim_recommended) AS total_claim_you_get
                FROM users u
                LEFT JOIN insurance i ON u.id = i.user_id
                LEFT JOIN claims c ON u.id = c.user_id
                LEFT JOIN claim_property_details cpd ON cpd.claims_id = c.id
                LEFT JOIN claims_value cv ON cv.claims_id = cpd.claims_id
                LEFT JOIN claim_property_image cpi ON cpi.claim_property_details_id = cpd.id
                WHERE u.id = %s
                GROUP BY u.name, u.email, u.mobile, u.address
            """
            cursor.execute(sql, (user_id,))
            counts = cursor.fetchone()
            print(counts)
            return jsonify({
                "total_insurance_count": counts.get('total_insurance_count', 0) if counts else 0,
                "total_claims_count": counts.get('total_claims_count', 0) if counts else 0,
                "total_picture_tests": counts.get('total_picture_tests', 0) if counts else 0,
                "total_claim_you_get": counts.get('total_claim_you_get', 0) if counts else 0,
                "total_policy_number": counts.get('total_policy_number', 0) if counts else 0,
                "name": counts.get('name', 'NA') if counts else 'NA',
                "email": counts.get('email', 'NA') if counts else 'NA',
                "mobile": counts.get('mobile', 'NA') if counts else 'NA',
                "address": counts.get('address', 'NA') if counts else 'NA'
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to serve dashboard HTML page
@dashboard_bp.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")
