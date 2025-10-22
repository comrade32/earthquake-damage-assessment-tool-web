import os
import sys
from flask import Blueprint, render_template, request, redirect, current_app, jsonify, url_for, abort
from app.db import get_db
import pymysql
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
claim_bp = Blueprint('claim', __name__)
import traceback
@claim_bp.route('/claim_insurance')
def claim_insurance():
    return render_template('insurance_form.html')
    
@claim_bp.route('/submit_insurance_detail', methods=['POST'])
def submit_insurance_detail():
    conn = get_db()
    data = request.form
    username = data.get('username')
    insurance_code = data.get('insurance_code')
    policy_number = data.get('policy_number')
    insurance_from = data.get('insurance_from')
    insurance_to = data.get('insurance_to')
    insurance_type = data.get('insurance_type')
    insured = data.get('insured')
    occupation = data.get('occupation')
    insurance_details = data.get('insurance_details')
    status = data.get('status')

    # Validate mandatory fields
    if not username:
        return jsonify({"success": False, "message": "Username missing"}), 400
    if not insurance_code or not insurance_from or not insurance_to:
        return jsonify({"success": False, "message": "Required fields missing"}), 400

    try:
        with conn.cursor() as cursor:
            # Get user_id using username
            sql_user_id = "SELECT id FROM users WHERE username=%s"
            cursor.execute(sql_user_id, (username,))
            row = cursor.fetchone()
            print(row)
            if not row:
                return jsonify({"success": False, "message": "User not found"}), 404
            user_id = row['id']
            print(user_id)
            # Insert insurance record
            sql = """
                INSERT INTO insurance
                (user_id, insurance_code, insurance_from, insurance_to, insurance_type, insured, occupation, insurance_details, is_active, status, created_by, policy_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1, %s, %s, %s)
            """
            cursor.execute(sql, (
                user_id,
                insurance_code,
                insurance_from,
                insurance_to,
                insurance_type,
                insured,
                occupation,
                insurance_details,
                status,
                user_id,
                policy_number
            ))
            conn.commit()
            return redirect('/insurance_claims_detail?user_id=' + str(user_id))
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error inserting insurance: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    

@claim_bp.route('/insurance_claims_detail')
def insurance_claims_detail():
    user_id = request.args.get('user_id')
    # insurance_code_all = request.args.get('insurance_id')
    print(user_id)

    conn = get_db()
    with conn.cursor() as cursor:
        sql_insurance_code_all = "SELECT insurance_code,policy_number FROM insurance WHERE user_id=%s"
        cursor.execute(sql_insurance_code_all, (user_id,))
        insurance_code_all = cursor.fetchall()
        print(insurance_code_all)
    # Pass the data to the template
    return render_template('insurance_claims_detail.html', insurance_code_all=insurance_code_all, user_id=user_id)

@claim_bp.route('/api/insurance_claims_detail', methods=['GET'])
@jwt_required()
def insurance_claims_detail_api():
    conn = get_db()
    user_identity = get_jwt_identity()

    with conn.cursor() as cursor:
        # Get user id from username (or user identity)
        sql_user_id = "SELECT id FROM users WHERE username = %s"
        cursor.execute(sql_user_id, (user_identity,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"success": False, "message": "User not found"}), 404
        user_id = row['id']

        # Get all insurance codes for this user
        sql_insurance_code_all = "SELECT insurance_code FROM insurance WHERE user_id = %s"
        cursor.execute(sql_insurance_code_all, (user_id,))
        insurance_code_all = cursor.fetchall()
        print(insurance_code_all)
    # Return JSON response with user_id and insurance codes
    return jsonify({
        "user_id": user_id,
        "insurance_codes": insurance_code_all
    })

@claim_bp.route('/api/get_policy', methods=['GET'])
def get_policy_api():
    insurance_code = request.args.get('insurance_code')
    conn = get_db()
    with conn.cursor() as cursor:
        sql_policy = "SELECT policy_number FROM insurance WHERE insurance_code = %s"
        cursor.execute(sql_policy, (insurance_code,))
        policy_number_all = [row['policy_number'] for row in cursor.fetchall()]
    return jsonify({
        "policy_number_all": policy_number_all
    })


