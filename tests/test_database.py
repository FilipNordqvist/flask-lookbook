"""Tests for database utilities."""
from unittest.mock import patch
from database import get_user_by_email, create_user, user_exists


class TestDatabase:
    """Test database functions."""
    
    def test_get_user_by_email(self, mock_db_connection):
        """Test getting user by email."""
        mock_conn, mock_cursor = mock_db_connection
        expected_user = {'email': 'test@example.com', 'password': 'hashed'}
        mock_cursor.fetchone.return_value = expected_user
        
        with patch('database.get_db_cursor') as mock_cursor_context:
            mock_cursor_context.return_value.__enter__.return_value = mock_cursor
            mock_cursor_context.return_value.__exit__ = lambda *args: None
            
            user = get_user_by_email('test@example.com')
            assert user == expected_user
            mock_cursor.execute.assert_called_once()
    
    def test_create_user(self, mock_db_connection):
        """Test creating a new user."""
        mock_conn, mock_cursor = mock_db_connection
        
        with patch('database.get_db_cursor') as mock_cursor_context:
            mock_cursor_context.return_value.__enter__.return_value = mock_cursor
            mock_cursor_context.return_value.__exit__ = lambda *args: None
            
            create_user('test@example.com', 'hashed_password')
            mock_cursor.execute.assert_called_once()
            assert mock_conn.commit.called
    
    def test_user_exists_true(self, mock_db_connection):
        """Test user_exists returns True when user exists."""
        mock_conn, mock_cursor = mock_db_connection
        mock_cursor.fetchone.return_value = {'email': 'test@example.com'}
        
        with patch('database.get_user_by_email', return_value={'email': 'test@example.com'}):
            assert user_exists('test@example.com') is True
    
    def test_user_exists_false(self, mock_db_connection):
        """Test user_exists returns False when user doesn't exist."""
        with patch('database.get_user_by_email', return_value=None):
            assert user_exists('nonexistent@example.com') is False

