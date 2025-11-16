# Flask Lookbook

A modern Flask web application for HNF Prints, built with Python 3.14, featuring authentication, contact forms, and comprehensive testing.

## Features

- 🔐 User authentication (login, registration, logout)
- 📧 Contact form with email integration (Resend)
- 🎨 Responsive design with Bootstrap
- 🧪 Comprehensive test suite with pytest
- 🔒 Security best practices (HTML escaping, secure sessions)
- 📝 Detailed code comments for learning
- 🛠️ Modern development tooling (Ruff, MyPy, Bandit)

## Tech Stack

- **Python**: 3.14.0 (managed via mise)
- **Web Framework**: Flask 3.1.2
- **Database**: MySQL (mysql-connector-python)
- **Email**: Resend
- **Testing**: pytest, pytest-cov, pytest-xdist
- **Code Quality**: Ruff, MyPy, Bandit, Safety

## Prerequisites

- Python 3.14.0 (recommended: use [mise](https://mise.jdx.dev/) for version management)
- MySQL database
- Resend API key (for email functionality)

## Installation

### Using mise (Recommended)

```bash
# Install mise if not already installed
curl https://mise.run | sh

# Navigate to project directory
cd flask-lookbook

# Install Python version and dependencies (mise handles this automatically)
mise install

# Install Python dependencies
pip install -r requirements.txt
```

### Without mise

```bash
# Ensure Python 3.14 is installed
python3.14 --version

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root with the following variables:

```env
# Required
FLASK_SECRET_KEY=your-secret-key-here

# Database Configuration
MYSQLHOST=localhost
MYSQLUSER=your_username
MYSQLPASSWORD=your_password
MYSQLDATABASE=your_database

# Email Configuration (Resend)
RESEND_API_KEY=your-resend-api-key

# Optional - Base Domain (defaults to nordqvist.tech)
BASE_DOMAIN=nordqvist.tech

# Optional - Email addresses (default to info@{BASE_DOMAIN})
EMAIL_FROM=info@nordqvist.tech
EMAIL_TO=info@nordqvist.tech

# Optional - Session Security (for production)
SESSION_COOKIE_SECURE=false  # Set to "true" in production with HTTPS
```

**Important**: Never commit the `.env` file to version control!

## Running the Application

### Development Server

```bash
# Using mise
mise run python app.py

# Or directly
python app.py
```

The application will be available at `http://localhost:8080`

### Production (with Gunicorn)

```bash
gunicorn app:app
```

## Project Structure

```
flask-lookbook/
├── app.py              # Application factory (Flask app creation)
├── config.py           # Configuration management
├── database.py         # Database utilities and context managers
├── utils.py            # Shared utilities and decorators
├── routes/             # Route blueprints
│   ├── __init__.py
│   ├── auth.py        # Authentication routes
│   ├── main.py        # Main public routes
│   └── contact.py    # Contact form routes
├── templates/         # Jinja2 templates
│   ├── layout.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── contact.html
│   ├── about.html
│   ├── inspiration.html
│   └── admin.html
├── static/            # Static files (CSS, images, JS)
├── tests/             # Test suite
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_main.py
│   ├── test_contact.py
│   ├── test_config.py
│   ├── test_database.py
│   └── test_utils.py
├── requirements.txt   # Python dependencies
├── pyproject.toml    # Project configuration (Ruff, MyPy, pytest)
├── mise.toml         # Mise environment configuration
├── .cursorrules      # Cursor IDE guidelines
└── README.md         # This file
```

## Development

### Code Quality Tools

The project uses several tools to maintain code quality:

- **Ruff**: Fast Python linter and formatter
- **MyPy**: Static type checking
- **Bandit**: Security vulnerability scanning
- **Safety**: Dependency vulnerability checking

### Running Code Quality Checks

```bash
# Format code
make format
# or
ruff format .

# Check linting
make lint
# or
ruff check .

# Type checking
make type-check
# or
mypy . --config-file mypy.ini

# Security scan
make security
# or
bandit -r . -c .bandit

# Run all checks
make check
```

See `Makefile` for all available commands.

### Pre-commit Hooks

Install pre-commit hooks to automatically run checks before each commit:

```bash
pip install pre-commit
pre-commit install
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run tests in parallel (faster)
pytest -n auto

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run only unit tests
pytest -m "unit"

# Skip slow tests
pytest -m "not slow"
```

### Test Structure

- `tests/conftest.py` - Shared fixtures and test configuration
- `tests/test_*.py` - Individual test modules
- Tests use mocking to avoid requiring a real database

See `tests/README.md` for more details.

## Architecture

### Application Factory Pattern

The app uses Flask's Application Factory pattern, which allows:
- Multiple app instances for testing
- Different configurations for different environments
- Better integration with WSGI servers

### Blueprints

Routes are organized into blueprints:
- `auth` - Authentication (login, register, logout)
- `main` - Public routes (home, about, inspiration, admin)
- `contact` - Contact form handling

### Configuration Management

All configuration is centralized in `config.py`:
- Uses `@property` decorators for lazy evaluation
- Reads from environment variables
- Supports class-level access via metaclass pattern

### Database

- Uses context managers for proper connection handling
- Automatic rollback on errors
- No global connections (prevents resource leaks)

## Security Features

- ✅ HTML escaping for all user input (XSS prevention)
- ✅ Secure session cookies (HTTPOnly, SameSite)
- ✅ Password hashing with Werkzeug
- ✅ Environment variable configuration (no hardcoded secrets)
- ✅ Input validation
- ✅ SQL injection prevention (parameterized queries)

## Contributing

1. Follow the code style guidelines in `.cursorrules`
2. Write tests for new features
3. Run code quality checks before committing
4. Use conventional commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `refactor:` for code refactoring
   - `test:` for test additions
   - `docs:` for documentation

## License

[Add your license here]

## Support

For questions or issues, please [create an issue](link-to-issues) or contact the maintainers.
