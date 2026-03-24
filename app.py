from flask import Flask, render_template, request, redirect, send_file
import mysql.connector
from datetime import datetime
from openpyxl import Workbook

app = Flask(__name__)

try:
    conn = mysql.connector.connect(
        host="gondola.proxy.rlwy.net",
        user="root",
        password="pICnbTsJRSQzZwHfXuhCpcSwZOpsXTPj",
        database="railway",
        port=58689
    )
    print("DB Connected ✅")
except Exception as e:
    print("DB Error:", e)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/intime', methods=['POST'])
def intime():
    emp_id = request.form['emp_id']
    name = request.form['name']
    date = datetime.now().date()
    intime = datetime.now().time()

    cursor.execute(
        "INSERT INTO attendance (emp_id, name, date, intime, status) VALUES (%s,%s,%s,%s,%s)",
        (emp_id, name, date, intime, "P")
    )
    conn.commit()

    return redirect('/dashboard')
@app.route('/outtime', methods=['POST'])
def outtime():
    emp_id = request.form['emp_id']
    date = datetime.now().date()
    outtime = datetime.now().time()

    cursor.execute(
        "UPDATE attendance SET outtime=%s WHERE emp_id=%s AND date=%s",
        (outtime, emp_id, date)
    )
    conn.commit()

    cursor.execute(
        "SELECT intime, outtime FROM attendance WHERE emp_id=%s AND date=%s",
        (emp_id, date)
    )
    data = cursor.fetchone()

    if data and data[0] and data[1]:
        hours = (data[1] - data[0]).total_seconds() / 3600

        cursor.execute(
            "UPDATE attendance SET work_hours=%s WHERE emp_id=%s AND date=%s",
            (hours, emp_id, date)
        )
        conn.commit()

    return redirect('/dashboard')

@app.route('/work', methods=['POST'])
def work():
    emp_id = request.form['emp_id']
    task = request.form['task']
    status = request.form['status']
    date = datetime.now().date()

    cursor.execute(
        "UPDATE attendance SET task=%s, status=%s WHERE emp_id=%s AND date=%s",
        (task, status, emp_id, date)
    )
    conn.commit()

    return redirect('/dashboard')

@app.route('/view')
def view():
    cursor.execute("SELECT * FROM attendance")
    data = cursor.fetchall()
    return render_template("view.html", data=data)

@app.route('/monthly')
def monthly():
    cursor.execute("SELECT emp_id, date FROM attendance")
    data = cursor.fetchall()

    attendance = {}

    for name, date in data:
        day = date.day

        if name not in attendance:
            attendance[name] = ['A'] * 31

        attendance[name][day-1] = 'P'

    return render_template("monthly.html", data=attendance)

@app.route('/download_excel')
def download_excel():

    wb = Workbook()
    ws = wb.active

    headers = ["Name"] + [str(i) for i in range(1, 32)] + ["Total"]
    ws.append(headers)

    cursor.execute("SELECT name, date FROM attendance")
    data = cursor.fetchall()

    attendance = {}

    for name, date in data:
        day = date.day

        if name not in attendance:
            attendance[name] = ['A'] * 31

        attendance[name][day-1] = 'P'

    for name, days in attendance.items():
        total = days.count('P')
        ws.append([name] + days + [total])

    file_path = "monthly_attendance.xlsx"
    wb.save(file_path)

    return send_file(file_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
