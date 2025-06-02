import psycopg2
from psycopg2 import Error
from werkzeug.security import generate_password_hash, check_password_hash
from .config import DATABASE_URL, SSL_MODE

def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode=SSL_MODE)

def init_db():
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            userType VARCHAR(50) NOT NULL
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

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
        print("Database Error:", e)  # Debug print
        return False, str(e)

def get_user_by_email(email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, password, userType FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'password': user[3],
                'userType': user[4]
            }
        return None
    except Error as e:
        print("Database Error:", e)
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
        print("Database Error:", e)
        return False 