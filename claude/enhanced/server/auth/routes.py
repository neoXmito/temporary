from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from database.models import db, User, ActionLog
from auth.decorators import admin_required, get_current_user

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")  # Rate limiting for login attempts
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        username_or_email = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username_or_email or not password:
            return jsonify({'message': 'Username/email and password are required'}), 400
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | 
            (User.email == username_or_email)
        ).first()
        
        if not user or not user.check_password(password):
            # Log failed login attempt
            if user:
                log_action(user.id, 'failed_login', None, 'failed', 'Invalid password')
            return jsonify({'message': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'message': 'Account is disabled'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Create tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        # Log successful login
        log_action(user.id, 'login', None, 'success', 'User logged in successfully')
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Login failed', 'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user or not user.is_active:
            return jsonify({'message': 'Invalid user'}), 401
        
        new_token = create_access_token(identity=current_user_id)
        return jsonify({'access_token': new_token}), 200
        
    except Exception as e:
        return jsonify({'message': 'Token refresh failed', 'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user_info():
    """Get current user information"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get user info', 'error': str(e)}), 500

@auth_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """Get all users (admin only)"""
    try:
        users = User.query.all()
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        return jsonify({'message': 'Failed to get users', 'error': str(e)}), 500

@auth_bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    """Create new user (admin only)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        role = data.get('role', 'user').strip()
        
        # Validation
        if not username or not email or not password:
            return jsonify({'message': 'Username, email, and password are required'}), 400
        
        if role not in ['admin', 'user']:
            return jsonify({'message': 'Role must be either "admin" or "user"'}), 400
        
        if len(password) < 6:
            return jsonify({'message': 'Password must be at least 6 characters long'}), 400
        
        # Check if user already exists
        if User.query.filter((User.username == username) | (User.email == email)).first():
            return jsonify({'message': 'User with this username or email already exists'}), 409
        
        # Create new user
        user = User(
            username=username,
            email=email,
            role=role
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Log user creation
        current_user = get_current_user()
        log_action(current_user.id, 'create_user', username, 'success', f'Created {role} user: {username}')
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to create user', 'error': str(e)}), 500

@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'message': 'No data provided'}), 400
        
        # Update fields
        if 'username' in data:
            new_username = data['username'].strip()
            if new_username and new_username != user.username:
                if User.query.filter(User.username == new_username, User.id != user_id).first():
                    return jsonify({'message': 'Username already exists'}), 409
                user.username = new_username
        
        if 'email' in data:
            new_email = data['email'].strip()
            if new_email and new_email != user.email:
                if User.query.filter(User.email == new_email, User.id != user_id).first():
                    return jsonify({'message': 'Email already exists'}), 409
                user.email = new_email
        
        if 'role' in data and data['role'] in ['admin', 'user']:
            user.role = data['role']
        
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        
        if 'password' in data and data['password']:
            if len(data['password']) < 6:
                return jsonify({'message': 'Password must be at least 6 characters long'}), 400
            user.set_password(data['password'])
        
        db.session.commit()
        
        # Log user update
        current_user = get_current_user()
        log_action(current_user.id, 'update_user', user.username, 'success', f'Updated user: {user.username}')
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update user', 'error': str(e)}), 500

@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user (admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        
        current_user = get_current_user()
        if user.id == current_user.id:
            return jsonify({'message': 'Cannot delete your own account'}), 400
        
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        # Log user deletion
        log_action(current_user.id, 'delete_user', username, 'success', f'Deleted user: {username}')
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete user', 'error': str(e)}), 500

def log_action(user_id, action, target, status, details=None):
    """Helper function to log user actions"""
    try:
        log = ActionLog(
            user_id=user_id,
            action=action,
            target=target,
            status=status,
            details=details
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"[WARNING] Failed to log action: {e}")
        db.session.rollback()