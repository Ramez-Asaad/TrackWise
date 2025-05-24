import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="2203",
        database="kbsystem"
    )

def create_user(username, email, password, userType):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password, userType) VALUES (%s, %s, %s, %s)",
            (username, email, password, userType)
        )
        conn.commit()
        cursor.close()
        conn.close()
        print("User created:", username, email, userType)  # Debug print
        return True, "Signup successful! Please log in."
    except Error as e:
        print("MySQL Error:", e)  # Debug print
        return False, str(e)

def get_user_by_email(email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except Error as e:
        return None

def check_user_credentials(email, password, userType):
    user = get_user_by_email(email)
    if user and user['password'] == password and user['userType'] == userType:
        return True, user
    return False, None

def user_exists(username, email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username=%s OR email=%s", (username, email))
        exists = cursor.fetchone() is not None
        cursor.close()
        conn.close()
        return exists
    except Error as e:
        return False 