from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('test-key', 'dev-secret-key-change-in-production')
    
    # Database configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root_password@users_db/users_db'
    app.config['SQLALCHEMY_BINDS'] = {
        'users_db': 'mysql+pymysql://root:root_password@users_db/users_db',
        'auth_db': 'mysql+pymysql://root:root_password@auth_db/auth_db'
    }
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app