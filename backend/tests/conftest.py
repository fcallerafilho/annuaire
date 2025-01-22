import pytest
from app import create_app, db

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': "mysql+pymysql://root:root_password@localhost:3307/users_db",
        'SQLALCHEMY_BINDS': {
            'users_db': 'mysql+pymysql://root:root_password@localhost:3307/users_db',
            'auth_db': 'mysql+pymysql://root:root_password@localhost:3308/auth_db'
        }
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()