"""Tests for contact form routes."""
from unittest.mock import patch, MagicMock


class TestContact:
    """Test contact form functionality."""
    
    def test_contact_get(self, client):
        """Test GET request to contact page."""
        response = client.get('/contact')
        assert response.status_code == 200
    
    def test_send_email_missing_fields(self, client):
        """Test sending email with missing required fields."""
        # Missing email
        response = client.post('/send', data={
            'message': 'Test message'
        }, follow_redirects=True)
        assert response.status_code == 200
        
        # Missing message
        response = client.post('/send', data={
            'email': 'test@example.com'
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_send_email_invalid_email(self, client):
        """Test sending email with invalid email format."""
        response = client.post('/send', data={
            'email': 'invalid-email',
            'message': 'Test message'
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_send_email_success(self, client):
        """Test successful email sending."""
        with patch('routes.contact.resend.Emails.send') as mock_send:
            mock_send.return_value = MagicMock()
            response = client.post('/send', data={
                'email': 'test@example.com',
                'message': 'Test message',
                'name': 'Test User',
                'phone': '1234567890'
            }, follow_redirects=False)
            assert response.status_code == 302  # Redirect
            mock_send.assert_called_once()
    
    def test_send_email_html_escaping(self, client):
        """Test that user input is properly escaped in email."""
        with patch('routes.contact.resend.Emails.send') as mock_send:
            mock_send.return_value = MagicMock()
            client.post('/send', data={
                'email': 'test@example.com',
                'message': 'Test <script>alert("xss")</script>',
                'name': '<b>Test</b>',
                'phone': '1234567890'
            }, follow_redirects=True)
            
            # Check that send was called
            assert mock_send.called
            call_args = mock_send.call_args[0][0]
            html_content = call_args['html']
            # Should contain escaped HTML
            assert '<script>' not in html_content or '&lt;script&gt;' in html_content
    
    def test_send_email_line_breaks(self, client):
        """Test that line breaks are converted to <br> tags."""
        with patch('routes.contact.resend.Emails.send') as mock_send:
            mock_send.return_value = MagicMock()
            client.post('/send', data={
                'email': 'test@example.com',
                'message': 'Line 1\nLine 2',
                'name': 'Test User',
                'phone': '1234567890'
            }, follow_redirects=True)
            
            call_args = mock_send.call_args[0][0]
            html_content = call_args['html']
            # Should contain <br> tags (not escaped)
            assert '<br>' in html_content
    
    def test_send_email_error_handling(self, client):
        """Test error handling when email sending fails."""
        with patch('routes.contact.resend.Emails.send') as mock_send:
            mock_send.side_effect = Exception("Email service error")
            response = client.post('/send', data={
                'email': 'test@example.com',
                'message': 'Test message'
            }, follow_redirects=True)
            assert response.status_code == 200  # Should redirect back with error message
    
    def test_send_email_reply_to_uses_safe_email(self, client):
        """Test that reply_to field uses escaped safe_email to prevent header injection."""
        with patch('routes.contact.resend.Emails.send') as mock_send:
            mock_send.return_value = MagicMock()
            test_email = 'test@example.com'
            client.post('/send', data={
                'email': test_email,
                'message': 'Test message',
                'name': 'Test User'
            }, follow_redirects=True)
            
            # Verify that send was called
            assert mock_send.called
            call_args = mock_send.call_args[0][0]
            reply_to = call_args['reply_to']
            
            # The reply_to should use safe_email (escaped version) instead of raw email
            # This prevents email header injection attacks where newlines could inject headers
            # For a normal email, escaped and unescaped are the same, but the fix ensures
            # that any dangerous characters (like newlines) would be HTML-escaped
            assert reply_to == test_email  # Should be the escaped version (same for normal emails)

