from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import mysql.connector
import openpyxl
import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# ---------------- MYSQL CONNECTION ----------------

db = None
cursor = None

try:
    db = mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST", "localhost"),
        user=os.environ.get("MYSQL_USER", "root"),
        password=os.environ.get("MYSQL_PASSWORD", "root"),
        database=os.environ.get("MYSQL_DATABASE", "gosafe_db"),
        port=int(os.environ.get("MYSQL_PORT", 3306))
    )

    cursor = db.cursor(dictionary=True)

    print("Connected to MySQL successfully")

except mysql.connector.Error as err:
    print("MySQL connection error:", err)


# ---------------- EMAIL FUNCTION ----------------

def send_email(data):

    sender_email = os.environ.get("EMAIL_USER")
    receiver_email = os.environ.get("RECEIVER_EMAIL")
    password = os.environ.get("EMAIL_PASSWORD")

    if not sender_email or not password or not receiver_email:
        print("Email credentials missing")
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

        print("Email sent successfully")

    except Exception as e:
        print("Email error:", e)


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


# ---------------- SUBMIT BOOKING ----------------

@app.route("/submit-booking", methods=["POST"])
def submit_booking():

    if cursor is None:
        return jsonify({"message": "Database not connected"})

    try:

        data = request.json

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
        print("Submit booking error:", e)
        return jsonify({"message": "Error"})


# ---------------- EXPORT BOOKINGS ----------------

@app.route("/export")
def export_excel():

    if cursor is None:
        return "Database not connected"

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

        file = "bookings.xlsx"
        workbook.save(file)

        return send_file(file, as_attachment=True)

    except Exception as e:
        print("Export error:", e)
        return "Error exporting bookings"


# ---------------- RUN SERVER ----------------

if __name__ == "__main__":

    from waitress import serve

    print("Server starting...")

    serve(app, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
