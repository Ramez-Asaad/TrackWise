from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from UI.DB import user_exists, create_user, check_user_credentials
from UI.KBSystem import run_kbsystem_for_student, load_courses_from_csv
from UI.course_db import get_all_courses

client_bp = Blueprint('client', __name__)

@client_bp.route('/')
def index():
    return render_template('index.html')

@client_bp.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('signupUsername').strip()
    email = request.form.get('signupEmail').strip()
    password = request.form.get('signupPassword')
    confirm_password = request.form.get('confirmPassword')
    user_type = request.form.get('role')

    # Validation
    if user_exists(username, email):
        flash("Username or email already exists", "error")
        return redirect(url_for('client.index'))
    if not email or '@' not in email or not email.split('@')[1]:
        flash("Email must contain @something", "error")
        return redirect(url_for('client.index'))
    if not password or not confirm_password or password != confirm_password:
        flash("Passwords must match", "error")
        return redirect(url_for('client.index'))
    import re
    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).{8,}$'
    if not re.match(password_regex, password):
        flash("Password must be at least 8 characters with uppercase, lowercase, and special characters", "error")
        return redirect(url_for('client.index'))
    if not user_type:
        flash("Please select a user type", "error")
        return redirect(url_for('client.index'))

    # Save user in DB
    success, msg = create_user(username, email, password, user_type)
    if success:
        flash(msg, "success")
    else:
        flash(f"Signup failed: {msg}", "error")
    return redirect(url_for('client.index'))

@client_bp.route('/login', methods=['POST'])
def login():
    email = request.form.get('signinEmail').strip()
    password = request.form.get('signinPassword')
    user_type = request.form.get('role')
    print("Login attempt:", email, password, user_type)  # Debug

    valid, user = check_user_credentials(email, password, user_type)
    print("Valid:", valid, "User:", user)  # Debug

    if valid:
        session['user_id'] = user['id']
        session['userType'] = user['userType']
        print('Logged in userType:', user['userType'])  # Debug print
        flash("Login success! Redirecting...", "success")
        if user['userType'] == 'Admin':
            print("Redirecting to admin dashboard")  # Debug
            return redirect(url_for('kbeditor.index'))
        else:
            print("Redirecting to student dashboard")  # Debug
            return redirect(url_for('client.student_dashboard'))
    else:
        print("Invalid credentials, redirecting to index")  # Debug
        flash("Invalid credentials", "error")
        return redirect(url_for('client.index'))

@client_bp.route('/admin_index')
def admin_index():
    return render_template('admin.index.html')

# Placeholder for student dashboard
@client_bp.route('/student_dashboard')
def student_dashboard():
    courses = get_all_courses()
    return render_template('student.html', courses=courses)

# Route to process student KBS form
@client_bp.route('/student_kbs', methods=['POST'])
def student_kbs():
    cgpa = float(request.form.get('cgpa', 0))
    current_credits = int(request.form.get('current_credits', 0))
    completed_courses = request.form.get('completed_courses', '')
    failed_courses = request.form.get('failed_courses', '')
    completed_courses = [c.strip() for c in completed_courses.split(',') if c.strip()]
    failed_courses = [c.strip() for c in failed_courses.split(',') if c.strip()]
    policy_feedback = run_kbsystem_for_student(cgpa, current_credits, completed_courses, failed_courses)
    return render_template('student.html', policy_feedback=policy_feedback)