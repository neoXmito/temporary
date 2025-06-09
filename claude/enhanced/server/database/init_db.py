from database.models import db, User, PC
from config import Config

def init_database(app):
    """Initialize database and create default admin user"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            # Create default admin user
            admin = User(
                username=Config.DEFAULT_ADMIN_USERNAME,
                email=Config.DEFAULT_ADMIN_EMAIL,
                role='admin'
            )
            admin.set_password(Config.DEFAULT_ADMIN_PASSWORD)
            
            db.session.add(admin)
            db.session.commit()
            
            print(f"[INFO] Default admin user created:")
            print(f"       Username: {Config.DEFAULT_ADMIN_USERNAME}")
            print(f"       Email: {Config.DEFAULT_ADMIN_EMAIL}")
            print(f"       Password: {Config.DEFAULT_ADMIN_PASSWORD}")
            print(f"       Please change the default password after first login!")
        
        print("[INFO] Database initialized successfully.")

def migrate_old_data(app):
    """Migrate data from old db.json file if it exists"""
    import json
    import os
    
    old_db_path = 'db.json'
    if not os.path.exists(old_db_path):
        return
    
    with app.app_context():
        try:
            with open(old_db_path, 'r') as f:
                old_pcs = json.load(f)
            
            # Get admin user for registration
            admin = User.query.filter_by(role='admin').first()
            
            for pc_data in old_pcs:
                # Check if PC already exists
                existing_pc = PC.query.filter_by(
                    name=pc_data['name'], 
                    ip=pc_data['ip']
                ).first()
                
                if not existing_pc:
                    pc = PC(
                        name=pc_data['name'],
                        ip=pc_data['ip'],
                        status=pc_data.get('status', 'offline'),
                        registered_by=admin.id if admin else None
                    )
                    db.session.add(pc)
            
            db.session.commit()
            print(f"[INFO] Successfully migrated {len(old_pcs)} PCs from old database.")
            
            # Backup old file
            os.rename(old_db_path, f"{old_db_path}.backup")
            print(f"[INFO] Old database file backed up as {old_db_path}.backup")
            
        except Exception as e:
            print(f"[WARNING] Failed to migrate old data: {e}")
            db.session.rollback()