from flask import Blueprint, request, jsonify
from app.services.user_service import UserService, UserRole
from functools import wraps
from app.models.user import User, UserRole

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
        # Check if this is the first user being created
        if User.query.count() == 0:
            user = user_service.create_user(
                username=data.get('username'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                password=data.get('password'),
                adresse=data.get('adresse'),
                num_phone=data.get('num_phone'),
                role=UserRole.admin  # Force first user to be admin
            )
            return jsonify({
                "message": "Admin user created successfully",
                "id": user.id, 
                "username": user.username
            }), 201
            
        # For subsequent users, require admin authentication
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({"error": "No authentication token provided"}), 401
        
        token = token.split('Bearer ')[1]
        payload = user_service.verify_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        if payload.get('role') != 'admin':
            return jsonify({"error": "Admin privileges required"}), 403
        
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
            role=UserRole(role)
        )
        return jsonify({"id": user.id, "username": user.username}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@api_bp.route('/users/<int:user_id>/password', methods=['PUT'])
@login_required
def change_password(user_id):
    if request.user['user_id'] != user_id and request.user['role'] != UserRole.admin.value:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({"error": "Missing password data"}), 400
    
    if user_service.change_password(user_id, old_password, new_password):
        return jsonify({"message": "Password updated successfully"}), 200
    return jsonify({"error": "Failed to update password"}), 400

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
@admin_required
def delete_user(user_id):
    if user_service.delete_user(user_id):
        return jsonify({"message": "User deleted successfully"}), 200
    return jsonify({"error": "Failed to delete user"}), 404