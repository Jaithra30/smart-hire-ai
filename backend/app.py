import os
from flask import Flask, send_from_directory
from flask_cors import CORS

from backend.routes.analyze import analyze_bp
from backend.routes.debug import debug_bp
from backend.routes.hr_routes import hr_bp
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Register Blueprints
app.register_blueprint(analyze_bp)
app.register_blueprint(hr_bp)
app.register_blueprint(debug_bp)

# Serve frontend HTML files
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/dashboard')
def serve_dashboard():
    return send_from_directory(app.static_folder, 'dashboard.html')

@app.route('/hr')
def serve_hr():
    return send_from_directory(app.static_folder, 'hr.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
