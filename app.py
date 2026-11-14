
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
CORS(app)


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():
    return "BloodLink Backend is Running!"


# ==========================================
# USER REGISTRATION
# ==========================================

@app.route("/register", methods=["POST"])
def register():

    data = request.get_json(silent=True)

    required_fields = ["name", "email", "phone", "password", "role"]

    if not data or any(not data.get(field) for field in required_fields):
        return jsonify({"error": "All required fields are required"}), 400

    name = str(data["name"]).strip()
    email = str(data["email"]).strip().lower()
    phone = str(data["phone"]).strip()
    password = data["password"]
    role = str(data["role"]).strip().lower()

    if not name or not email or not phone:
        return jsonify({"error": "Name, email and phone cannot be empty"}), 400

    if not isinstance(password, str) or len(password) < 8:
        return jsonify({"error": "Password must contain at least 8 characters"}), 400

    if role not in ["donor", "recipient", "both"]:
        return jsonify({"error": "Invalid role"}), 400

    blood_group = data.get("blood_group")
    location = data.get("location")

    if role in ["donor", "both"]:

        if not blood_group or not location or not str(location).strip():
            return jsonify({
                "error": "Blood group and location are required for donors"
            }), 400

        if blood_group not in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
            return jsonify({"error": "Invalid blood group"}), 400

    password_hash = generate_password_hash(password)

    connection = get_connection()

    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO Users
            (name, email, phone, password_hash, role)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, email, phone, password_hash, role)
        )

        user_id = cursor.lastrowid

        if role in ["donor", "both"]:

            cursor.execute(
                """
                INSERT INTO Donors
                (user_id, blood_group, location)
                VALUES (%s, %s, %s)
                """,
                (user_id, blood_group, str(location).strip())
            )

        connection.commit()

        return jsonify({
            "message": "Registration successful",
            "user_id": user_id,
            "name": name,
            "email": email,
            "role": role
        }), 201

    except Exception as error:

        connection.rollback()

        if getattr(error, "errno", None) == 1062:
            return jsonify({
                "error": "Email or phone number already registered"
            }), 409

        print("Registration error:", error)
        return jsonify({"error": "Registration failed"}), 500

    finally:
        if cursor:
            cursor.close()
        connection.close()


# ==========================================
# USER LOGIN
# ==========================================

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json(silent=True)

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({
            "error": "Email and password are required"
        }), 400

    email = str(data["email"]).strip().lower()
    password = data["password"]

    connection = get_connection()

    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT user_id, name, email, phone, password_hash, role
            FROM Users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()

        if not user or not check_password_hash(user["password_hash"], password):
            return jsonify({
                "error": "Invalid email or password"
            }), 401

        user_response = {
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
            "phone": user["phone"],
            "role": user["role"]
        }

        if user["role"] in ["donor", "both"]:

            cursor.execute(
                """
                SELECT donor_id, blood_group, location, availability
                FROM Donors
                WHERE user_id = %s
                """,
                (user["user_id"],)
            )

            donor = cursor.fetchone()

            if donor:
                user_response["donor"] = donor

        return jsonify({
            "message": "Login successful",
            "user": user_response
        }), 200

    except Exception as error:

        print("Login error:", error)
        return jsonify({"error": "Login failed"}), 500

    finally:
        if cursor:
            cursor.close()
        connection.close()


# ==========================================
# CREATE BLOOD REQUEST
# ==========================================

