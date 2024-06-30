from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import os

from functools import wraps





app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER_PHOTOS'] = 'uploads/photos'
app.config['UPLOAD_FOLDER_TRANSCRIPTS'] = 'uploads/transcripts'
app.config['MAX_CONTENT_PATH'] = 1024 * 1024  # 1MB max file size

db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    other_name = db.Column(db.String(100), nullable=False)
    faculty = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    photo = db.Column(db.String(200), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    father_name = db.Column(db.String(100), nullable=True)
    mother_name = db.Column(db.String(100), nullable=True)
    dob = db.Column(db.String(10), nullable=True)
    email = db.Column(db.String(100), nullable=True)

class TranscriptRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Text, nullable=False)
    student_level = db.Column(db.String(50), nullable=False)
    degree_program = db.Column(db.String(100), nullable=False)
    graduation_year = db.Column(db.String(4), nullable=False)
    additional_info = db.Column(db.Text, nullable=True)

class TranscriptUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), db.ForeignKey('student.username'), nullable=False, unique=True)
    admin_password = db.Column(db.String(200), nullable=False)  # Plain text
    transcript_file = db.Column(db.String(200), nullable=False)


def create_default_admin():
    """Create a default admin user if it doesn't already exist."""
    admin_username = "admin"
    admin_password = "admin"
    admin = Student.query.filter_by(username=admin_username).first()
    if not admin:
        hashed_password = generate_password_hash(admin_password, method='pbkdf2:sha256')
        new_admin = Student(
            surname="Admin",
            first_name="Admin",
            other_name="",
            faculty="Admin",
            phone_number="",
            username=admin_username,
            password=hashed_password,
            photo=None
        )
        db.session.add(new_admin)
        db.session.commit()

