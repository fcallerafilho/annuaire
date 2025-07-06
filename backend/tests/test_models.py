import pytest
from app import create_app, db
from app.models.user import User, Auth, UserRole

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:root_password@mysql/test_users_db"
    app.config['SQLALCHEMY_BINDS'] = {
        'users_db': 'mysql+pymysql://root:root_password@mysql/test_users_db',
        'auth_db': 'mysql+pymysql://root:root_password@mysql/test_auth_db'
    }
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_create_user():
    """Test creating a new user"""
    user = User(username="testuser", role=UserRole.user)
    assert user.username == "testuser"
    assert user.role == UserRole.user

def test_create_auth():
    """Test creating auth details"""
    auth = Auth(
        user_id=1,
        first_name="Test",
        last_name="User",
        adresse="Test Address",
        num_phone="1234567890",
        hashed_password="hashedpass",
        salt="salt",
        is_active=True
    )
    assert auth.user_id == 1
    assert auth.first_name == "Test"
    assert auth.is_active == True