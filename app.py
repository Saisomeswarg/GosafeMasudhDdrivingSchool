from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import mysql.connector
import openpyxl
import smtplib
from email.mime.text import MIMEText
import os
import datetime
import logging
from dotenv import load_dotenv

# ---------------- LOAD ENV ----------------

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("info@gosafedriving.com")

# ---------------- APP CONFIG ----------------

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

# ---------------- MYSQL CONNECTION ----------------

db = None
cursor = None


def connect_db():
    global db, cursor

    try:
        db = mysql.connector.connect(
            host=os.environ.get("MYSQL_HOST", "localhost"),
            user=os.environ.get("MYSQL_USER", "root"),
            password=os.environ.get("MYSQL_PASSWORD", "root"),
            database=os.environ.get("MYSQL_DATABASE", "gosafe_db"),
            port=int(os.environ.get("MYSQL_PORT", 3306))
        )

        cursor = db.cursor(dictionary=True)

        logging.info("Connected to MySQL successfully")

    except mysql.connector.Error as err:
        logging.error(f"MySQL connection error: {err}")


connect_db()

# ---------------- EMAIL FUNCTION ----------------


def send_email(data):

    sender_email = os.environ.get("EMAIL_USER")
    receiver_email = os.environ.get("RECEIVER_EMAIL")
    password = os.environ.get("EMAIL_PASSWORD")

    if not sender_email or not password or not receiver_email:
        logging.warning("Email credentials missing")
        return

    subject = "New Driving Class Booking"

    body = f"""
New Booking Received

Name: {data.get('full_name')}
Email: {data.get('email')}
Phone: {data.get('phone')}
Age: {data.get('age')}
Gender: {data.get('gender')}
Class: {data.get('class_type')}
Date: {data.get('preferred_date')}
Time: {data.get('preferred_time')}

Message:
{data.get('message')}
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()

        server.login(sender_email, password)

        server.sendmail(sender_email, receiver_email, msg.as_string())

        server.quit()

        logging.info("Email sent successfully")

    except Exception as e:
        logging.error(f"Email error: {e}")


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


# ---------------- HEALTH CHECK ----------------


@app.route("/health")
def health():
    return {"status": "running"}


# ---------------- SUBMIT BOOKING ----------------


@app.route("/submit-booking", methods=["POST"])
def submit_booking():

    global db, cursor

    if cursor is None:
        return jsonify({"message": "Database not connected"}), 500

    if not db.is_connected():
        connect_db()

    try:

        data = request.get_json()

        if not data:
            return jsonify({"message": "Invalid data"}), 400

        sql = """
        INSERT INTO bookings
        (full_name,email,phone,age,gender,permit_status,license_status,
        experience_level,class_type,preferred_date,preferred_time,message)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            data.get("full_name"),
            data.get("email"),
            data.get("phone"),
            data.get("age"),
            data.get("gender"),
            data.get("permit_status"),
            data.get("license_status"),
            data.get("experience_level"),
            data.get("class_type"),
            data.get("preferred_date"),
            data.get("preferred_time"),
            data.get("message")
        )

        cursor.execute(sql, values)
        db.commit()

        send_email(data)

        return jsonify({"message": "Success"})

    except Exception as e:
        logging.error(f"Submit booking error: {e}")
        return jsonify({"message": "Error"}), 500


# ---------------- EXPORT BOOKINGS ----------------


@app.route("/export")
def export_excel():

    global db, cursor

    if cursor is None:
        return "Database not connected"

    if not db.is_connected():
        connect_db()

    try:

        cursor.execute("SELECT * FROM bookings")
        data = cursor.fetchall()

        workbook = openpyxl.Workbook()
        sheet = workbook.active

        if data:
            headers = data[0].keys()
            sheet.append(list(headers))

            for row in data:
                sheet.append(list(row.values()))

        filename = f"bookings_{datetime.datetime.now().timestamp()}.xlsx"

        workbook.save(filename)

        response = send_file(filename, as_attachment=True)

        @response.call_on_close
        def cleanup():
            try:
                os.remove(filename)
            except:
                pass

        return response

    except Exception as e:
        logging.error(f"Export error: {e}")
        return "Error exporting bookings"


# ---------------- RUN SERVER ----------------


if __name__ == "__main__":

    from waitress import serve

    port = int(os.environ.get("PORT", 5000))

    logging.info(f"Server starting on port {port}...")

    serve(app, host="0.0.0.0", port=port)