from flask import Flask
from Client import client_bp
from KBEditor import kbeditor_bp
from KBSystem import kbsystem_bp
from inference_engine import inference_engine_bp
from gpa_calculator import gpa_calculator_bp
from DB import init_db
import os

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