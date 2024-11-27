import pytest
from app.services.user_service import UserService
from app.models.user import UserRole

def test_user_creation(app): 
    with app.app_context(): 
        service = UserService()
        user = service.create_user(
            username="testuser",
            first_name="Test",
            last_name="User",
            password="password123",
            adresse="Test Address",
            num_phone="1234567890"
        )
        assert user.username == "testuser"
        assert user.role == UserRole.user

def test_password_change(app):
    with app.app_context():
        service = UserService()
        user = service.create_user(
            username="testuser",
            first_name="Test",
            last_name="User",
            password="oldpass",
            adresse="Test Address",
            num_phone="1234567890"
        )
        
        success = service.change_password(user.id, "oldpass", "newpass")
        assert success == True
        
        token = service.authenticate("testuser", "newpass")
        assert token is not None

def test_user_promotion(app):
    with app.app_context():
        service = UserService()
        user = service.create_user(
            username="testuser",
            first_name="Test",
            last_name="User",
            password="password123",
            adresse="Test Address",
            num_phone="1234567890"
        )
        
        assert user.role == UserRole.user
        success = service.promote_user(user.id)
        assert success == True