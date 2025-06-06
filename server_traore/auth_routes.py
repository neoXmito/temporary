from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token,get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3  # ou SQLAlchemy


auth_routes = Blueprint('auth_routes', __name__)

# # ==============================
# # Login Route (Admin Login)
# # ==============================
# @auth_routes.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     if data.get('username') == 'admin' and data.get('password') == 'admin':
#         token = create_access_token(identity=data['username'])
#         return jsonify({'token': token}), 200
#     else:
#         return jsonify({'message': 'Invalid credentials'}), 401


@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    role = data.get('role', 'user')  # Par défaut, user

    if not username or not email or not password:
        return jsonify({'message': 'Missing fields'}), 400

    hashed_password = generate_password_hash(password)

    try:
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        # Vérifier si username ou email existe déjà
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            return jsonify({'message': 'Email already exists'}), 409

        # Insérer nouvel utilisateur avec role 'user' par défaut
        cursor.execute("INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
                       (username, email, hashed_password, role))
        conn.commit()
        conn.close()
        return jsonify({'message': 'User created successfully'}), 201

    except Exception as e:
        return jsonify({'message': 'Internal server error', 'error': str(e)}), 500


# ==============================
# Login Route (User Login)
@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Exemple avec sqlite
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT password, role FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    conn.close()

    if result and check_password_hash(result[0], password):
        role = result[1]
        token = create_access_token(identity={'email': email, 'role': role})
        return jsonify({'token': token, 'role': role}), 200 # Retourne le token et le rôle de l'utilisateur pour pouvoir faire des redictions côté client 
    else:
        return jsonify({'message': 'Invalid credentials'}), 401
    

# ==============================
# Logout Route

@auth_routes.route('/logout', methods=['POST'])
def logout():
    # Pour le logout, on n'a pas besoin de faire quoi que ce soit côté serveur
    # JWT est stateless, donc le token devient invalide simplement en ne l'utilisant plus
    return jsonify({'message': 'Logged out successfully'}), 200


# ==============================
# Dashboard Route (Accessible by both admin and standard users)

@auth_routes.route('/dashboard')
@jwt_required()
def dashboard():
    user = get_jwt_identity()  # ex: {'username': 'john', 'role': 'admin'}
    if user['role'] == 'admin':
        return jsonify({'message': 'Welcome admin'}), 200
    else:
        return jsonify({'message': 'Standard user dashboard'}), 200
