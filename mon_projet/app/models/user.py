from app import db
from enum import Enum

class UserRole(Enum):
    user = 'user'
    admin = 'admin'

class User(db.Model):
    __bind_key__ = 'users_db'
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.user, nullable=False)

class Auth(db.Model):
    __bind_key__ = 'auth_db'
    __tablename__ = 'auth' 
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False) 
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    adresse = db.Column(db.String(100))
    num_phone = db.Column(db.CHAR(10))
    hashed_password = db.Column(db.String(255), nullable=False)
    salt = db.Column(db.String(255), nullable=False)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    user = db.relationship('User', 
                          primaryjoin="Auth.user_id == foreign(User.id)",
                          backref=db.backref('auth', uselist=False))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "adresse": self.adresse,
            "num_phone": self.num_phone,
            "last_login": self.last_login,
            "is_active": self.is_active
        }