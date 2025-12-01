"""Tests for main application routes."""

from unittest.mock import patch


class TestMainRoutes:
    """Test main application routes."""

    def test_home(self, client):
        """Test home page."""
        response = client.get("/")
        assert response.status_code == 200

    def test_inspiration(self, client):
        """Test inspiration page."""
        # Mock database calls to avoid connecting to real database
        with patch("routes.main.create_images_table"):
            with patch("routes.main.get_all_active_images", return_value=[]):
                response = client.get("/inspiration")
                assert response.status_code == 200

    def test_about(self, client):
        """Test about page."""
        response = client.get("/about")
        assert response.status_code == 200

    def test_admin_requires_login(self, client):
        """Test admin page requires authentication."""
        response = client.get("/admin", follow_redirects=False)
        assert response.status_code == 302  # Redirect to login

    def test_admin_authenticated(self, authenticated_session, mock_db_connection):
        """Test admin page when authenticated."""
        # Mock database calls to avoid connecting to real database
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchall.return_value = []
        
        with patch("routes.main.create_images_table"):
            with patch("routes.main.get_db_cursor") as mock_cursor_context:
                mock_cursor_context.return_value.__enter__.return_value = mock_cursor
                mock_cursor_context.return_value.__exit__ = lambda *args: None
                
                response = authenticated_session.get("/admin")
                assert response.status_code == 200
