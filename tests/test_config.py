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
    
    def test_base_domain_default(self):
        """Test BASE_DOMAIN defaults to nordqvist.tech."""
        # Clear any existing BASE_DOMAIN
        import os
        original = os.environ.pop('BASE_DOMAIN', None)
        try:
            import importlib
            import config
            importlib.reload(config)
            assert config.Config.BASE_DOMAIN == "nordqvist.tech"
        finally:
            # Restore original value if it existed
            if original:
                os.environ['BASE_DOMAIN'] = original
    
    def test_base_domain_custom(self, monkeypatch):
        """Test BASE_DOMAIN can be set via environment variable."""
        monkeypatch.setenv('BASE_DOMAIN', 'example.com')
        import importlib
        import config
        importlib.reload(config)
        assert config.Config.BASE_DOMAIN == "example.com"
    
    def test_email_from_uses_base_domain(self, monkeypatch):
        """Test EMAIL_FROM uses BASE_DOMAIN when EMAIL_FROM not explicitly set."""
        monkeypatch.setenv('BASE_DOMAIN', 'example.com')
        monkeypatch.delenv('EMAIL_FROM', raising=False)
        import importlib
        import config
        importlib.reload(config)
        assert config.Config.EMAIL_FROM == "info@example.com"
    
    def test_email_from_explicit_override(self, monkeypatch):
        """Test EMAIL_FROM can be explicitly set, overriding BASE_DOMAIN."""
        monkeypatch.setenv('BASE_DOMAIN', 'example.com')
        monkeypatch.setenv('EMAIL_FROM', 'custom@other.com')
        import importlib
        import config
        importlib.reload(config)
        assert config.Config.EMAIL_FROM == "custom@other.com"
    
    def test_email_to_uses_base_domain(self, monkeypatch):
        """Test EMAIL_TO uses BASE_DOMAIN when EMAIL_TO not explicitly set."""
        monkeypatch.setenv('BASE_DOMAIN', 'example.com')
        monkeypatch.delenv('EMAIL_TO', raising=False)
        import importlib
        import config
        importlib.reload(config)
        assert config.Config.EMAIL_TO == "info@example.com"
    
    def test_email_to_explicit_override(self, monkeypatch):
        """Test EMAIL_TO can be explicitly set, overriding BASE_DOMAIN."""
        monkeypatch.setenv('BASE_DOMAIN', 'example.com')
        monkeypatch.setenv('EMAIL_TO', 'custom@other.com')
        import importlib
        import config
        importlib.reload(config)
        assert config.Config.EMAIL_TO == "custom@other.com"

