from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import mysql.connector
import smtplib
from email.mime.text import MIMEText
import os
import datetime
import logging
import requests
from dotenv import load_dotenv
from io import BytesIO
import openpyxl

# ---------------- LOAD ENV ----------------
load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "gosafe_db")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "info@gosafedriving.com")

RECAPTCHA_SECRET = os.getenv("RECAPTCHA_SECRET")

# ---------------- APP CONFIG ----------------
app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

# ---------------- CREATE DATABASE ----------------
def create_database():
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            port=MYSQL_PORT
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE}")
        logging.info(f"Database '{MYSQL_DATABASE}' ready")
        cursor.close()
        conn.close()
    except Exception as e:
        logging.error(f"Database error: {e}")

# ---------------- DB CONNECTION ----------------
def get_db():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        port=MYSQL_PORT
    )

# ---------------- CREATE TABLE ----------------
def create_table():
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100),
            email VARCHAR(100),
            phone VARCHAR(20),
            age INT,
            gender VARCHAR(20),
            permit_status VARCHAR(20),
            license_status VARCHAR(20),
            experience_level VARCHAR(50),
            class_type VARCHAR(150),
            preferred_date DATE,
            preferred_time TIME,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        cursor.close()
        conn.close()

        logging.info("Table 'bookings' ready")

    except Exception as e:
        logging.error(f"Table error: {e}")

# Run DB setup
create_database()
create_table()

# ---------------- EMAIL FUNCTION ----------------
def send_email(data):
    if not EMAIL_USER or not EMAIL_PASSWORD:
        logging.warning("Email not configured")
        return

    try:
        msg = MIMEText(f"""
New Booking Received

Name: {data.get('full_name')}
Email: {data.get('email')}
Phone: {data.get('phone')}
Class: {data.get('class_type')}
Date: {data.get('preferred_date')}
Time: {data.get('preferred_time')}
""")

        msg["Subject"] = "New Driving Class Booking"
        msg["From"] = EMAIL_USER
        msg["To"] = RECEIVER_EMAIL

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        logging.info("Email sent")

    except Exception as e:
        logging.error(f"Email error: {e}")

# ---------------- CAPTCHA ----------------
def verify_captcha(token):
    if not RECAPTCHA_SECRET:
        return True

    try:
        response = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data={"secret": RECAPTCHA_SECRET, "response": token}
        )
        return response.json().get("success", False)
    except:
        return False

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/pricing")
def pricing():
    return render_template("pricing.html")

@app.route("/contact")
def contact_page():
    return render_template("contact.html")

@app.route("/health")
def health():
    return {"status": "running"}

# ---------------- SUBMIT BOOKING ----------------
@app.route("/submit-booking", methods=["POST"])
def submit_booking():

    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"message": "Invalid data"}), 400

        logging.info(f"Received data: {data}")

        # Validation
        for field in ["full_name", "email", "phone"]:
            if not data.get(field):
                return jsonify({"message": f"{field} required"}), 400

        # Captcha
        if not verify_captcha(data.get("captcha")):
            return jsonify({"message": "Captcha failed"}), 400

        try:
            preferred_date = datetime.datetime.strptime(
                data.get("preferred_date"), "%Y-%m-%d"
            ).date() if data.get("preferred_date") else None

            preferred_time = datetime.datetime.strptime(
                data.get("preferred_time"), "%H:%M"
            ).time() if data.get("preferred_time") else None

        except Exception as e:
            logging.error(f"Date/Time error: {e}")
            return jsonify({"message": "Invalid date/time format"}), 400

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO bookings
        (full_name,email,phone,age,gender,permit_status,license_status,
        experience_level,class_type,preferred_date,preferred_time,message)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            data.get("full_name"),
            data.get("email"),
            data.get("phone"),
            data.get("age"),
            data.get("gender"),
            data.get("permit_status"),
            data.get("license_status"),
            data.get("experience_level"),
            data.get("class_type"),
            preferred_date,
            preferred_time,
            data.get("message")
        ))

        conn.commit()
        cursor.close()
        conn.close()

        try:
            send_email(data)
        except:
            pass

        return jsonify({"message": "Success"})

    except Exception as e:
        logging.error(f"Submit error: {e}")
        return jsonify({"message": str(e)}), 500

# ---------------- EXPORT ----------------
@app.route("/export")
def export():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM bookings")
        data = cursor.fetchall()

        wb = openpyxl.Workbook()
        sheet = wb.active

        if data:
            sheet.append(list(data[0].keys()))
            for row in data:
                sheet.append(list(row.values()))

        output = BytesIO()
        wb.save(output)
        output.seek(0)

        cursor.close()
        conn.close()

        return send_file(output, download_name="bookings.xlsx", as_attachment=True)

    except Exception as e:
        logging.error(f"Export error: {e}")
        return "Error"

# ---------------- RUN ----------------
if __name__ == "__main__":
    from waitress import serve
    port = int(os.getenv("PORT", 5000))
    logging.info(f"Server running on port {port}")
    serve(app, host="0.0.0.0", port=port)