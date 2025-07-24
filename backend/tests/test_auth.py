import pytest
import json
from app.models import User


class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_register_user(self, client):
        """Test user registration."""
        user_data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'securepassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/api/auth/register', 
                             json=user_data,
                             content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['email'] == user_data['email']
        assert data['user']['username'] == user_data['username']
    
    def test_register_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        user_data = {
            'email': 'test@example.com',  # Same as test_user
            'username': 'newuser',
            'password': 'securepassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = client.post('/api/auth/register', json=user_data)
        assert response.status_code == 400
        data = response.get_json()
        assert 'email' in data['message'].lower()
    
    def test_register_invalid_data(self, client):
        """Test registration with invalid data."""
        # Missing required fields
        user_data = {
            'email': 'invalid@example.com',
            'username': 'testuser'
            # Missing password, first_name, last_name
        }
        
        response = client.post('/api/auth/register', json=user_data)
        assert response.status_code == 400
    
    def test_login_valid_credentials(self, client, test_user):
        """Test login with valid credentials."""
        login_data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['id'] == str(test_user.id)
    
    def test_login_invalid_email(self, client):
        """Test login with invalid email."""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': 'somepassword'
        }
        
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 401
    
    def test_login_invalid_password(self, client, test_user):
        """Test login with invalid password."""
        login_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 401
    
    def test_get_profile(self, client, auth_headers):
        """Test getting user profile."""
        response = client.get('/api/auth/profile', headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['email'] == 'test@example.com'
        assert data['username'] == 'testuser'
    
    def test_update_profile(self, client, auth_headers):
        """Test updating user profile."""
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = client.put('/api/auth/profile', 
                            json=update_data, 
                            headers=auth_headers)
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['first_name'] == 'Updated'
        assert data['last_name'] == 'Name'
    
    def test_change_password(self, client, auth_headers):
        """Test changing password."""
        password_data = {
            'current_password': 'testpassword123',
            'new_password': 'newsecurepassword456'
        }
        
        response = client.post('/api/auth/change-password', 
                             json=password_data, 
                             headers=auth_headers)
        assert response.status_code == 200
    
    def test_change_password_wrong_current(self, client, auth_headers):
        """Test changing password with wrong current password."""
        password_data = {
            'current_password': 'wrongpassword',
            'new_password': 'newsecurepassword456'
        }
        
        response = client.post('/api/auth/change-password', 
                             json=password_data, 
                             headers=auth_headers)
        assert response.status_code == 400
    
    def test_logout(self, client, auth_headers):
        """Test user logout."""
        response = client.post('/api/auth/logout', headers=auth_headers)
        assert response.status_code == 200
    
    def test_protected_route_without_token(self, client):
        """Test accessing protected route without authentication."""
        response = client.get('/api/auth/profile')
        assert response.status_code == 401
    
    def test_protected_route_with_invalid_token(self, client):
        """Test accessing protected route with invalid token."""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/api/auth/profile', headers=headers)
        assert response.status_code == 422 