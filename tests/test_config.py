"""Tests for configuration management."""
import os
import pytest
from config import Config


class TestConfig:
    """Test configuration class."""
    
    def test_get_db_config(self):
        """Test database configuration retrieval."""
        config = Config.get_db_config()
        assert isinstance(config, dict)
        assert 'host' in config
        assert 'port' in config
        assert 'user' in config
        assert 'password' in config
        assert 'database' in config
    
    def test_validate_missing_secret_key(self, monkeypatch):
        """Test validation fails when FLASK_SECRET_KEY is missing."""
        monkeypatch.delenv('FLASK_SECRET_KEY', raising=False)
        with pytest.raises(ValueError, match="Missing required environment variables"):
            Config.validate()
    
    def test_validate_with_secret_key(self, monkeypatch):
        """Test validation passes when FLASK_SECRET_KEY is present."""
        monkeypatch.setenv('FLASK_SECRET_KEY', 'test-secret-key')
        # Should not raise
        Config.validate()
    
    def test_session_cookie_secure_default(self, monkeypatch):
        """Test SESSION_COOKIE_SECURE defaults to False."""
        monkeypatch.delenv('SESSION_COOKIE_SECURE', raising=False)
        # Reload config by re-importing
        import importlib
        import config
        importlib.reload(config)
        assert config.Config.SESSION_COOKIE_SECURE is False
    
    def test_session_cookie_secure_true(self, monkeypatch):
        """Test SESSION_COOKIE_SECURE can be set to True."""
        monkeypatch.setenv('SESSION_COOKIE_SECURE', 'true')
        import importlib
        import config
        importlib.reload(config)
        assert config.Config.SESSION_COOKIE_SECURE is True

