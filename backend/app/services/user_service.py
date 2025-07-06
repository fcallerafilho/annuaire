from app.models.user import User, Auth, UserRole
from sqlalchemy.exc import SQLAlchemyError
from app import db
from datetime import datetime
import hashlib
import jwt
from typing import Optional, List, Dict
from flask import current_app
from typing import Optional

class UserService:
    def __init__(self):
        self.TOKEN_EXPIRY = 24 * 3600  # 24 hours

    def _hash_password(self, password: str, salt: Optional[str] = None) -> tuple:
        """Hash password with salt"""
        if not salt:
            salt = '5f7c6a83f1e9b4d2a8c5e7d9b2a4f6c8'  # Use our fixed salt for consistency
        print(f"Hashing password with salt: {salt}")  # Debug
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return hashed, salt

    def _verify_password(self, password: str, hashed: str, salt: str) -> bool:
        """Verify password against stored hash"""
        calculated_hash, _ = self._hash_password(password, salt)
        return calculated_hash == hashed

    def create_user(self, username: str, first_name: str, last_name: str, 
               password: str, adresse: str, num_phone: str, role: UserRole = UserRole.user) -> User:
        """Create a new user with authentication details"""
        try:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                raise Exception("Username already exists")

            hashed_password, salt = self._hash_password(password)
            
            # Convert string role to UserRole enum if a string was passed
            if isinstance(role, str):
                role = UserRole(role)
            
            new_user = User(username=username, role=role)
            db.session.add(new_user)
            db.session.flush()

            new_auth = Auth(
                user_id=new_user.id,
                first_name=first_name,
                last_name=last_name,
                adresse=adresse,
                num_phone=num_phone,
                hashed_password=hashed_password,
                salt=salt,
                is_active=True
            )
            db.session.add(new_auth)
            db.session.commit()

            return new_user
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Error creating user: {str(e)}")

    def authenticate(self, username: str, password: str) -> Optional[str]:
        """Authenticate user and return JWT token"""
        print(f"Attempting authentication for username: {username}")  # Debug
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print("User not found")  # Debug
            return None
        
        if not user.auth:
            print("No auth record found")  # Debug
            return None
            
        if not user.auth.is_active:
            print("User not active")  # Debug
            return None

        # Debug password verification
        calculated_hash, _ = self._hash_password(password, user.auth.salt)
        print(f"Stored hash: {user.auth.hashed_password}")  # Debug
        print(f"Calculated hash: {calculated_hash}")  # Debug
        print(f"Stored salt: {user.auth.salt}")  # Debug

        if self._verify_password(password, user.auth.hashed_password, user.auth.salt):
            user.auth.last_login = datetime.utcnow()
            db.session.commit()
            
            token = jwt.encode(
                {
                    'user_id': user.id,
                    'role': user.role.value,
                    'exp': datetime.utcnow().timestamp() + self.TOKEN_EXPIRY
                },
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            return token
        print("Password verification failed")  # Debug
        return None

    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def change_password(self, user_id: int, old_password: Optional[str], new_password: str, require_old: bool = True) -> bool:
        """Change user password"""
        print(f"Attempting password change for user_id: {user_id}, require_old: {require_old}")
        
        auth = Auth.query.filter_by(user_id=user_id).first()
        if not auth:
            print(f"No auth record found for user_id: {user_id}")
            raise Exception("User not found")
        
        if not auth.is_active:
            print(f"User {user_id} is inactive")
            raise Exception("Cannot change password for inactive user")

        if require_old:
            print("Verifying old password")
            if not old_password:
                raise Exception("Old password is required")
                
            if not self._verify_password(old_password, auth.hashed_password, auth.salt):
                print("Old password verification failed")
                return False
            print("Old password verified successfully")

        print("Generating new password hash")
        hashed_password, salt = self._hash_password(new_password)
        
        try:
            auth.hashed_password = hashed_password
            auth.salt = salt
            db.session.commit()
            print(f"Password successfully updated for user {user_id}")
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Database error during password update: {str(e)}")
            raise Exception(f"Database error: {str(e)}")
        except Exception as e:
            print(f"Unexpected error during password update: {str(e)}")
            raise

    def promote_user(self, user_id: int) -> bool:
        """Promote user to admin"""
        user = User.query.get(user_id)
        if user and user.role != UserRole.admin:
            user.role = UserRole.admin
            db.session.commit()
            return True
        return False

    def demote_user(self, user_id: int) -> bool:
        """Demote admin to regular user"""
        user = User.query.get(user_id)
        if user and user.role != UserRole.user:
            user.role = UserRole.user
            db.session.commit()
            return True
        return False

    def list_users(self, search_term: Optional[str] = None) -> List[Dict]:
        """List all users with optional search"""
        # First get all users
        users_query = User.query
        
        if search_term:
            search = f"%{search_term}%"
            users_query = users_query.filter(User.username.ilike(search))
        
        users = users_query.all()
        
        # Then get their auth details
        user_ids = [user.id for user in users]
        auth_records = Auth.query.filter(
            Auth.user_id.in_(user_ids),
            Auth.is_active == True
        ).all()
        
        # Create a lookup dictionary for auth records
        auth_lookup = {auth.user_id: auth for auth in auth_records}
        
        # Combine the data
        result = []
        for user in users:
            auth = auth_lookup.get(user.id)
            if auth and auth.is_active:  # Only include users with active auth records
                result.append({
                    "id": user.id,
                    "username": user.username,
                    "role": user.role.value,
                    "first_name": auth.first_name,
                    "last_name": auth.last_name,
                    "adresse" : auth.adresse,
                    "num_phone":auth.num_phone
                })
        
        return result

    def delete_user(self, user_id: int) -> bool:
        """Soft delete user by setting is_active to False"""
        auth = Auth.query.filter_by(user_id=user_id).first()
        if auth:
            auth.is_active = False
            db.session.commit()
            return True
        return False
    
    def update_profile(self, user_id: int, profile_data: dict) -> Optional[dict]:
        """Update user profile information"""
        try:
            auth = Auth.query.filter_by(user_id=user_id).first()
            if not auth:
                return None
                
            # Update allowed fields
            for field in ['first_name', 'last_name', 'adresse', 'num_phone']:
                if field in profile_data:
                    setattr(auth, field, profile_data[field])
            
            db.session.commit()
            return auth.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise Exception(f"Error updating profile: {str(e)}")

    def delete_user(self, user_id: int) -> bool:
        """Soft delete user by setting is_active to False"""
        auth = Auth.query.filter_by(user_id=user_id).first()
        if auth:
            auth.is_active = False
            db.session.commit()
            return True
        return False