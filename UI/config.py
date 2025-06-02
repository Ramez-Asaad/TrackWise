import os
from dotenv import load_dotenv

load_dotenv()

# Get database connection info from environment variables
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_HOST = os.getenv('DB_HOST', '')
DB_NAME = os.getenv('DB_NAME', 'postgres')
DB_PORT = os.getenv('DB_PORT', '5432')

# Construct database URL
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# SSL mode for Supabase
SSL_MODE = os.getenv('SSL_MODE', 'require')

# If the URL starts with postgres://, replace it with postgresql://
# This is needed because Render provides URLs with postgres:// but psycopg2 requires postgresql://
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1) 