@app.route("/requests", methods=["POST"])
def create_request():

    data = request.get_json(silent=True)

    required_fields = [
        "requester_id", "blood_group", "units",
        "hospital", "location", "urgency", "required_date"
    ]

    if not data or any(field not in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        units = int(data["units"])

        if units <= 0:
            return jsonify({"error": "Units must be greater than zero"}), 400

    except (ValueError, TypeError):
        return jsonify({"error": "Units must be a valid number"}), 400

    connection = get_connection()

    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            INSERT INTO Blood_Requests
            (requester_id, blood_group, units, hospital,
             location, urgency, required_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data["requester_id"],
            data["blood_group"],
            units,
            data["hospital"],
            data["location"],
            data["urgency"],
            data["required_date"]
        )

        cursor.execute(query, values)
        connection.commit()

        return jsonify({
            "message": "Blood request created successfully",
            "request_id": cursor.lastrowid
        }), 201

    except Exception as error:
        connection.rollback()
        print("Request creation error:", error)
        return jsonify({"error": "Unable to create blood request"}), 500

    finally:
        if cursor:
            cursor.close()
        connection.close()


# ==========================================
# FETCH ALL BLOOD REQUESTS
# ==========================================

@app.route("/requests", methods=["GET"])
def get_requests():

    connection = get_connection()

    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                br.request_id,
                br.requester_id,
                u.name AS recipient,
                br.blood_group,
                br.units,
                br.hospital,
                br.location,
                br.urgency,
                br.required_date,
                br.status
            FROM Blood_Requests br
            JOIN Users u ON br.requester_id = u.user_id
            ORDER BY br.request_id DESC
        """

        cursor.execute(query)
        results = cursor.fetchall()

        return app.response_class(
            response=json.dumps(results, default=str),
            mimetype="application/json"
        )

    except Exception as error:
        print("Fetch requests error:", error)
        return jsonify({"error": "Unable to fetch requests"}), 500

    finally:
        if cursor:
            cursor.close()
        connection.close()


# ==========================================
# FETCH REGISTERED DONORS
# ==========================================

@app.route("/donors", methods=["GET"])
def get_donors():

    connection = get_connection()

    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                d.donor_id,
                d.user_id,
                u.name AS donor_name,
                d.blood_group,
                d.location,
                d.availability
            FROM Donors d
            JOIN Users u ON d.user_id = u.user_id
        """

        cursor.execute(query)
        results = cursor.fetchall()

        return app.response_class(
            response=json.dumps(results, default=str),
            mimetype="application/json"
        )

    except Exception as error:
        print("Fetch donors error:", error)
        return jsonify({"error": "Unable to fetch donors"}), 500

    finally:
        if cursor:
            cursor.close()
        connection.close()


# ==========================================
# DONOR ACCEPT OR DECLINE
# ==========================================

@app.route("/responses", methods=["POST"])
def respond_to_request():

    data = request.get_json(silent=True)

    required_fields = ["request_id", "donor_id", "response_status"]

    if not data or any(field not in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    request_id = data["request_id"]
    donor_id = data["donor_id"]
    response_status = str(data["response_status"]).lower()

    if response_status not in ["accepted", "declined"]:
        return jsonify({
            "error": "Response must be accepted or declined"
        }), 400

    connection = get_connection()

    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT units, status
            FROM Blood_Requests
            WHERE request_id = %s
            FOR UPDATE
            """,
            (request_id,)
        )

        blood_request = cursor.fetchone()

        if not blood_request:
            return jsonify({"error": "Blood request not found"}), 404

        if blood_request["status"] in ["fulfilled", "cancelled"]:
            return jsonify({"error": "Request is closed"}), 400

        cursor.execute(
            """
            SELECT donor_id, availability
            FROM Donors
            WHERE donor_id = %s
            """,
            (donor_id,)
        )

        donor = cursor.fetchone()

        if not donor:
            return jsonify({"error": "Donor not found"}), 404

        if not donor["availability"]:
            return jsonify({"error": "Donor is not available"}), 400

        cursor.execute(
            """
            SELECT response_id
            FROM Request_Responses
            WHERE request_id = %s AND donor_id = %s
            """,
            (request_id, donor_id)
        )

        existing = cursor.fetchone()

        if existing:

            cursor.execute(
                """
                UPDATE Request_Responses
                SET response_status = %s,
                    response_date = CURRENT_TIMESTAMP
                WHERE response_id = %s
                """,
                (response_status, existing["response_id"])
            )

        else:

            cursor.execute(
                """
                INSERT INTO Request_Responses
                (request_id, donor_id, response_status)
                VALUES (%s, %s, %s)
                """,
                (request_id, donor_id, response_status)
            )

        cursor.execute(
            """
            SELECT COUNT(*) AS accepted_count
            FROM Request_Responses
            WHERE request_id = %s
            AND response_status = 'accepted'
            """,
            (request_id,)
        )

        accepted_count = cursor.fetchone()["accepted_count"]

        if accepted_count >= blood_request["units"]:
            new_status = "fulfilled"
        else:
            new_status = "open"

        cursor.execute(
            """
            UPDATE Blood_Requests
            SET status = %s
            WHERE request_id = %s
            """,
            (new_status, request_id)
        )

        connection.commit()

        return jsonify({
            "message": "Donor response recorded successfully",
            "request_id": request_id,
            "donor_id": donor_id,
            "response_status": response_status,
            "accepted_donors": accepted_count,
            "required_units": blood_request["units"],
            "request_status": new_status
        }), 200

    except Exception as error:
        connection.rollback()
        print("Donor response error:", error)
        return jsonify({"error": "Unable to record donor response"}), 500

    finally:
        if cursor:
            cursor.close()
        connection.close()


# ==========================================
# FETCH DONOR RESPONSES
# ==========================================

@app.route("/requests/<int:request_id>/responses", methods=["GET"])
def get_responses(request_id):

    connection = get_connection()

    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                rr.response_id,
                rr.request_id,
                rr.donor_id,
                u.name AS donor_name,
                d.blood_group,
                rr.response_status,
                rr.response_date
            FROM Request_Responses rr
            JOIN Donors d ON rr.donor_id = d.donor_id
            JOIN Users u ON d.user_id = u.user_id
            WHERE rr.request_id = %s
        """

        cursor.execute(query, (request_id,))
        results = cursor.fetchall()

        return app.response_class(
            response=json.dumps(results, default=str),
            mimetype="application/json"
        )

    except Exception as error:
        print("Fetch responses error:", error)
        return jsonify({"error": "Unable to fetch responses"}), 500

    finally:
        if cursor:
            cursor.close()
        connection.close()


# ==========================================
# REQUEST STATUS TRACKING
# ==========================================

@app.route("/requests/<int:request_id>/status", methods=["GET"])
def get_request_status(request_id):

    connection = get_connection()

    if not connection:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                br.request_id,
                br.blood_group,
                br.units,
                br.status AS request_status,
                COUNT(rr.response_id) AS total_responses,
                COALESCE(SUM(
                    rr.response_status = 'accepted'
                ), 0) AS accepted_donors,
                COALESCE(SUM(
                    rr.response_status = 'declined'
                ), 0) AS declined_donors
            FROM Blood_Requests br
            LEFT JOIN Request_Responses rr
                ON br.request_id = rr.request_id
            WHERE br.request_id = %s
            GROUP BY
                br.request_id,
                br.blood_group,
                br.units,
                br.status
        """

        cursor.execute(query, (request_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"error": "Blood request not found"}), 404

        return jsonify(result)

    except Exception as error:
        print("Request status error:", error)
        return jsonify({"error": "Unable to fetch request status"}), 500

    finally:
        if cursor:
            cursor.close()
        connection.close()


# ==========================================
# RUN FLASK APPLICATION
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