@claim_bp.route('/submit_insurance_claims', methods=['POST'])
def submit_insurance_claims():
    conn = get_db()
    data = request.form
    user_id = data.get('user_id')
    claims_code = data.get('claims_code')
    insurance_id = data.get('insurance_id')
    claim_details = data.get('claim_details')
    time_of_loss = data.get('time_of_loss')
    situation_of_loss = data.get('situation_of_loss')
    cause_of_loss = data.get('cause_of_loss')
    policy_number = data.get('policy_number')
    is_active = 1
    status = 'inactive'
    created_by = user_id  # use user_id from form

    if not user_id or not claims_code or not insurance_id:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO claims
                (user_id, claims_code, insurance_id, claim_details, time_of_loss, situation_of_loss, cause_of_loss, is_active, status, created_by, policy_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                user_id,
                claims_code,
                insurance_id,
                claim_details,
                time_of_loss,
                situation_of_loss,
                cause_of_loss,
                is_active,
                status,
                created_by,
                policy_number
            ))
            conn.commit()
            inserted_id = cursor.lastrowid
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error inserting claims: {e}")
        return jsonify({"success": False, "message": "Error saving claims"}), 500

    return redirect('/damaged_property_image?claims_id=' + str(inserted_id) + '&claims_code=' + str(claims_code))

@claim_bp.route('/damaged_property_image')
def damaged_property_image():
    claims_id = request.args.get('claims_id')
    claims_code = request.args.get('claims_code')
    print(claims_id)
    print(claims_code)
    return render_template('damaged_property_image.html',claims_id=claims_id,claims_code=claims_code)

@claim_bp.route('/submit_damaged_property_image', methods=['POST'])
def submit_damaged_property_image():
    conn = get_db()

    if 'file_name' not in request.files:
        return jsonify({"success": False, "message": "No file part"}), 400
    
    file = request.files['file_name']
    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file"}), 400

    filename = secure_filename(file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)

    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    try:
        ############# Image Analysis part start here #####################
        print(filepath)
        from app.routes.image_area_calculater import calculate_crack_area
        image_response = calculate_crack_area(filepath)
        crack_area = image_response['crack_area']
        crack_file_image_path = image_response['plot_path']
        crack_filename = image_response['filename']
        damage_length = image_response['length_ft']
        damage_breadth = image_response['width_ft']
        print("BP32")
        print(damage_length)
        print(damage_breadth)
        print(crack_area)
        print(crack_filename)
        ############## Image Analysis part start here #####################
    except Exception as e:
        current_app.logger.error(f"Failed to import calculate_crack_area: {e}", exc_info=True)
        return jsonify({"success": False, "message": "Internal server error"}), 500
    
    # Call detect_earthquake function passing file object
    with open(filepath, 'rb') as img_file:
        from app.routes.earthquake_detection import e_detect_earthquake
        response, status_code = e_detect_earthquake(img_file)
        detection_data = response.json  # detection_data is a dict
        confidence = detection_data.get("confidence")
        crack_percent = detection_data.get("probabilities", {}).get("Positive (Crack Detected)")
        non_crack_percent = detection_data.get("probabilities", {}).get("Negative (No Crack)")
        ai_decision = detection_data.get("predicted_class")

    data = request.form
    claims_id = data.get('claims_id')
    claims_code = data.get('claims_code')
    file_format = data.get('file_format')
    file_desc = data.get('file_desc')
    is_active = 1
    status = 'inactive'

    try:
        with conn.cursor() as cursor:
            ################ Save to claim_property_details table Start here ################
            claim_property_details_area = """
                                            INSERT INTO claim_property_details
                                            (claims_id, damage_area, damage_length, damage_breadth)
                                            VALUES (%s, %s, %s, %s)
                                        """
            cursor.execute(claim_property_details_area, (
                    claims_id,
                    crack_area,
                    damage_length,
                    damage_breadth                   
                ))
            claim_property_details_id = cursor.lastrowid

            # ############# Save to claim_property_details table end here ######################

            ################ Save to claim_property_assessment table start here##################
            if claims_id and detection_data:
                sql_assessment = """
                    INSERT INTO claim_property_assessment
                    (claims_id, confidence, crack_percent, non_crack_percent, ai_decision)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql_assessment, (
                    claims_id,
                    confidence,
                    crack_percent,
                    non_crack_percent,
                    ai_decision                    
                ))
            ################ Save to claim_property_assessment table end here ####################

            #################Save file info to claim_property_image table start here #############
            sql_image = """
                INSERT INTO claim_property_image
                (claim_property_details_id, file_name, file_location, file_format, file_desc, is_active, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql_image, (
                claim_property_details_id,
                crack_filename,
                crack_file_image_path,
                file_format,
                file_desc,
                is_active,
                status
            ))
            #################Save file info to claim_property_image table end here ###############
            conn.commit()
    except Exception as e:
        conn.rollback()
        error_message = f"Error saving file or assessment info: {e}\n{traceback.format_exc()}"
        current_app.logger.error(error_message)
        return jsonify({"success": False, "message": f"Database error: {str(e)}"}), 500

    return redirect('/damaged_property_details?claims_id=' + str(claims_id) + '&claim_property_details_id=' + str(claim_property_details_id) + '&claims_code=' + str(claims_code))
    
