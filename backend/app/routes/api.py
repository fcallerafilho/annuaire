from flask import Blueprint, request, jsonify, current_app
from app.services.user_service import UserService, UserRole
from functools import wraps
from app.models.user import User, UserRole
import jwt
import json


api_bp = Blueprint('api', __name__)
user_service = UserService()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({"error": "No authentication token provided"}), 401
        
        token = token.split('Bearer ')[1]
        payload = user_service.verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        request.user = payload
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({"error": "No authentication token provided"}), 401
        
        token = token.split('Bearer ')[1]
        payload = user_service.verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        if payload.get('role') != UserRole.admin.value:
            return jsonify({"error": "Admin privileges required"}), 403
        
        request.user = payload
        return f(*args, **kwargs)
    return decorated_function

def admin_or_self_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = kwargs.get('user_id')
        token = request.headers.get('Authorization')

        if not token or not token.startswith('Bearer '):
            return jsonify({"error": "No authentication token provided"}), 401

        token = token.split('Bearer ')[1]
        payload = user_service.verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        current_user_id = payload.get('user_id')
        if current_user_id is None:
            return jsonify({"error": "User ID not found in token"}), 401

        if user_id == int(current_user_id):
            request.user = payload
            return f(*args, **kwargs)

        if payload.get('role') != UserRole.admin.value:
            return jsonify({"error": "Admin privileges required"}), 403

        request.user = payload
        return f(*args, **kwargs)

    return decorated_function

@api_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400
    
    token = user_service.authenticate(username, password)
    if token:
        return jsonify({"token": token}), 200
    return jsonify({"error": "Invalid credentials"}), 401

@api_bp.route('/users', methods=['GET'])
@login_required
def list_users():
    search_term = request.args.get('search')
    users = user_service.list_users(search_term)
    return jsonify(users), 200

