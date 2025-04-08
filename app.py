from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import random

app = Flask(__name__)
DB_PATH = 'database/university.db'
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT UNIQUE,
                name TEXT NOT NULL,
                address TEXT NOT NULL
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rubric TEXT NOT NULL,
                number TEXT NOT NULL,
                name TEXT NOT NULL,
                credits INTEGER NOT NULL
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                semester TEXT NOT NULL,
                FOREIGN KEY(course_id) REFERENCES courses(id)
            );
        ''')
        conn.commit()

def generate_unique_student_id():
    while True:
        new_id = str(random.randint(10000000, 99999999))
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM students WHERE student_id = ?", (new_id,))
            if not cursor.fetchone():
                return new_id

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add-student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        student_id = generate_unique_student_id()
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO students (student_id, name, address) VALUES (?, ?, ?)',
                           (student_id, name, address))
            conn.commit()
        return redirect(url_for('index'))
    return render_template('add_student.html')

@app.route('/add-course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        rubric = request.form['rubric']
        number = request.form['number']
        name = request.form['name']
        credits = request.form['credits']
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO courses (rubric, number, name, credits) VALUES (?, ?, ?, ?)',
                           (rubric, number, name, credits))
            conn.commit()
        return redirect(url_for('index'))
    return render_template('add_course.html')

@app.route('/add-section', methods=['GET', 'POST'])
def add_section():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, rubric, number FROM courses')
        courses = cursor.fetchall()

    if request.method == 'POST':
        course_id = request.form['course_id']
        semester = request.form['semester']
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO sections (course_id, semester) VALUES (?, ?)', (course_id, semester))
            conn.commit()
        return redirect(url_for('index'))
    return render_template('add_section.html', courses=courses)

@app.route('/list-students')
def list_students():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM students')
        students = cursor.fetchall()
    return render_template('list_students.html', students=students)

@app.route('/list-courses')
def list_courses():
    rubric = request.args.get('rubric', '')
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if rubric:
            cursor.execute('SELECT * FROM courses WHERE rubric = ?', (rubric,))
        else:
            cursor.execute('SELECT * FROM courses')
        courses = cursor.fetchall()
    return render_template('list_courses.html', courses=courses, rubric=rubric or 'All')

@app.route('/list-sections')
def list_sections():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT sections.id, semester, courses.rubric, courses.number, courses.name
            FROM sections
            JOIN courses ON sections.course_id = courses.id
        ''')
        sections = cursor.fetchall()
    return render_template('list_sections.html', sections=sections)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
