from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymysql
import bcrypt
import cv2
import numpy as np
import pytesseract
import base64
import io
from PIL import Image
import subprocess
import pandas as pd
import re
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database Connection Function
def get_db_connection():
    return pymysql.connect(host="localhost", user="root", password="", database="number_plate")

# Home Route
@app.route('/')
def home():
    if "user" in session:
        return render_template("index.html", user=session["user"])
    return redirect(url_for("login"))

# User Registration Route
@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        address = request.form['address']
        mobile_no = request.form['mobile_no']
        password = request.form['password']

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        db = get_db_connection()
        cursor = db.cursor()

        try:
            cursor.execute("INSERT INTO users (username, address, mobile_no, password) VALUES (%s, %s, %s, %s)",
                           (username, address, mobile_no, hashed_password))
            db.commit()
            return redirect(url_for("login"))
        except pymysql.IntegrityError:
            return "User already exists!"
        finally:
            cursor.close()
            db.close()
    
    return render_template("register.html")

# User Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[4].encode('utf-8')):
            session["user"] = username
            return redirect(url_for("home"))
        return "Invalid username or password!"

    return render_template("login.html")

# Vehicle Registration
@app.route('/register', methods=['POST'])
def register_vehicle():
    if "user" not in session:
        return jsonify({"status": "error", "message": "Please log in first"}), 403

    # Ensure request data is JSON
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid request format"}), 400

    # Extract and validate data
    name = data.get("name")
    address = data.get("address")
    vehicle_number = data.get("vehicle_number")
    amount = data.get("amount")

    if not all([name, address, vehicle_number]) or amount != 500:
        return jsonify({"status": "error", "message": "Invalid details or incorrect payment amount"}), 400

    # Establish Database Connection
    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("INSERT INTO vehicle_registration (name, address, vehicle_number, amount, status) VALUES (%s, %s, %s, %s, %s)",
                       (name, address, vehicle_number, amount, "Paid"))
        db.commit()
        return jsonify({"status": "success", "message": "Vehicle registered successfully!"})
    except pymysql.IntegrityError:
        return jsonify({"status": "error", "message": "Vehicle number already registered"}), 400
    finally:
        cursor.close()
        db.close()


# Logout
@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))




def get_detected_number_plate():
    """ Read and clean the last detected number plate from data.csv """
    try:
        df = pd.read_csv("data.csv", header=None, names=["timestamp", "number_plate"])  # Read with proper column names
        if df.empty:
            print("⚠ data.csv is empty!")
            return None

        # Get the last detected plate and remove unwanted characters
        detected_plate = df.iloc[-1]["number_plate"]
        detected_plate = re.sub(r"[^A-Za-z0-9]", "", detected_plate).upper().strip()  # Remove all special characters
        
        print(f"🔍 Detected Plate (After Formatting): '{detected_plate}'")  # Debugging
        return detected_plate
    except Exception as e:
        print("❌ Error reading data.csv:", e)
    return None




def check_plate_in_database(detected_plate):
    """Check if the detected plate exists in the database and apply correct deductions."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch vehicle details and check if it's a green plate
        query = "SELECT vehicle_number, amount FROM vehicle_registration WHERE vehicle_number = %s"
        cursor.execute(query, (detected_plate,))
        vehicle = cursor.fetchone()

        if vehicle:
            vehicle_number, amount = vehicle

            # Get current time
            current_hour = datetime.now().hour

            # Check if the number plate is green
            is_green_plate = (vehicle_number == "KA02KJ9088")  # Replace with your green plate logic

            if is_green_plate:
                # Special green plate deduction logic
                deduction_amount = 100 if 17 <= current_hour < 19 else 95
            else:
                # Normal deduction logic
                deduction_amount = 105 if 17 <= current_hour < 19 else 100

            new_amount = max(0, amount - deduction_amount)  # Ensuring balance does not go negative

            # Update balance in database
            update_query = "UPDATE vehicle_registration SET amount = %s WHERE vehicle_number = %s"
            cursor.execute(update_query, (new_amount, detected_plate))
            conn.commit()

            print(f"✅ ₹{deduction_amount} Deducted from {detected_plate}. New Balance: ₹{new_amount}")
            return True  # Plate matched and amount updated

        print(f"🚫 Plate {detected_plate} Not Found in Database.")
        return False  # Plate not found

    except Exception as e:
        print("❌ Database error:", e)
        return False
    finally:
        conn.close()



@app.route('/detect', methods=['GET'])
def detect_number_plate():
    try:
        # Step 1: Run test.py to detect the number plate
        subprocess.run(["python", "test1.py"], capture_output=True, text=True)

        # Step 2: Read the last detected plate from data.csv
        detected_plate = get_detected_number_plate()
        if not detected_plate:
            return jsonify({"error": "No plate detected"})

        # Step 3: Check if the detected plate is in the database and deduct ₹100 if found
        is_registered = check_plate_in_database(detected_plate)

        if is_registered:
            return jsonify({"message": "Matching - ₹100 Deducted", "plate": detected_plate})
        else:
            return jsonify({"message": "Not Matching", "plate": detected_plate})

    except Exception as e:
        return jsonify({"error": str(e)})
    

@app.route('/check_balance', methods=['GET', 'POST'])
def check_balance():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get("username")
        vehicle_number = data.get("vehicle_number")

        if not username or not vehicle_number:
            return jsonify({"error": "Missing details"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            query = "SELECT name, vehicle_number, amount FROM vehicle_registration WHERE vehicle_number = %s"
            cursor.execute(query, (vehicle_number,))
            result = cursor.fetchone()
            
            if result:
                return jsonify({
                    "name": result[0],
                    "vehicle_number": result[1],
                    "balance": result[2]
                })
            else:
                return jsonify({"error": "Vehicle not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            conn.close()

    return render_template("balance.html")  # Show the balance check form

@app.route('/detect_vehicle', methods=['POST'])
def detect_vehicle():
    try:
        script_path = r"D:\Number_plate_detection\main12.py"  # Use the correct full path

        # Run the script in a separate process
        process = subprocess.Popen(["python", script_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Capture output
        stdout, stderr = process.communicate()

        # Print logs for debugging
        print("STDOUT:", stdout.decode('utf-8'))
        print("STDERR:", stderr.decode('utf-8'))

        return jsonify({
            "status": "success" if not stderr else "error",
            "output": stdout.decode('utf-8'),
            "error": stderr.decode('utf-8')
        })

    except Exception as e:
        print("Exception:", str(e))
        return jsonify({"status": "error", "message": str(e)})




if __name__ == '__main__':
    app.run(debug=True)
