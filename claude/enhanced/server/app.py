import os
import secrets
from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from datetime import timedelta
from routes import shutdown_routes
from auth_routes import auth_routes
from config import Config

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app, origins=['http://localhost:5000', 'http://127.0.0.1:5000'])

# Import models after db initialization
from models import User, PC, ActionLog

# Register Blueprints
app.register_blueprint(shutdown_routes, url_prefix='/api')
app.register_blueprint(auth_routes, url_prefix='/api')

# ======================
# Main Routes
# ======================
@app.route('/')
def home():
    return redirect(url_for('login_page'))

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

# ======================
# Database Initialization
# ======================
def init_database():
    """Initialize database with default admin user if not exists"""
    db.create_all()
    
    # Check if admin user exists
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        # Create default admin user
        hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin_user = User(
            username='admin',
            email='admin@admin.com',
            password=hashed_password,
            role='admin',
            is_active=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("[INFO] Default admin user created (username: admin, password: admin123)")

# ======================
# Error Handlers
# ======================
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return {'message': 'Token has expired', 'error': 'token_expired'}, 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return {'message': 'Invalid token', 'error': 'invalid_token'}, 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return {'message': 'Token is required', 'error': 'authorization_required'}, 401

if __name__ == '__main__':
    with app.app_context():
        init_database()
    
    print("[INFO] Server starting on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)