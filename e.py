[1mdiff --git a/.gitignore b/.gitignore[m
[1mnew file mode 100644[m
[1mindex 0000000..e6ddc51[m
[1m--- /dev/null[m
[1m+++ b/.gitignore[m
[36m@@ -0,0 +1,10 @@[m
[32m+[m[32m__pycache__/[m
[32m+[m[32m*.pyc[m
[32m+[m[32m*.pyo[m
[32m+[m[32mvenv/[m
[32m+[m[32m.venv/[m
[32m+[m[32m.env[m
[32m+[m[32m.env.*[m
[32m+[m[32m.vscode/[m
[32m+[m[32m*.log[m
[32m+[m[32m*.sql[m
[1mdiff --git a/app.py b/app.py[m
[1mnew file mode 100644[m
[1mindex 0000000..e9af529[m
[1m--- /dev/null[m
[1m+++ b/app.py[m
[36m@@ -0,0 +1,644 @@[m
[32m+[m
[32m+[m[32mfrom flask import Flask, request, jsonify[m
[32m+[m[32mfrom flask_cors import CORS[m
[32m+[m[32mfrom database import get_connection[m
[32m+[m[32mfrom werkzeug.security import generate_password_hash, check_password_hash[m
[32m+[m[32mimport json[m
[32m+[m
[32m+[m[32mapp = Flask(__name__)[m
[32m+[m[32mCORS(app)[m
[32m+[m
[32m+[m
[32m+[m[32m# ==========================================[m
[32m+[m[32m# HOME[m
[32m+[m[32m# ==========================================[m
[32m+[m
[32m+[m[32m@app.route("/")[m
[32m+[m[32mdef home():[m
[32m+[m[32m    return "BloodLink Backend is Running!"[m
[32m+[m
[32m+[m
[32m+[m[32m# ==========================================[m
[32m+[m[32m# USER REGISTRATION[m
[32m+[m[32m# ==========================================[m
[32m+[m
[32m+[m[32m@app.route("/register", methods=["POST"])[m
[32m+[m[32mdef register():[m
[32m+[m
[32m+[m[32m    data = request.get_json(silent=True)[m
[32m+[m
[32m+[m[32m    required_fields = ["name", "email", "phone", "password", "role"][m
[32m+[m
[32m+[m[32m    if not data or any(not data.get(field) for field in required_fields):[m
[32m+[m[32m        return jsonify({"error": "All required fields are required"}), 400[m
[32m+[m
[32m+[m[32m    name = str(data["name"]).strip()[m
[32m+[m[32m    email = str(data["email"]).strip().lower()[m
[32m+[m[32m    phone = str(data["phone"]).strip()[m
[32m+[m[32m    password = data["password"][m
[32m+[m[32m    role = str(data["role"]).strip().lower()[m
[32m+[m
[32m+[m[32m    if not name or not email or not phone:[m
[32m+[m[32m        return jsonify({"error": "Name, email and phone cannot be empty"}), 400[m
[32m+[m
[32m+[m[32m    if not isinstance(password, str) or len(password) < 8:[m
[32m+[m[32m        return jsonify({"error": "Password must contain at least 8 characters"}), 400[m
[32m+[m
[32m+[m[32m    if role not in ["donor", "recipient", "both"]:[m
[32m+[m[32m        return jsonify({"error": "Invalid role"}), 400[m
[32m+[m
[32m+[m[32m    blood_group = data.get("blood_group")[m
[32m+[m[32m    location = data.get("location")[m
[32m+[m
[32m+[m[32m    if role in ["donor", "both"]:[m
[32m+[m
[32m+[m[32m        if not blood_group or not location or not str(location).strip():[m
[32m+[m[32m            return jsonify({[m
[32m+[m[32m                "error": "Blood group and location are required for donors"[m
[32m+[m[32m            }), 400[m
[32m+[m
[32m+[m[32m        if blood_group not in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:[m
[32m+[m[32m            return jsonify({"error": "Invalid blood group"}), 400[m
[32m+[m
[32m+[m[32m    password_hash = generate_password_hash(password)[m
[32m+[m
[32m+[m[32m    connection = get_connection()[m
[32m+[m
[32m+[m[32m    if not connection:[m
[32m+[m[32m        return jsonify({"error": "Database connection failed"}), 500[m
[32m+[m
[32m+[m[32m    cursor = None[m
[32m+[m
[32m+[m[32m    try:[m
[32m+[m[32m        cursor = connection.cursor()[m
[32m+[m
[32m+[m[32m        cursor.execute([m
[32m+[m[32m            """[m
[32m+[m[32m            INSERT INTO Users[m
[32m+[m[32m            (name, email, phone, password_hash, role)[m
[32m+[m[32m            VALUES (%s, %s, %s, %s, %s)[m
[32m+[m[32m            """,[m
[32m+[m[32m            (name, email, phone, password_hash, role)[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        user_id = cursor.lastrowid[m
[32m+[m
[32m+[m[32m        if role in ["donor", "both"]:[m
[32m+[m
[32m+[m[32m            cursor.execute([m
[32m+[m[32m                """[m
[32m+[m[32m                INSERT INTO Donors[m
[32m+[m[32m                (user_id, blood_group, location)[m
[32m+[m[32m                VALUES (%s, %s, %s)[m
[32m+[m[32m                """,[m
[32m+[m[32m                (user_id, blood_group, str(location).strip())[m
[32m+[m[32m            )[m
[32m+[m
[32m+[m[32m        connection.commit()[m
[32m+[m
[32m+[m[32m        return jsonify({[m
[32m+[m[32m            "message": "Registration successful",[m
[32m+[m[32m            "user_id": user_id,[m
[32m+[m[32m            "name": name,[m
[32m+[m[32m            "email": email,[m
[32m+[m[32m            "role": role[m
[32m+[m[32m        }), 201[m
[32m+[m
[32m+[m[32m    except Exception as error:[m
[32m+[m
[32m+[m[32m        connection.rollback()[m
[32m+[m
[32m+[m[32m        if getattr(error, "errno", None) == 1062:[m
[32m+[m[32m            return jsonify({[m
[32m+[m[32m                "error": "Email or phone number already registered"[m
[32m+[m[32m            }), 409[m
[32m+[m
[32m+[m[32m        print("Registration error:", error)[m
[32m+[m[32m        return jsonify({"error": "Registration failed"}), 500[m
[32m+[m
[32m+[m[32m    finally:[m
[32m+[m[32m        if cursor:[m
[32m+[m[32m            cursor.close()[m
[32m+[m[32m        connection.close()[m
[32m+[m
[32m+[m
[32m+[m[32m# ==========================================[m
[32m+[m[32m# USER LOGIN[m
[32m+[m[32m# ==========================================[m
[32m+[m
[32m+[m[32m@app.route("/login", methods=["POST"])[m
[32m+[m[32mdef login():[m
[32m+[m
[32m+[m[32m    data = request.get_json(silent=True)[m
[32m+[m
[32m+[m[32m    if not data or not data.get("email") or not data.get("password"):[m
[32m+[m[32m        return jsonify({[m
[32m+[m[32m            "error": "Email and password are required"[m
[32m+[m[32m        }), 400[m
[32m+[m
[32m+[m[32m    email = str(data["email"]).strip().lower()[m
[32m+[m[32m    password = data["password"][m
[32m+[m
[32m+[m[32m    connection = get_connection()[m
[32m+[m
[32m+[m[32m    if not connection:[m
[32m+[m[32m        return jsonify({"error": "Database connection failed"}), 500[m
[32m+[m
[32m+[m[32m    cursor = None[m
[32m+[m
[32m+[m[32m    try:[m
[32m+[m[32m        cursor = connection.cursor(dictionary=True)[m
[32m+[m
[32m+[m[32m        cursor.execute([m
[32m+[m[32m            """[m
[32m+[m[32m            SELECT user_id, name, email, phone, password_hash, role[m
[32m+[m[32m            FROM Users[m
[32m+[m[32m            WHERE email = %s[m
[32m+[m[32m            """,[m
[32m+[m[32m            (email,)[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        user = cursor.fetchone()[m
[32m+[m
[32m+[m[32m        if not user or not check_password_hash(user["password_hash"], password):[m
[32m+[m[32m            return jsonify({[m
[32m+[m[32m                "error": "Invalid email or password"[m
[32m+[m[32m            }), 401[m
[32m+[m
[32m+[m[32m        user_response = {[m
[32m+[m[32m            "user_id": user["user_id"],[m
[32m+[m[32m            "name": user["name"],[m
[32m+[m[32m            "email": user["email"],[m
[32m+[m[32m            "phone": user["phone"],[m
[32m+[m[32m            "role": user["role"][m
[32m+[m[32m        }[m
[32m+[m
[32m+[m[32m        if user["role"] in ["donor", "both"]:[m
[32m+[m
[32m+[m[32m            cursor.execute([m
[32m+[m[32m                """[m
[32m+[m[32m                SELECT donor_id, blood_group, location, availability[m
[32m+[m[32m                FROM Donors[m
[32m+[m[32m                WHERE user_id = %s[m
[32m+[m[32m                """,[m
[32m+[m[32m                (user["user_id"],)[m
[32m+[m[32m            )[m
[32m+[m
[32m+[m[32m            donor = cursor.fetchone()[m
[32m+[m
[32m+[m[32m            if donor:[m
[32m+[m[32m                user_response["donor"] = donor[m
[32m+[m
[32m+[m[32m        return jsonify({[m
[32m+[m[32m            "message": "Login successful",[m
[32m+[m[32m            "user": user_response[m
[32m+[m[32m        }), 200[m
[32m+[m
[32m+[m[32m    except Exception as error:[m
[32m+[m
[32m+[m[32m        print("Login error:", error)[m
[32m+[m[32m        return jsonify({"error": "Login failed"}), 500[m
[32m+[m
[32m+[m[32m    finally:[m
[32m+[m[32m        if cursor:[m
[32m+[m[32m            cursor.close()[m
[32m+[m[32m        connection.close()[m
[32m+[m
[32m+[m
[32m+[m[32m# ==========================================[m
[32m+[m[32m# CREATE BLOOD REQUEST[m
[32m+[m[32m# ==========================================[m
[32m+[m
[32m+[m[32m@app.route("/requests", methods=["POST"])[m
[32m+[m[32mdef create_request():[m
[32m+[m
[32m+[m[32m    data = request.get_json(silent=True)[m
[32m+[m
[32m+[m[32m    required_fields = [[m
[32m+[m[32m        "requester_id", "blood_group", "units",[m
[32m+[m[32m        "hospital", "location", "urgency", "required_date"[m
[32m+[m[32m    ][m
[32m+[m
[32m+[m[32m    if not data or any(field not in data for field in required_fields):[m
[32m+[m[32m        return jsonify({"error": "Missing required fields"}), 400[m
[32m+[m
[32m+[m[32m    try:[m
[32m+[m[32m        units = int(data["units"])[m
[32m+[m
[32m+[m[32m        if units <= 0:[m
[32m+[m[32m            return jsonify({"error": "Units must be greater than zero"}), 400[m
[32m+[m
[32m+[m[32m    except (ValueError, TypeError):[m
[32m+[m[32m        return jsonify({"error": "Units must be a valid number"}), 400[m
[32m+[m
[32m+[m[32m    connection = get_connection()[m
[32m+[m
[32m+[m[32m    if not connection:[m
[32m+[m[32m        return jsonify({"error": "Database connection failed"}), 500[m
[32m+[m
[32m+[m[32m    cursor = None[m
[32m+[m
[32m+[m[32m    try:[m
[32m+[m[32m        cursor = connection.cursor()[m
[32m+[m
[32m+[m[32m        query = """[m
[32m+[m[32m            INSERT INTO Blood_Requests[m
[32m+[m[32m            (requester_id, blood_group, units, hospital,[m
[32m+[m[32m             location, urgency, required_date)[m
[32m+[m[32m            VALUES (%s, %s, %s, %s, %s, %s, %s)[m
[32m+[m[32m        """[m
[32m+[m
[32m+[m[32m        values = ([m
[32m+[m[32m            data["requester_id"],[m
[32m+[m[32m            data["blood_group"],[m
[32m+[m[32m            units,[m
[32m+[m[32m            data["hospital"],[m
[32m+[m[32m            data["location"],[m
[32m+[m[32m            data["urgency"],[m
[32m+[m[32m            data["required_date"][m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        cursor.execute(query, values)[m
[32m+[m[32m        connection.commit()[m
[32m+[m
[32m+[m[32m        return jsonify({[m
[32m+[m[32m            "message": "Blood request created successfully",[m
[32m+[m[32m            "request_id": cursor.lastrowid[m
[32m+[m[32m        }), 201[m
[32m+[m
[32m+[m[32m    except Exception as error:[m
[32m+[m[32m        connection.rollback()[m
[32m+[m[32m        print("Request creation error:", error)[m
[32m+[m[32m        return jsonify({"error": "Unable to create blood request"}), 500[m
[32m+[m
[32m+[m[32m    finally:[m
[32m+[m[32m        if cursor:[m
[32m+[m[32m            cursor.close()[m
[32m+[m[32m        connection.close()[m
[32m+[m
[32m+[m
[32m+[m[32m# ==========================================[m
[32m+[m[32m# FETCH ALL BLOOD REQUESTS[m
[32m+[m[32m# ==========================================[m
[32m+[m
[32m+[m[32m@app.route("/requests", methods=["GET"])[m
[32m+[m[32mdef get_requests():[m
[32m+[m
[32m+[m[32m    connection = get_connection()[m
[32m+[m
[32m+[m[32m    if not connection:[m
[32m+[m[32m        return jsonify({"error": "Database connection failed"}), 500[m
[32m+[m
[32m+[m[32m    cursor = None[m
[32m+[m
[32m+[m[32m    try:[m
[32m+[m[32m        cursor = connection.cursor(dictionary=True)[m
[32m+[m
[32m+[m[32m        query = """[m
[32m+[m[32m            SELECT[m
[32m+[m[32m                br.request_id,[m
[32m+[m[32m                br.requester_id,[m
[32m+[m[32m                u.name AS recipient,[m
[32m+[m[32m                br.blood_group,[m
[32m+[m[32m                br.units,[m
[32m+[m[32m                br.hospital,[m
[32m+[m[32m                br.location,[m
[32m+[m[32m                br.urgency,[m
[32m+[m[32m                br.required_date,[m
[32m+[m[32m                br.status[m
[32m+[m[32m            FROM Blood_Requests br[m
[32m+[m[32m            JOIN Users u ON br.requester_id = u.user_id[m
[32m+[m[32m            ORDER BY br.request_id DESC[m
[32m+[m[32m        """[m
[32m+[m
[32m+[m[32m        cursor.execute(query)[m
[32m+[m[32m        results = cursor.fetchall()[m
[32m+[m
[32m+[m[32m        return app.response_class([m
[32m+[m[32m            response=json.dumps(results, default=str),[m
[32m+[m[32m            mimetype="application/json"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m    except Exception as error:[m
[32m+[m[32m        print("Fetch requests error:", error)[m
[32m+[m[32m        return jsonify({"error": "Unable to fetch requests"}), 500[m
[32m+[m
[32m+[m[32m    finally:[m
[32m+[m[32m        if cursor:[m
[32m+[m[32m            cursor.close()[m
[32m+[m[32m        connection.close()[m
[32m+[m
[32m+[m
[32m+[m[32m# ==========================================[m
[32m+[m[32m# FETCH REGISTERED DONORS[m
[32m+[m[32m# ==========================================[m
[32m+[m
[32m+[m[32m@app.route("/donors", methods=["GET"])[m
[32m+[m[32mdef get_donors():[m
[32m+[m
[32m+[m[32m    connection = get_connection()[m
[32m+[m
[32m+[m[32m    if not connection:[m
[32m+[m[32m        return jsonify({"error": "Database connection failed"}), 500[m
[32m+[m
[32m+[m[32m    cursor = None[m
[32m+[m
[32m+[m[32m    try:[m
[32m+[m[32m        cursor = connection.cursor(dictionary=True)[m
[32m+[m
[32m+[m[32m        query = """[m
[32m+[m[32m            SELECT[m
[32m+[m[32m                d.donor_id,[m
[32m+[m[32m                d.user_id,[m
[32m+[m[32m                u.name AS donor_name,[m
[32m+[m[32m                d.blood_group,[m
[32m+[m[32m                d.location,[m
[32m+[m[32m                d.availability[m
[32m+[m[32m            FROM Donors d[m
[32m+[m[32m            JOIN Users u ON d.user_id = u.user_id[m
[32m+[m[32m        """[m
[32m+[m
[32m+[m[32m        cursor.execute(query)[m
[32m+[m[32m        results = cursor.fetchall()[m
[32m+[m
[32m+[m[32m        return app.response_class([m
[32m+[m[32m            response=json.dumps(results, default=str),[m
[32m+[m[32m            mimetype="application/json"[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m    except Exception as error:[m
[32m+[m[32m        print("Fetch donors error:", error)[m
[32m+[m[32m        return jsonify({"error": "Unable to fetch donors"}), 500[m
[32m+[m
[32m+[m[32m    finally:[m
[32m+[m[32m        if cursor:[m
[32m+[m[32m            cursor.close()[m
[32m+[m[32m        connection.close()[m
[32m+[m
[32m+[m
[32m+[m[32m# ==========================================[m
[32m+[m[32m# DONOR ACCEPT OR DECLINE[m
[32m+[m[32m# ==========================================[m
[32m+[m
[32m+[m[32m@app.route("/responses", methods=["POST"])[m
[32m+[m[32mdef respond_to_request():[m
[32m+[m
[32m+[m[32m    data = request.get_json(silent=True)[m
[32m+[m
[32m+[m[32m    required_fields = ["request_id", "donor_id", "response_status"][m
[32m+[m
[32m+[m[32m    if not data or any(field not in data for field in required_fields):[m
[32m+[m[32m        return jsonify({"error": "Missing required fields"}), 400[m
[32m+[m
[32m+[m[32m    request_id = data["request_id"][m
[32m+[m[32m    donor_id = data["donor_id"][m
[32m+[m[32m    response_status = str(data["response_status"]).lower()[m
[32m+[m
[32m+[m[32m    if response_status not in ["accepted", "declined"]:[m
[32m+[m[32m        return jsonify({[m
[32m+[m[32m            "error": "Response must be accepted or declined"[m
[32m+[m[32m        }), 400[m
[32m+[m
[32m+[m[32m    connection = get_connection()[m
[32m+[m
[32m+[m[32m    if not connection:[m
[32m+[m[32m        return jsonify({"error": "Database connection failed"}), 500[m
[32m+[m
[32m+[m[32m    cursor = None[m
[32m+[m
[32m+[m[32m    try:[m
[32m+[m[32m        cursor = connection.cursor(dictionary=True)[m
[32m+[m
[32m+[m[32m        cursor.execute([m
[32m+[m[32m            """[m
[32m+[m[32m            SELECT units, status[m
[32m+[m[32m            FROM Blood_Requests[m
[32m+[m[32m            WHERE request_id = %s[m
[32m+[m[32m            FOR UPDATE[m
[32m+[m[32m            """,[m
[32m+[m[32m            (request_id,)[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        blood_request = cursor.fetchone()[m
[32m+[m
[32m+[m[32m        if not blood_request:[m
[32m+[m[32m            return jsonify({"error": "Blood request not found"}), 404[m
[32m+[m
[32m+[m[32m        if blood_request["status"] in ["fulfilled", "cancelled"]:[m
[32m+[m[32m            return jsonify({"error": "Request is closed"}), 400[m
[32m+[m
[32m+[m[32m        cursor.execute([m
[32m+[m[32m            """[m
[32m+[m[32m            SELECT donor_id, availability[m
[32m+[m[32m            FROM Donors[m
[32m+[m[32m            WHERE donor_id = %s[m
[32m+[m[32m            """,[m
[32m+[m[32m            (donor_id,)[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        donor = cursor.fetchone()[m
[32m+[m
[32m+[m[32m        if not donor:[m
[32m+[m[32m            return jsonify({"error": "Donor not found"}), 404[m
[32m+[m
[32m+[m[32m        if not donor["availability"]:[m
[32m+[m[32m            return jsonify({"error": "Donor is not available"}), 400[m
[32m+[m
[32m+[m[32m        cursor.execute([m
[32m+[m[32m            """[m
[32m+[m[32m            SELECT response_id[m
[32m+[m[32m            FROM Request_Responses[m
[32m+[m[32m            WHERE request_id = %s AND donor_id = %s[m
[32m+[m[32m            """,[m
[32m+[m[32m            (request_id, donor_id)[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m        existing = cursor.fetchone()[m
[32m+[m
[32m+[m[32m        if existing:[m
[32m+[m
[32m+[m[32m            cursor.execute([m
[32m+[m[32m                """[m
[32m+[m[32m                UPDATE Request_Responses[m
[32m+[m[32m                SET response_status = %s,[m
[32m+[m[32m                    response_date = CURRENT_TIMESTAMP[m
[32m+[m[32m                WHERE response_id = %s[m
[32m+[m[32m                """,[m
[32m+[m[32m                (response_status, existing["response_id"])[m
[32m+[m[32m            )[m
[32m+[m
[32m+[m[32m        else:[m
[32m+[m
[32m+[m[32m            cursor.execute([m
[32m+[m[32m                """[m
[32m+[m[32m                INSERT INTO Request_Responses[m
[32m+[m[32m                (request_id, donor_id, response_status)[m
[32m+[m[32m                VALUES (%s, %s, %s)[m
[32m+[m[32m                """,[m
[32m+[m[32m                (request_id, donor_id, response_status)[m
[32m+[m[32m            )[m
[32m+[m
[32m+[m[32m        cursor.execute([m
[32m+[m[32m            """[m
[32m+[m[32m            SELECT COUNT(*) AS accepted_count[m
[32m+[m[32m            FROM Request_Responses[m
[32m+[m[32m            WHERE request_id = %s[m
[32m+[m[32m            AND response_sta