@claim_bp.route('/damaged_property_details')
def damaged_property_details():
    claims_id = request.args.get('claims_id')
    claims_code = request.args.get('claims_code')
    claim_property_details_id = request.args.get('claim_property_details_id')

    conn = get_db()  # Ensure you get your database connection here
    with conn.cursor() as cursor:
        sql_damage_area = "SELECT damage_area FROM claim_property_details WHERE id = %s"
        cursor.execute(sql_damage_area, (claim_property_details_id,))
        damage_area = cursor.fetchone()  # This returns a tuple or dict depending on cursor type
    
    print(damage_area)
    return render_template(
        'damaged_property_details.html',
        claims_id=claims_id,
        claim_property_details_id=claim_property_details_id,
        damage_area=damage_area,
        claims_code=claims_code
    )

@claim_bp.route('/submit_damaged_property', methods=['POST'])
def submit_damaged_property():
    conn = get_db()
    data = request.form
    claims_id = data.get('claims_id')
    claim_property_details_id = data.get('claim_property_details_id')
    claims_code = data.get('claims_code')
    property_type = data.get('property_type')
    wall_type = data.get('wall_type')
    damage_area = float(data.get('damage_area', 0))
    damage_height = float(1)
    rate_per_sqft = float(data.get('rate_per_sqft', 0))
    is_active = 1
    status = 'inactive'
    exchange_rate = 88
    claim_recommended = damage_area * rate_per_sqft
    claim_recommended_usd = claim_recommended / exchange_rate

    if not claim_property_details_id or not claims_id:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    try:
        with conn.cursor() as cursor:
            sql = """
                UPDATE claim_property_details
                SET
                   claims_id = %s,
                   property_type = %s,
                   wall_type = %s,
                   damage_area = %s,
                   damage_height = %s,
                   rate_per_sqft = %s,
                   is_active = %s,
                   status = %s
                WHERE id = %s
            """
            cursor.execute(sql, (
                claims_id,
                property_type,
                wall_type,
                damage_area,
                damage_height,
                rate_per_sqft,
                is_active,
                status,
                claim_property_details_id,
            ))
            if claims_id and claim_recommended:
                sql_claims_value = """
                    INSERT INTO claims_value
                    (claims_id, claim_recommended)
                    VALUES (%s, %s)
                """
                cursor.execute(sql_claims_value, (
                    claims_id,
                    claim_recommended_usd                    
                ))
            conn.commit()
            print('Brajendra')
    except Exception as e:
        conn.rollback()
        current_app.logger.error(f"Error updating damaged property: {e}")
        return jsonify({"success": False, "message": "Error saving damaged property details"}), 500

    return redirect('/new_report?claims_id=' + str(claims_id) + '&claim_property_details_id=' + str(claim_property_details_id) + '&claims_code=' + str(claims_code))


