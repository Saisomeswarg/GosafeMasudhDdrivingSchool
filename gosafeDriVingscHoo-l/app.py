from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import mysql.connector
import openpyxl
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)
CORS(app)

# ---------------- MYSQL CONNECTION ----------------
try:
    db = mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST"),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
        database=os.environ.get("MYSQL_DATABASE"),
        port=int(os.environ.get("MYSQL_PORT", 3306))
    )
    cursor = db.cursor()
    print("Connected to MySQL successfully")
except mysql.connector.Error as err:
    print("MySQL connection error:", err)
    cursor = None

# ---------------- EMAIL FUNCTION ----------------
def send_email(data):
    sender_email = os.environ.get("EMAIL_USER")       # info@gosafedriving.com
    receiver_email = os.environ.get("EMAIL_RECEIVER") # info@gosafedriving.com
    password = os.environ.get("EMAIL_PASSWORD")       # Gmail App Password

    subject = "New Driving Class Booking"
    body = f"""
New Booking Received

Name: {data['full_name']}
Email: {data['email']}
Phone: {data['phone']}
Age: {data['age']}
Gender: {data['gender']}
Class: {data['class_type']}
Date: {data['preferred_date']}
Time: {data['preferred_time']}

Message:
{data['message']}
"""

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

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

@app.route("/admin")
def admin():
    try:
        cursor.execute("SELECT * FROM bookings")
        bookings = cursor.fetchall()
        return render_template("admin.html", bookings=bookings)
    except Exception as e:
        print("Admin panel error:", e)
        return "Error loading admin panel"

@app.route("/submit-booking", methods=["POST"])
def submit_booking():
    try:
        data = request.json
        sql = """
        INSERT INTO bookings 
        (full_name, email, phone, age, gender, permit_status, license_status,
        experience_level, class_type, preferred_date, preferred_time, message)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        values = (
            data["full_name"], data["email"], data["phone"], data["age"],
            data["gender"], data["permit_status"], data["license_status"],
            data["experience_level"], data["class_type"],
            data["preferred_date"], data["preferred_time"], data["message"]
        )
        cursor.execute(sql, values)
        db.commit()

        send_email(data)
        return jsonify({"message": "Success"})
    except Exception as e:
        print("Submit booking error:", e)
        return jsonify({"message": "Error"})

@app.route("/delete/<int:booking_id>")
def delete_booking(booking_id):
    try:
        cursor.execute("DELETE FROM bookings WHERE id=%s", (booking_id,))
        db.commit()
        return jsonify({"message": "Deleted"})
    except Exception as e:
        print("Delete booking error:", e)
        return jsonify({"message": "Error"})

@app.route("/update/<int:booking_id>", methods=["POST"])
def update_booking(booking_id):
    try:
        data = request.json
        sql = """
        UPDATE bookings SET 
        full_name=%s,email=%s,phone=%s,age=%s,gender=%s,
        permit_status=%s,license_status=%s,experience_level=%s,
        class_type=%s,preferred_date=%s,preferred_time=%s,message=%s
        WHERE id=%s
        """
        values = (
            data["full_name"], data["email"], data["phone"], data["age"],
            data["gender"], data["permit_status"], data["license_status"],
            data["experience_level"], data["class_type"],
            data["preferred_date"], data["preferred_time"], data["message"],
            booking_id
        )
        cursor.execute(sql, values)
        db.commit()
        return jsonify({"message": "Updated"})
    except Exception as e:
        print("Update booking error:", e)
        return jsonify({"message": "Error"})

@app.route("/export")
def export_excel():
    try:
        cursor.execute("SELECT * FROM bookings")
        data = cursor.fetchall()
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        headers = [i[0] for i in cursor.description]
        sheet.append(headers)
        for row in data:
            sheet.append(row)
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