@api_bp.route('/users', methods=['POST'])
def create_user():
    data = request.json
    try:
        # Case 1: First user creation (becomes admin)
        if User.query.count() == 0:
            user = user_service.create_user(
                username=data.get('username'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                password=data.get('password'),
                adresse=data.get('adresse'),
                num_phone=data.get('num_phone'),
                role=UserRole.admin
            )
            return jsonify({
                "message": "Admin user created successfully",
                "id": user.id, 
                "username": user.username
            }), 201

        # Get token if exists
        token = request.headers.get('Authorization')
        
        # Case 2: Admin creating a user
        if token and token.startswith('Bearer '):
            token = token.split('Bearer ')[1]
            payload = user_service.verify_token(token)
            
            if not payload:
                return jsonify({"error": "Invalid or expired token"}), 401
            
            if payload.get('role') != 'admin':
                return jsonify({"error": "Admin privileges required"}), 403
            
            # Admin can specify the role
            role = data.get('role', 'user')
            if role not in ['user', 'admin']:
                role = 'user'
                
            user = user_service.create_user(
                username=data.get('username'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                password=data.get('password'),
                adresse=data.get('adresse'),
                num_phone=data.get('num_phone'),
                role=UserRole[role]
            )
            return jsonify({
                "message": "User created successfully",
                "id": user.id,
                "username": user.username
            }), 201
            
        # Case 3: Self-registration (no token or invalid token format)
        user = user_service.create_user(
            username=data.get('username'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            password=data.get('password'),
            adresse=data.get('adresse'),
            num_phone=data.get('num_phone'),
            role=UserRole.user  # Force regular user for self-registration
        )
        return jsonify({
            "message": "User registered successfully",
            "id": user.id,
            "username": user.username
        }), 201
            
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/users/<int:user_id>/password', methods=['PUT'])
@login_required
def change_password(user_id):
    print(f"Password change attempt for user_id: {user_id}")
    print(f"Request made by user_id: {request.user['user_id']} with role: {request.user['role']}")
    
    if request.user['user_id'] != user_id and request.user['role'] != UserRole.admin.value:
        print(f"Unauthorized password change attempt: User {request.user['user_id']} tried to change password for user {user_id}")
        return jsonify({
            "error": "Unauthorized",
            "details": "You must be either the user or an admin to change this password"
        }), 403
    
    data = request.json
    print(f"Received password change data: {data}")
    new_password = data.get('new_password')
    
    if not new_password:
        return jsonify({
            "error": "Missing data",
            "details": "New password is required"
        }), 400
    
    # If it's the user changing their own password, require old password
    if request.user['user_id'] == user_id:
        print("User is changing their own password")
        old_password = data.get('old_password')
        if not old_password:
            return jsonify({
                "error": "Missing data",
                "details": "Old password is required when changing your own password"
            }), 400
        try:
            success = user_service.change_password(user_id, old_password, new_password, require_old=True)
            if not success:
                return jsonify({
                    "error": "Authentication failed",
                    "details": "The old password provided is incorrect"
                }), 400
        except Exception as e:
            print(f"Error during self password change: {str(e)}")
            return jsonify({
                "error": "Password change failed",
                "details": str(e)
            }), 500
    else:
        # Admin changing someone else's password
        print(f"Admin (user_id: {request.user['user_id']}) is changing password for user {user_id}")
        try:
            success = user_service.change_password(user_id, None, new_password, require_old=False)
            if not success:
                return jsonify({
                    "error": "Password change failed",
                    "details": "User not found or inactive"
                }), 404
        except Exception as e:
            print(f"Error during admin password change: {str(e)}")
            return jsonify({
                "error": "Password change failed",
                "details": str(e)
            }), 500
    
    print(f"Password successfully changed for user {user_id}")
    return jsonify({
        "message": "Password updated successfully",
        "user_id": user_id
    }), 200

@api_bp.route('/users/<int:user_id>/promote', methods=['PUT'])
@admin_required
def promote_user(user_id):
    if user_service.promote_user(user_id):
        return jsonify({"message": "User promoted to admin"}), 200
    return jsonify({"error": "Failed to promote user"}), 400

@api_bp.route('/users/<int:user_id>/demote', methods=['PUT'])
@admin_required
def demote_user(user_id):
    if user_service.demote_user(user_id):
        return jsonify({"message": "User demoted to regular user"}), 200
    return jsonify({"error": "Failed to demote user"}), 400

@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_or_self_required # by pass the admin requirement if you want to close your acount.
def delete_user(user_id):
    if user_service.delete_user(user_id):
        return jsonify({"message": "User deleted successfully"}), 200
    return jsonify({"error": "Failed to delete user"}), 404

@api_bp.route('/logs', methods=['POST'])
@login_required     
def receive_frontend_logs():
    try:
        user_info = request.user

        logs = request.json.get('logs', [])
        
        for log in logs:
            log['user_id'] = user_info.get('user_id')
            log['user_role'] = user_info.get('role')
            
            # Logging avec le logger de sécurité
            current_app.security_logger.logger.info(
                f"Frontend log: {json.dumps(log)}",
                extra={
                    'user_id': user_info.get('user_id'),
                    'username': user_info.get('username'),
                    'ip': request.remote_addr
                }
            )

        return jsonify({"status": "success", "logged": len(logs)}), 200
        
    except Exception as e:
        current_app.security_logger.logger.error(
            f"Error processing logs: {str(e)}",
            extra={
                'user_id': request.user.get('user_id') if request.user else None,
                'ip': request.remote_addr
            }
        )
        return jsonify({"error": "Failed to process logs"}), 500
    
@api_bp.route('/users/<int:user_id>/profile', methods=['PUT'])
@admin_or_self_required
def update_profile(user_id):
    """Update user profile information"""
    print(f"Received profile update request for user_id: {user_id}")
    print(f"Request data: {request.json}")
    
    data = request.json
    if not data:
        print("No JSON data in request")
        return jsonify({"error": "No data provided"}), 400
    
    # Validate required fields
    allowed_fields = {'first_name', 'last_name', 'adresse', 'num_phone'}
    update_data = {k: v for k, v in data.items() if k in allowed_fields}
    
    print(f"Filtered update data: {update_data}")
    
    if not update_data:
        print("No valid fields found in request data")
        return jsonify({"error": "No valid fields to update"}), 400
        
    try:
        print("Attempting to update profile...")
        updated_profile = user_service.update_profile(user_id, update_data)
        
        if not updated_profile:
            print("User not found or inactive")
            return jsonify({"error": "User not found or inactive"}), 404
            
        print(f"Profile updated successfully: {updated_profile}")
        return jsonify(updated_profile), 200
    except Exception as e:
        print(f"Error during profile update: {str(e)}")
        return jsonify({"error": str(e)}), 400