def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if role != "ANY" and session.get('user_role') != role:
                return redirect(url_for('unauthorized'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

@app.route('/unauthorized')
def unauthorized():
    return 'Unauthorized Access', 403

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        surname = request.form["surname"]
        first_name = request.form["first_name"]
        other_name = request.form["other_name"]
        faculty = request.form["faculty"]
        phone_number = request.form["phone_number"]
        username = request.form["username"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Handle photo upload
        photo = None
        if 'photo' in request.files and allowed_file(request.files['photo'].filename, {'png', 'jpg', 'jpeg', 'gif'}):
            file = request.files['photo']
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER_PHOTOS'], filename)
            file.save(filepath)
            photo = filepath

        existing_student = Student.query.filter_by(username=username).first()
        if existing_student:
            flash('Username already exists. Please choose a different username.')
            return redirect(url_for('sign_up'))

        new_student = Student(
            surname=surname,
            first_name=first_name,
            other_name=other_name,
            faculty=faculty,
            phone_number=phone_number,
            username=username,
            password=hashed_password,
            photo=photo
        )

        db.session.add(new_student)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template("sign-up.html")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        username = data["username"]
        password = data["password"]
        user_type = data["type"]

        if user_type == "staff":
            if username == "admin" and password == "admin":
                session['user_id'] = 0
                session['username'] = "admin"
                session['user_role'] = 'admin'
                return jsonify({'message': 'Login successful', 'role': 'admin'}), 200
            else:
                return jsonify({'message': 'Invalid credentials for admin'}), 401
        else:
            student = Student.query.filter_by(username=username).first()
            if student and check_password_hash(student.password, password):
                session['user_id'] = student.id
                session['username'] = student.username
                session['user_role'] = 'student'
                return jsonify({'message': 'Login successful', 'role': 'student'}), 200
            else:
                return jsonify({'message': 'Invalid credentials'}), 401

    return render_template("login.html")

@app.route('/index3')
@login_required(role='student')
def index3():
    user = Student.query.get(session['user_id'])
    return render_template('index3.html', user=user)

@app.route("/index")
@login_required(role='admin')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/edit_user', methods=['POST'])
@login_required(role='student')
def edit_user():
    user_id = session['user_id']
    user = Student.query.get(user_id)

    if user:
        user.surname = request.form['surname']
        user.first_name = request.form['first_name']
        user.other_name = request.form['other_name']
        user.faculty = request.form['faculty']
        user.phone_number = request.form['phone_number']
        user.username = request.form['username']
        db.session.commit()
        return jsonify(success=True)
    else:
        return jsonify(success=False)

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route("/submit_transcript_request", methods=["POST"])
def submit_transcript_request():
    student_name = request.form['studentName']
    student_id = request.form['studentID']
    email = request.form['email']
    phone = request.form['phone']
    address = request.form['address']
    student_level = request.form['studentLevel']
    degree_program = request.form['degreeProgram']
    graduation_year = request.form['graduationYear']
    additional_info = request.form['additionalInfo']

    new_request = TranscriptRequest(
        student_name=student_name,
        student_id=student_id,
        email=email,
        phone=phone,
        address=address,
        student_level=student_level,
        degree_program=degree_program,
        graduation_year=graduation_year,
        additional_info=additional_info
    )

    db.session.add(new_request)
    db.session.commit()

    flash('Your request has been submitted successfully!')
    return redirect(url_for('index3'))

@app.route('/upload_transcript', methods=['POST'])
@login_required(role='admin')
def upload_transcript():
    registration_number = request.form['registration_number']
    admin_password = request.form['admin_password']
    
    # Verify admin password
    if admin_password != "admin":
        flash('Invalid admin password')
        return redirect(url_for('index'))

    student = Student.query.filter_by(username=registration_number).first()
    if not student:
        flash('Student not found')
        return redirect(url_for('index'))

    if 'transcript_file' in request.files:
        file = request.files['transcript_file']
        if file and allowed_file(file.filename, {'pdf', 'doc', 'docx', 'xlsx'}):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER_TRANSCRIPTS'], filename)
            file.save(filepath)

            # Check if the student already has a transcript uploaded
            existing_upload = TranscriptUpload.query.filter_by(username=registration_number).first()
            if existing_upload:
                # Update existing upload
                existing_upload.transcript_file = filepath
                existing_upload.admin_password = admin_password
            else:
                # Create a new upload record
                new_upload = TranscriptUpload(
                    username=registration_number,
                    admin_password=admin_password,
                    transcript_file=filepath
                )
                db.session.add(new_upload)
            
            db.session.commit()

            flash('Transcript uploaded successfully')
            return redirect(url_for('index'))

    flash('No file uploaded or invalid file type')
    return redirect(url_for('index'))


@app.route('/download_transcript/<int:student_id>', methods=['GET'])
@login_required(role='admin')
def download_transcript(student_id):
    student = Student.query.get(student_id)
    transcript_upload = TranscriptUpload.query.filter_by(username=student.username).first()
    if not student or not transcript_upload or not transcript_upload.transcript_file:
        flash('Transcript not found')
        return redirect(url_for('index'))
    
    return send_file(transcript_upload.transcript_file, as_attachment=True)

@app.route('/student-details')
@login_required(role='student')
def student_details():
    user = Student.query.get(session['user_id'])
    return render_template('student-details.html', user=user)

@app.route('/handle_download_transcript', methods=['POST'])
@login_required(role='admin')
def handle_download_transcript():
    registration_number = request.form['registration_number']
    admin_password = request.form['admin_password']

    # Verify admin password
    if admin_password != "admin":
        flash('Invalid admin password')
        return redirect(url_for('index'))

    transcript_upload = TranscriptUpload.query.filter_by(username=registration_number, admin_password=admin_password).first()
    if not transcript_upload:
        flash('Transcript not found or invalid credentials')
        return redirect(url_for('index'))

    return send_file(transcript_upload.transcript_file, as_attachment=True)


# Other routes for the admin and student dashboards...



@app.route('/handle_download_transcript_student', methods=['POST'])
@login_required(role='student')
def handle_download_transcript_student():
    user_id = session['user_id']
    student = Student.query.get(user_id)
    if not student:
        flash('Student not found')
        return redirect(url_for('index3'))

    transcript_upload = TranscriptUpload.query.filter_by(username=student.username).first()
    if not transcript_upload or not transcript_upload.transcript_file:
        flash('Transcript not found')
        return redirect(url_for('index3'))

    return send_file(transcript_upload.transcript_file, as_attachment=True)



# ... other routes ...

@app.route("/index5")
def index5():
    return render_template('index5.html')

@app.route("/index4")
def index4():
    return render_template('index4.html')

@app.route("/all-student")
@login_required(role='admin')
def all_student():
    students = Student.query.all()
    return render_template('all-student.html', students=students)


@app.route("/transcript")
def transcript():
    return render_template('transcript.html')

@app.route("/admit-form")
def admit_form():
    return render_template('admit-form.html')

@app.route("/all-teacher")
def all_teacher():
    return render_template('all-teacher.html')

@app.route("/add-teacher")
def add_teacher():
    return render_template('add-teacher.html')

@app.route("/teacher-details")
def teacher_details():
    return render_template('teacher-details.html')

@app.route("/teacher-payment")
def teacher_payment():
    return render_template('teacher-payment.html')

@app.route("/all-parents")
def all_parents():
    return render_template('all-parents.html')

@app.route("/add-parents")
def add_parents():
    return render_template('add-parents.html')

@app.route("/parents-details")
def parents_details():
    return render_template('parents-details.html')

@app.route("/all-book")
def all_book():
    return render_template('all-book.html')

@app.route("/add-book")
def add_book():
    return render_template('add-book.html')

@app.route("/all-fees")
def all_fees():
    return render_template('all-fees.html')

@app.route("/add-expense")
def add_expense():
    return render_template('add-expense.html')

@app.route("/all-expense")
def all_expense():
    return render_template('all-expense.html')

@app.route("/add-class")
def add_class():
    return render_template('add-class.html')

@app.route("/all-class")
def all_class():
    return render_template('all-class.html')

@app.route("/all-subject")
def all_subject():
    return render_template('all-subject.html')

@app.route("/class-routine")
def class_routine():
    return render_template('class-routine.html')

@app.route("/student-attendence")
def student_attendence():
    return render_template('student-attendence.html')

@app.route("/exam-schedule")
def exam_schedule():
    return render_template('exam-schedule.html')

@app.route("/exam-grade")
def exam_grade():
    return render_template('exam-grade.html')

@app.route("/transport")
def transport():
    return render_template('transport.html')

@app.route("/hostel")
def hostel():
    return render_template('hostel.html')

@app.route("/notice-board")
def notice_board():
    return render_template('notice-board.html')



@app.route("/account-settings")
def account_settings():
    return render_template('account-settings.html')



@app.route("/messaging")
def messaging():
    return render_template('messaging.html')



if __name__ == "__main__":
   
    if not os.path.exists(app.config['UPLOAD_FOLDER_PHOTOS']):
        os.makedirs(app.config['UPLOAD_FOLDER_PHOTOS'])
    if not os.path.exists(app.config['UPLOAD_FOLDER_TRANSCRIPTS']):
        os.makedirs(app.config['UPLOAD_FOLDER_TRANSCRIPTS'])
    with app.app_context():
        db.create_all()
        create_default_admin()
    app.run(debug=True)
