from flask import Flask
from Client import client_bp
from KBEditor import kbeditor_bp
from KBSystem import kbsystem_bp
from inference_engine import inference_engine_bp
from gpa_calculator import gpa_calculator_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Register blueprints
app.register_blueprint(client_bp)
app.register_blueprint(kbeditor_bp)
app.register_blueprint(kbsystem_bp)
app.register_blueprint(inference_engine_bp)
app.register_blueprint(gpa_calculator_bp)

if __name__ == '__main__':
    app.run(debug=True) 