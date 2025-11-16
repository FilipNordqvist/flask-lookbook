"""Pytest configuration and shared fixtures."""

import os
import pytest
from unittest.mock import patch, MagicMock
from app import create_app


@pytest.fixture
def app():
    """Create application for testing."""
    # Set test environment variables
    os.environ["FLASK_SECRET_KEY"] = "test-secret-key"
    os.environ["MYSQLHOST"] = "localhost"
    os.environ["MYSQLUSER"] = "test_user"
    os.environ["MYSQLPASSWORD"] = "test_password"
    os.environ["MYSQLDATABASE"] = "test_db"
    os.environ["RESEND_API_KEY"] = "test-resend-key"

    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False  # Disable CSRF for testing

    yield app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def mock_db_connection():
    """Mock database connection."""
    with patch("database.mysql.connector.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.is_connected.return_value = True
        mock_connect.return_value = mock_conn
        yield mock_conn, mock_cursor


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    from werkzeug.security import generate_password_hash

    return {
        "email": "test@example.com",
        "password": generate_password_hash("testpassword123"),
    }


@pytest.fixture
def authenticated_session(client):
    """Create an authenticated session."""
    from werkzeug.security import generate_password_hash

    mock_user = {
        "email": "test@example.com",
        "password": generate_password_hash("testpassword123"),
    }

    with patch("routes.auth.get_user_by_email", return_value=mock_user):
        with patch("routes.auth.check_password_hash", return_value=True):
            client.post(
                "/login",
                data={"email": "test@example.com", "password": "testpassword123"},
                follow_redirects=False,
            )
            return client
