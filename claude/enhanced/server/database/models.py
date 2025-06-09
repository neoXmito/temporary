from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' or 'user'
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class PC(db.Model):
    __tablename__ = 'pcs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ip = db.Column(db.String(15), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='offline')  # 'online', 'offline'
    last_seen = db.Column(db.DateTime)
    registered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    registered_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationship
    registrar = db.relationship('User', backref=db.backref('registered_pcs', lazy=True))
    
    def to_dict(self):
        """Convert PC to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'ip': self.ip,
            'status': self.status,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'registered_at': self.registered_at.isoformat() if self.registered_at else None,
            'registered_by': self.registrar.username if self.registrar else None
        }

class ActionLog(db.Model):
    __tablename__ = 'action_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # 'shutdown', 'ping', 'register_pc', etc.
    target = db.Column(db.String(100))  # PC name or IP
    status = db.Column(db.String(20), nullable=False)  # 'success', 'failed'
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('action_logs', lazy=True))
    
    def to_dict(self):
        """Convert action log to dictionary"""
        return {
            'id': self.id,
            'user': self.user.username if self.user else None,
            'action': self.action,
            'target': self.target,
            'status': self.status,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }