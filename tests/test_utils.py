"""Tests for utility functions."""
from utils import login_required


class TestLoginRequired:
    """Test login_required decorator."""
    
    def test_login_required_without_session(self, app):
        """Test decorator redirects when not logged in."""
        with app.test_request_context():
            @app.route('/protected')
            @login_required
            def protected():
                return "Protected"
            
            # Create a test client
            client = app.test_client()
            response = client.get('/protected', follow_redirects=False)
            assert response.status_code == 302  # Redirect to login
    
    def test_login_required_with_session(self, app):
        """Test decorator allows access when logged in."""
        with app.test_request_context():
            @app.route('/protected')
            @login_required
            def protected():
                return "Protected"
            
            # Set session
            with app.test_client() as client:
                with client.session_transaction() as sess:
                    sess['admin_logged_in'] = True
                
                response = client.get('/protected')
                assert response.status_code == 200
                assert b"Protected" in response.data

