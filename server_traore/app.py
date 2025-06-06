from flask import Flask, render_template, jsonify
from flask_cors import CORS
from routes import shutdown_routes
from auth_routes import auth_routes
from auth import jwt
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import redirect, url_for

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)
# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key'

# Initialize JWT
jwt.init_app(app)

# Register Blueprints (routes)
app.register_blueprint(shutdown_routes)
app.register_blueprint(auth_routes)

# Serve the Dashboard
@app.route('/')
def index():
    return redirect(url_for('register'))

@app.route('/register')
def register():
    return render_template('screen_1.html')  # Page de register

@app.route('/login')
def login():
    return render_template('screen_2.html')



# @app.route('/user_dash')
# @jwt_required()
# def user_dashboard():
#     user = get_jwt_identity()
#     if user['role'] != 'user':
#         return "Unauthorized", 403
#     return render_template('screen_4.html')  # dashboard user

@app.route('/user_dash_data')
@jwt_required()
def user_dashboard_data():
    user = get_jwt_identity()
    if user['role'] != 'user':
        return jsonify({'msg': 'Unauthorized'}), 403
    return jsonify({'msg': 'Welcome to the user dashboard'}), 200

@app.route('/user_dash')
def user_dash():
    return render_template('screen_4.html')  # page HTML simple, sans @jwt_required()

@app.route('/admin_dash')
@jwt_required()
def admin_dashboard():
    user = get_jwt_identity()
    if user['role'] != 'admin':
        return "Unauthorized", 403
    return render_template('screen_3.html')  # dashboard admin















if __name__ == '__main__':
    # Run the Flask development server
    app.run(host='0.0.0.0', port=5000, debug=True)
