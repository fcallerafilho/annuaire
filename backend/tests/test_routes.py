import pytest
import json
from app.models.user import User, UserRole
from app.services.user_service import UserService

def test_register_user(client, app):
    with app.app_context():
        login_response = client.post('/api/login', json={ # reminder: test with admin created during initialization
            'username': 'admin',
            'password': 'admin123'
        })
        assert login_response.status_code == 200
        admin_token = login_response.json['token']
        
        response = client.post('/api/users', json={ # use his token to create a new admin
            'username': 'testuser',
            'password': 'testpass',
            'first_name': 'Test',
            'last_name': 'User',
            'adresse': 'Test Address',
            'num_phone': '1234567890'
        }, headers={'Authorization': f'Bearer {admin_token}'})
        
        assert response.status_code == 201
        assert 'id' in response.json
        assert 'username' in response.json
        assert response.json['username'] == 'testuser'


def test_login(client):
    """Test login endpoint"""
    user_service = UserService()
    user_service.create_user(
        username='testuser',
        password='testpass',
        first_name='Test',
        last_name='User',
        adresse='Test Address',
        num_phone='1234567890'
    )
    
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data

def test_list_users(client):
    """Test listing users endpoint"""
    user_service = UserService()
    user_service.create_user(
        username='testuser',
        password='testpass',
        first_name='Test',
        last_name='User',
        adresse='Test Address',
        num_phone='1234567890'
    )
    
    response = client.post('/api/login', json={
        'username': 'testuser',
        'password': 'testpass'
    })
    token = json.loads(response.data)['token']
    
    response = client.get('/api/users', 
                         headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'username' in data[0]