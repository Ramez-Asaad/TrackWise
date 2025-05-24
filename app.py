from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Simulated user database
users = [{"email": "ro@gmail.com", "password": "1234", "userType": "admin"}]
existing_usernames = ["user1", "user2", "admin"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form.get('signupUsername').strip()
    email = request.form.get('signupEmail').strip()
    password = request.form.get('signupPassword')
    confirm_password = request.form.get('confirmPassword')
    user_type = request.form.get('role')

    # Validation
    if username in existing_usernames:
        flash("Username must be unique", "error")
        return redirect(url_for('index'))
    if not email or '@' not in email or not email.split('@')[1]:
        flash("Email must contain @something", "error")
        return redirect(url_for('index'))
    if not password or not confirm_password or password != confirm_password:
        flash("Passwords must match", "error")
        return redirect(url_for('index'))
    import re
    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).{8,}$'
    if not re.match(password_regex, password):
        flash("Password must be at least 8 characters with uppercase, lowercase, and special characters", "error")
        return redirect(url_for('index'))
    if not user_type:
        flash("Please select a user type", "error")
        return redirect(url_for('index'))

    # Save user (simulated)
    users.append({"email": email, "password": password, "userType": user_type, "username": username})
    existing_usernames.append(username)
    flash("Signup successful! Please log in.", "success")
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('signinEmail').strip()
    password = request.form.get('signinPassword')
    user_type = request.form.get('role')

    if (
        email == "ro@gmail.com" and
        password == "1234" and
        user_type == "admin"
    ):
        flash("Login success! Redirecting...", "success")
        return redirect(url_for('admin_index'))
    else:
        flash("Invalid credentials", "error")
        return redirect(url_for('index'))

@app.route('/admin_index')
def admin_index():
    return render_template('admin.index.html')

if __name__ == '__main__':
    app.run(debug=True)