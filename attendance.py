import mysql.connector
from datetime import datetime

class Attendance:

    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Panda@5252",  
            database="office_db"
        )
        self.cursor = self.conn.cursor()

    def mark_intime(self, name):
        date = datetime.now().date()
        intime = datetime.now().time()

        check = "SELECT * FROM attendance WHERE name=%s AND date=%s"
        self.cursor.execute(check, (name, date))

        if self.cursor.fetchone():
            print("⚠ Already marked today")
            return

        query = "INSERT INTO attendance (name, date, intime) VALUES (%s, %s, %s)"
        self.cursor.execute(query, (name, date, intime))
        self.conn.commit()

        print("✅ In-Time Marked")

    def mark_outtime(self, name):
        date = datetime.now().date()
        outtime = datetime.now().time()

        query = "UPDATE attendance SET outtime=%s WHERE name=%s AND date=%s"
        self.cursor.execute(query, (outtime, name, date))
        self.conn.commit()

        print("✅ Out-Time Marked")

        self.calculate_hours(name)

    def calculate_hours(self, name):
        date = datetime.now().date()

        query = "SELECT intime, outtime FROM attendance WHERE name=%s AND date=%s"
        self.cursor.execute(query, (name, date))
        result = self.cursor.fetchone()

        if result:
            intime, outtime = result

            if intime is None or outtime is None:
                print("⚠ In/Out time missing")
                return

            hours = (outtime - intime).total_seconds() / 3600

            update = "UPDATE attendance SET work_hours=%s WHERE name=%s AND date=%s"
            self.cursor.execute(update, (hours, name, date))
            self.conn.commit()

            print("⏱ Working Hours:", round(hours, 2))

        else:
            print("No record found")

    def add_work_report(self, name):
        date = datetime.now().date()

        task = input("Enter work done: ")
        status = input("Enter status (Completed/Pending): ")

        query = "UPDATE attendance SET task=%s, status=%s WHERE name=%s AND date=%s"
        self.cursor.execute(query, (task, status, name, date))
        self.conn.commit()

        print("✅ Work Report Added")

    def view_attendance(self):
        self.cursor.execute("SELECT * FROM attendance")
        data = self.cursor.fetchall()

        print("\n📊 ===== Attendance Records =====")

        for row in data:
            print(row)

obj = Attendance()

while True:
    print("\n===== Attendance + Work Report System =====")
    print("1. Mark In-Time")
    print("2. Mark Out-Time (EOD)")
    print("3. Add Work Report")
    print("4. View Attendance")
    print("5. Exit")

    try:
        choice = int(input("Enter choice: "))

        if choice == 1:
            name = input("Enter name: ")
            obj.mark_intime(name)

        elif choice == 2:
            name = input("Enter name: ")
            obj.mark_outtime(name)

        elif choice == 3:
            name = input("Enter name: ")
            obj.add_work_report(name)

        elif choice == 4:
            obj.view_attendance()

        elif choice == 5:
            print("Exiting...")
            break

        else:
            print("Invalid choice")

    except ValueError:
        print("⚠ Enter numbers only")