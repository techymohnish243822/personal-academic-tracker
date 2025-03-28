from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database connection
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="student_management"
)
cursor = connection.cursor()

# Home Page
@app.route('/')
def index():
    cursor.execute("SELECT * FROM subjects")
    subjects = cursor.fetchall()
    return render_template('index.html', subjects=subjects)

# Add Subject
@app.route('/add_subject', methods=['POST'])
def add_subject():
    subject_name = request.form['subject_name']
    try:
        cursor.execute("INSERT INTO subjects (name) VALUES (%s)", (subject_name,))
        cursor.execute("INSERT INTO marks (subject_name) VALUES (%s)", (subject_name,))
        connection.commit()
        flash("Subject added successfully.", "success")
    except mysql.connector.Error as err:
        flash(f"Error adding subject: {err}", "error")
    return redirect(url_for('index'))

# Delete Subject
@app.route('/delete_subject/<subject_name>')
def delete_subject(subject_name):
    try:
        cursor.execute("DELETE FROM subjects WHERE name = %s", (subject_name,))
        connection.commit()
        flash("Subject deleted successfully.", "success")
    except mysql.connector.Error as err:
        flash(f"Error deleting subject: {err}", "error")
    return redirect(url_for('index'))

# Search Subjects
@app.route('/search_subject', methods=['POST'])
def search_subject():
    search_query = request.form['search_query']
    cursor.execute("SELECT * FROM subjects WHERE name LIKE %s", ('%' + search_query + '%',))
    subjects = cursor.fetchall()
    return render_template('index.html', subjects=subjects)

# Attendance Page (Join subjects with attendance)
@app.route('/attendance')
def attendance():
    try:
        # Join subjects with attendance to get subject names along with attendance status
        cursor.execute("""
            SELECT subjects.name, attendance.date, attendance.status 
            FROM subjects
            LEFT JOIN attendance ON subjects.name = attendance.subject_name
        """)
        attendance_records = cursor.fetchall()

        # Fetch subjects for the form dropdown
        cursor.execute("SELECT * FROM subjects")
        subjects = cursor.fetchall()

        return render_template('attendance.html', subjects=subjects, attendance_records=attendance_records)
    
    except mysql.connector.Error as err:
        print("Error fetching subjects:", err)
        flash(f"Error fetching data: {err}", "error")
        return redirect(url_for('index'))

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    subject_name = request.form['subject_name']
    date = request.form['date']
    status = request.form['status']

    try:
        cursor.execute(
            "INSERT INTO attendance (subject_name, date, status) VALUES (%s, %s, %s)",
            (subject_name, date, status)
        )
        connection.commit()
        flash("Attendance marked successfully.", "success")
    except mysql.connector.Error as err:
        flash(f"Error marking attendance: {err}", "error")
    return redirect(url_for('attendance'))

# Update Attendance
@app.route('/update_attendance', methods=['POST'])
def update_attendance():
    subject_name = request.form['subject_name']
    date = request.form['date']
    status = request.form['status']

    try:
        cursor.execute(
            "UPDATE attendance SET status = %s WHERE subject_name = %s AND date = %s",
            (status, subject_name, date)
        )
        connection.commit()
        flash("Attendance updated successfully.", "success")
    except mysql.connector.Error as err:
        flash(f"Error updating attendance: {err}", "error")
    return redirect(url_for('attendance'))


# Marks Page (Join subjects with marks)
@app.route('/marks')
def marks():
    try:
        # Join subjects with marks to get subject names along with their marks details
        cursor.execute("""
            SELECT subjects.name, 
                   COALESCE(marks.assignment_marks, 'No Marks') AS assignment_marks, 
                   COALESCE(marks.term1_marks, 'No Marks') AS term1_marks, 
                   COALESCE(marks.term2_marks, 'No Marks') AS term2_marks, 
                   COALESCE(marks.sem_end_marks, 'No Marks') AS sem_end_marks 
            FROM subjects
            LEFT JOIN marks ON subjects.name = marks.subject_name
        """)
        marks_records = cursor.fetchall()
        return render_template('marks.html', marks_records=marks_records)
    except mysql.connector.Error as err:
        flash(f"Error fetching marks data: {err}", "error")
        return redirect(url_for('index'))

@app.route('/update_marks', methods=['POST'])
def update_marks():
    subject_name = request.form['subject_name']
    assignment_marks = request.form['assignment_marks']
    term1_marks = request.form['term1_marks']
    term2_marks = request.form['term2_marks']
    sem_end_marks = request.form['sem_end_marks']

    try:
        cursor.execute(
            "UPDATE marks SET assignment_marks = %s, term1_marks = %s, term2_marks = %s, sem_end_marks = %s WHERE subject_name = %s",
            (assignment_marks, term1_marks, term2_marks, sem_end_marks, subject_name)
        )
        connection.commit()
        flash("Marks updated successfully.", "success")
    except mysql.connector.Error as err:
        flash(f"Error updating marks: {err}", "error")
    return redirect(url_for('marks'))

if __name__ == '__main__':
    app.run(debug=True)
