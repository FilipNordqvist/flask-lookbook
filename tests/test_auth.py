"""Tests for authentication routes."""
from unittest.mock import patch
from werkzeug.security import generate_password_hash


class TestLogin:
    """Test login functionality."""
    
    def test_login_get(self, client):
        """Test GET request to login page."""
        response = client.get('/login')
        assert response.status_code == 200
    
    def test_login_empty_email(self, client):
        """Test login with empty email."""
        response = client.post('/login', data={
            'email': '',
            'password': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
        # Should show flash message
    
    def test_login_invalid_credentials(self, client, mock_db_connection):
        """Test login with invalid credentials."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = None
        
        with patch('routes.auth.get_user_by_email', return_value=None):
            response = client.post('/login', data={
                'email': 'wrong@example.com',
                'password': 'wrongpassword'
            }, follow_redirects=True)
            assert response.status_code == 200
    
    def test_login_valid_credentials(self, client):
        """Test login with valid credentials."""
        mock_user = {
            'email': 'test@example.com',
            'password': generate_password_hash('testpassword123')
        }
        
        with patch('routes.auth.get_user_by_email', return_value=mock_user):
            with patch('routes.auth.check_password_hash', return_value=True):
                response = client.post('/login', data={
                    'email': 'test@example.com',
                    'password': 'testpassword123'
                }, follow_redirects=False)
                # Should redirect to admin page
                assert response.status_code in [200, 302]
                # Check session
                with client.session_transaction() as sess:
                    assert sess.get('admin_logged_in') is True


class TestRegister:
    """Test registration functionality."""
    
    def test_register_requires_login(self, client):
        """Test register page requires authentication."""
        response = client.get('/register', follow_redirects=False)
        assert response.status_code == 302  # Redirect to login
    
    def test_register_get_authenticated(self, authenticated_session):
        """Test GET request to register page when authenticated."""
        response = authenticated_session.get('/register')
        assert response.status_code == 200
    
    def test_register_empty_email(self, authenticated_session):
        """Test registration with empty email."""
        response = authenticated_session.post('/register', data={
            'email': '',
            'password': 'password123',
            'password_repeat': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_register_password_mismatch(self, authenticated_session):
        """Test registration with mismatched passwords."""
        with patch('routes.auth.user_exists', return_value=False):
            response = authenticated_session.post('/register', data={
                'email': 'new@example.com',
                'password': 'password123',
                'password_repeat': 'different123'
            }, follow_redirects=True)
            assert response.status_code == 200
    
    def test_register_short_password(self, authenticated_session):
        """Test registration with password shorter than 8 characters."""
        with patch('routes.auth.user_exists', return_value=False):
            response = authenticated_session.post('/register', data={
                'email': 'new@example.com',
                'password': 'short',
                'password_repeat': 'short'
            }, follow_redirects=True)
            assert response.status_code == 200
    
    def test_register_existing_email(self, authenticated_session):
        """Test registration with existing email."""
        with patch('routes.auth.user_exists', return_value=True):
            response = authenticated_session.post('/register', data={
                'email': 'existing@example.com',
                'password': 'password123',
                'password_repeat': 'password123'
            }, follow_redirects=True)
            assert response.status_code == 200
    
    def test_register_success(self, authenticated_session):
        """Test successful registration."""
        with patch('routes.auth.user_exists', return_value=False):
            with patch('routes.auth.create_user'):
                response = authenticated_session.post('/register', data={
                    'email': 'new@example.com',
                    'password': 'password123',
                    'password_repeat': 'password123'
                }, follow_redirects=False)
                # Should redirect to login
                assert response.status_code == 302


class TestLogout:
    """Test logout functionality."""
    
    def test_logout(self, authenticated_session):
        """Test logout clears session."""
        response = authenticated_session.get('/logout', follow_redirects=False)
        assert response.status_code == 302
        # Session should be cleared
        with authenticated_session.session_transaction() as sess:
            assert sess.get('admin_logged_in') is None

