from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'secret123'   # IMPORTANT for login session

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# MODEL
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    course = db.Column(db.String(100))


# CREATE DB
with app.app_context():
    db.create_all()


# LOGIN PAGE
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # simple login (you can upgrade later)
        if username == 'admin' and password == 'admin':
            session['user'] = username
            return redirect('/dashboard')

    return render_template('login.html')


# LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


# DASHBOARD
@app.route('/dashboard')
def dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 5

    students = Student.query.paginate(page=page, per_page=per_page)

    total_students = Student.query.count()
    courses = db.session.query(Student.course).distinct().count()

    # Chart data
    course_counts = {}
    all_students = Student.query.all()

    for s in all_students:
        course_counts[s.course] = course_counts.get(s.course, 0) + 1

    return render_template(
        'dashboard.html',
        students=students,
        total_students=total_students,
        courses=courses,
        course_counts=course_counts
    )

# ADD STUDENT
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']

        new_student = Student(name=name, email=email, course=course)
        db.session.add(new_student)
        db.session.commit()

        return redirect('/dashboard')

    return render_template('add_student.html')


# EDIT STUDENT
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if 'user' not in session:
        return redirect('/')

    student = Student.query.get(id)

    if request.method == 'POST':
        student.name = request.form['name']
        student.email = request.form['email']
        student.course = request.form['course']

        db.session.commit()
        return redirect('/dashboard')

    return render_template('edit_student.html', student=student)


# DELETE STUDENT
@app.route('/delete/<int:id>')
def delete_student(id):
    if 'user' not in session:
        return redirect('/')

    student = Student.query.get(id)
    db.session.delete(student)
    db.session.commit()

    return redirect('/dashboard')


# RUN
if __name__ == '__main__':
    app.run(debug=True)