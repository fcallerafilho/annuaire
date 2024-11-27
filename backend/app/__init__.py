from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root_password@users_db/users_db'
    app.config['SQLALCHEMY_BINDS'] = {
        'users_db': 'mysql+pymysql://root:root_password@users_db/users_db',
        'auth_db': 'mysql+pymysql://root:root_password@auth_db/auth_db'
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-key'
    
    db.init_app(app)
    
    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    with app.app_context():
        db.create_all()
        init_first_user(app)
        
    return app

def init_first_user(app):
    from app.models.user import User, UserRole
    from app.services.user_service import UserService
    
    if User.query.count() == 0:
        user_service = UserService()
        try:
            user_service.create_user(
                username='admin',
                first_name='Admin',
                last_name='User',
                password='admin123',
                adresse='123 Admin St',
                num_phone='1234567890',
                role=UserRole.admin
            )
            print("Premier utilisateur admin créé avec succès!")
            print("Username: admin")
            print("Password: admin123")
        except Exception as e:
            print(f"Erreur lors de la création du premier utilisateur : {str(e)}")