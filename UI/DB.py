import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from werkzeug.security import generate_password_hash, check_password_hash
import time

# MongoDB connection with retry logic
def get_db_client():
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            # MongoDB Atlas URI
            uri = "mongodb+srv://ramez:ramez@cluster0.jkciz4n.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
            
            # Create a new client and connect to the server with ServerApi configuration
            client = MongoClient(uri, server_api=ServerApi('1'))
            
            # Test the connection
            client.admin.command('ping')
            print("Successfully connected to MongoDB Atlas!")
            return client
            
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"MongoDB connection attempt {attempt + 1} failed. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to connect to MongoDB: {str(e)}")
                print("Falling back to in-memory storage")
                if not hasattr(get_db_client, '_mock_db'):
                    get_db_client._mock_db = {
                        'users': {}
                    }
                return None

# Initialize client
client = get_db_client()
if client:
    # Use the trackwise database
    db = client['trackwise']
else:
    db = None

def init_db():
    """Initialize the database with required collections"""
    if client:
        try:
            # Create unique indexes if using MongoDB
            db.users.create_index('username', unique=True)
            db.users.create_index('email', unique=True)
        except Exception as e:
            print(f"Error creating indexes: {e}")

def create_user(username, email, password, userType):
    try:
        user_data = {
            'username': username,
            'email': email,
            'password': password,
            'userType': userType
        }
        
        if client:
            # MongoDB storage
            result = db.users.insert_one(user_data)
        else:
            # In-memory storage
            if username in get_db_client._mock_db['users'] or email in [u['email'] for u in get_db_client._mock_db['users'].values()]:
                raise Exception("Username or email already exists")
            user_id = str(len(get_db_client._mock_db['users']) + 1)
            get_db_client._mock_db['users'][user_id] = user_data
            
        print("User created:", username, email, userType)
        return True, "Signup successful! Please log in."
    except Exception as e:
        print("Database Error:", e)
        return False, str(e)

def get_user_by_email(email):
    try:
        if client:
            # MongoDB storage
            user = db.users.find_one({'email': email})
            if user:
                return {
                    'id': str(user['_id']),
                    'username': user['username'],
                    'email': user['email'],
                    'password': user['password'],
                    'userType': user['userType']
                }
        else:
            # In-memory storage
            for user_id, user in get_db_client._mock_db['users'].items():
                if user['email'] == email:
                    return {
                        'id': user_id,
                        **user
                    }
        return None
    except Exception as e:
        print("Database Error:", e)
        return None

def check_user_credentials(email, password, userType):
    user = get_user_by_email(email)
    if user and user['password'] == password and user['userType'] == userType:
        return True, user
    return False, None

def user_exists(username, email):
    try:
        if client:
            # MongoDB storage
            return db.users.find_one({
                '$or': [
                    {'username': username},
                    {'email': email}
                ]
            }) is not None
        else:
            # In-memory storage
            return any(
                u['username'] == username or u['email'] == email
                for u in get_db_client._mock_db['users'].values()
            )
    except Exception as e:
        print("Database Error:", e)
        return False 