@claim_bp.route('/new_report')
def new_report():
    data = request.args  # or request.form if POST
    claims_id = data.get('claims_id')
    claim_property_details_id = data.get('claim_property_details_id')
    claims_code = data.get('claims_code')
    
    if not claims_id:
        abort(400, description="Missing claims_id")
    if not claims_code:
        abort(400, description="Missing claims_code")

    conn = get_db()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM claims WHERE claims_code=%s", (claims_code,))
            get_user_id = cursor.fetchone()
            if get_user_id is None:
                abort(404, description="User not found")
            user_id = get_user_id['user_id']
            
            cursor.execute("SELECT insurance_code FROM insurance WHERE user_id=%s", (user_id,))
            all_insurance_code = cursor.fetchall()

            cursor.execute("SELECT insurance_id FROM claims WHERE id=%s", (claims_id,))
            selected_insurance = cursor.fetchone()

            cursor.execute("SELECT policy_number FROM claims WHERE id=%s", (claims_id,))
            selected_policy = cursor.fetchone()

            cursor.execute("SELECT claims_code FROM claims WHERE claims_code = %s", (claims_code,))
            selected_claim = cursor.fetchone()

    except Exception as e:
        current_app.logger.error(f"DB error in new_report: {e}")
        abort(500, description="Database error")

    return render_template(
        'new_report.html',
        all_insurance_code=all_insurance_code,
        get_select_insurance_code_one=selected_insurance,
        get_select_policy_number_one=selected_policy,
        get_select_claims_code_one=selected_claim,
        claims_id=claims_id,
        claim_property_details_id=claim_property_details_id,
        claims_code=claims_code,
    )

@claim_bp.route('/get_policy_dropdown')
def get_policy_dropdown():
    insurance_code = request.args.get('insurance_code')
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute("SELECT policy_number FROM insurance WHERE insurance_code = %s", (insurance_code,))
        policies = cursor.fetchall()
    # Return JSON list of policy numbers
    return jsonify([p['policy_number'] for p in policies])

@claim_bp.route('/get_claims_code_dropdown')
def get_claims_code_dropdown():
    policy_number = request.args.get('policy_number')
    conn = get_db()
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT claims_code FROM claims WHERE policy_number = %s", 
            (policy_number,)
        )
        claims_codes = cursor.fetchall()
    return jsonify([c['claims_code'] for c in claims_codes])

@claim_bp.route('/get_assessment_data')
def get_assessment_data():
    claims_code = request.args.get('claims_code')
    conn = get_db()
    with conn.cursor() as cursor:
        sql = """SELECT 
                    cpi.file_name,
                    cpa.ai_decision,
                    cpa.confidence,
                    cpa.crack_percent,
                    cv.claim_recommended,
                    cpd.damage_area,
                    cpd.damage_length,
                    cpd.damage_breadth,
                    cpa.id as cpa_id
                FROM claims as c 
                LEFT JOIN claim_property_details cpd ON cpd.claims_id = c.id
                LEFT JOIN claim_property_image cpi ON cpi.claim_property_details_id = cpd.id
                LEFT JOIN claim_property_assessment cpa ON cpa.claims_id = c.id
                LEFT JOIN claims_value cv ON cv.claims_id = c.id
                WHERE c.claims_code = %s"""
        cursor.execute(sql, (claims_code,))
        get_assessment_data = cursor.fetchone()
    return jsonify(get_assessment_data if get_assessment_data else {})

