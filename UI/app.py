import sys
import os

# Add the current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import setup first to patch the system
from UI.setup import *

from flask import Flask
from UI.Client import client_bp
from UI.KBEditor import kbeditor_bp
from UI.KBSystem import kbsystem_bp
from UI.inference_engine import inference_engine_bp
from UI.gpa_calculator import gpa_calculator_bp
from UI.DB import init_db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_here')

# Initialize the database
with app.app_context():
    init_db()

# Register blueprints
app.register_blueprint(client_bp)
app.register_blueprint(kbeditor_bp)
app.register_blueprint(kbsystem_bp)
app.register_blueprint(inference_engine_bp)
app.register_blueprint(gpa_calculator_bp)

# Vercel requires the app to be named 'app'
app = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 