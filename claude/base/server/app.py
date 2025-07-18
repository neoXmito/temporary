from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS
from routes import shutdown_routes
from auth_routes import auth_routes
from auth import jwt

app = Flask(__name__)

# Enable CORS for all routes
CORS(app)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
jwt.init_app(app)

# Register Blueprints
app.register_blueprint(shutdown_routes)
app.register_blueprint(auth_routes)

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
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)