@claim_bp.route('/submit_claim_report', methods=['POST'])
def submit_claim_report():
    data = request.form
    claims_id = data.get('claims_id')
    claim_property_details_id = data.get('claim_property_details_id')
    claims_code = data.get('claims_code')
    cpa_id = data.get('cpa_id')
    user_inference = data.get('user_inference')
    final_damage_area = data.get('final_damage_area') or 0
    final_damage_cost = data.get('final_damage_cost') or 0


    conn = get_db()
    with conn.cursor() as cursor:
        sql = """
            UPDATE claim_property_assessment
            SET
                user_inference = %s,
                final_damage_area = %s,
                final_damage_cost = %s
            WHERE id = %s
        """
        # Make sure you pass the correct id for 'id' in WHERE clause
        cursor.execute(sql, (
            user_inference,
            final_damage_area,
            final_damage_cost,
            cpa_id,  # Use correct id field here
        ))
        conn.commit()

    return redirect('/new_report?claims_id=' + str(claims_id) +
                    '&claim_property_details_id=' + str(claim_property_details_id) +
                    '&claims_code=' + str(claims_code) + 
                    '&user_inference=' + str(user_inference) + 
                    '&final_damage_area=' + str(final_damage_area) + 
                    '&final_damage_cost=' + str(final_damage_cost))



@claim_bp.route('/damaged_property_calculation')
def damaged_property_calculation():
    claims_id = request.args.get('claims_id')
    conn = get_db()
    try:
        with conn.cursor() as cursor:
            sql_user_id = "SELECT user_id FROM claims WHERE id=%s"
            cursor.execute(sql_user_id, (claims_id,))
            result = cursor.fetchone()
            print(result)
            if result:
                user_id = result.get('user_id')
            else:
                user_id = 'NULL'
            sql = """
                    SELECT 
                        u.name,
                        c.insurance_id AS insurance_id,
                        c.policy_number AS policy_number,
                        c.claims_code AS claim_id,
                        cpi.file_name,
                        cpa.ai_decision,
                        cpa.confidence,
                        cpa.crack_percent,
                        cpa.non_crack_percent,
                        cv.claim_recommended
                    FROM users as u
                    INNER JOIN claims as c ON c.user_id = u.id
                    LEFT JOIN claim_property_details cpd ON cpd.claims_id = c.id
                    LEFT JOIN claim_property_image cpi ON cpi.claim_property_details_id = cpd.id
                    LEFT JOIN claim_property_assessment cpa ON cpa.claims_id = c.id
                    LEFT JOIN claims_value cv ON cv.claims_id = c.id
                    WHERE u.id= %s;
                    """
            cursor.execute(sql, (user_id,))
            records = cursor.fetchall()
        print(records)
        return render_template('damaged_property_calculation.html',records=records)  
    except Exception as e:
        current_app.logger.error(e)
        return jsonify({"success": False, "message": f"Page not found error: {str(e)}"}), 500

@claim_bp.route('/insurance_report')
def insurance_report():
    return render_template("report.html")

@claim_bp.route('/api/insurance_report', methods=['GET'])
@jwt_required()
def insurance_report_api():
    conn = get_db()
    try:
        user_identity = get_jwt_identity()

        with conn.cursor() as cursor:
            sql_user_id = "SELECT id FROM users WHERE username = %s"
            cursor.execute(sql_user_id, (user_identity,))
            user_row = cursor.fetchone()
            if not user_row:
                return jsonify([])  # return empty list if user not found
            user_id = user_row['id']

        with conn.cursor() as cursor:
            sql_data = """
                SELECT 
                    u.name,
                    u.email,
                    i.insurance_code,
                    i.insurance_type,
                    c.policy_number,
                    c.claims_code,
                    cpd.property_type,
                    cpd.wall_type,
                    cpd.damage_area,
                    cpd.rate_per_sqft,
                    cpa.confidence,
                    cpa.crack_percent,
                    cpa.non_crack_percent,
                    cpa.ai_decision,
                    cpi.file_name
                FROM users AS u
                INNER JOIN insurance AS i ON i.user_id = u.id
                INNER JOIN claims AS c ON c.insurance_id = i.insurance_code
                INNER JOIN claim_property_details AS cpd ON cpd.claims_id = c.id
                INNER JOIN claim_property_assessment AS cpa ON cpa.claims_id = cpd.claims_id
                INNER JOIN claim_property_image AS cpi ON cpi.claim_property_details_id = cpd.id
                WHERE u.id = %s
            """
            cursor.execute(sql_data, (user_id,))
            records = cursor.fetchall()

        return jsonify(records if records else [])

    except Exception as e:
        return jsonify({'msg': 'Database error: ' + str(e)}), 500


