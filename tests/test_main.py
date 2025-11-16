"""Tests for main application routes."""
import pytest


class TestMainRoutes:
    """Test main application routes."""
    
    def test_home(self, client):
        """Test home page."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_inspiration(self, client):
        """Test inspiration page."""
        response = client.get('/inspiration')
        assert response.status_code == 200
    
    def test_about(self, client):
        """Test about page."""
        response = client.get('/about')
        assert response.status_code == 200
    
    def test_admin_requires_login(self, client):
        """Test admin page requires authentication."""
        response = client.get('/admin', follow_redirects=False)
        assert response.status_code == 302  # Redirect to login
    
    def test_admin_authenticated(self, authenticated_session):
        """Test admin page when authenticated."""
        response = authenticated_session.get('/admin')
        assert response.status_code == 200

