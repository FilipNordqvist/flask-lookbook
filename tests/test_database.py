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
        
        # create_user uses get_db_cursor, which internally uses get_db_connection
        # get_db_connection calls commit() when the context manager exits successfully
        # We need to mock get_db_connection to properly simulate this behavior
        from contextlib import contextmanager
        
        @contextmanager
        def mock_get_db_connection():
            """Mock get_db_connection that calls commit on exit."""
            yield mock_conn
            # This simulates the commit() call that happens after yield in get_db_connection
            mock_conn.commit()
        
        with patch('database.get_db_connection', side_effect=mock_get_db_connection):
            # Make sure the connection's cursor method returns our mocked cursor
            mock_conn.cursor.return_value = mock_cursor
            
            create_user('test@example.com', 'hashed_password')
            mock_cursor.execute.assert_called_once()
            # commit is called by get_db_connection when the context manager exits successfully
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

