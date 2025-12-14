"""
Tests for Flask routes.
"""

import pytest
from werkzeug.security import generate_password_hash

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Task


@pytest.fixture
def client():
    """Create test client and database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def authenticated_client(client):
    """Create authenticated test client."""
    with app.app_context():
        user = User(
            username='testuser',
            password_hash=generate_password_hash('password123')
        )
        db.session.add(user)
        db.session.commit()

    # Login
    client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })

    return client


class TestAuthRoutes:
    """Tests for authentication routes."""

    def test_login_page_loads(self, client):
        """Test login page loads correctly."""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Sign in' in response.data

    def test_register_page_loads(self, client):
        """Test register page loads correctly."""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Create Account' in response.data

    def test_register_new_user(self, client):
        """Test registering a new user."""
        response = client.post('/register', data={
            'username': 'newuser',
            'password': 'password123',
            'confirmation': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Registration successful' in response.data

    def test_register_password_mismatch(self, client):
        """Test registration with mismatched passwords."""
        response = client.post('/register', data={
            'username': 'newuser',
            'password': 'password123',
            'confirmation': 'different'
        })

        assert b'Passwords do not match' in response.data

    def test_login_success(self, client):
        """Test successful login."""
        # First register
        client.post('/register', data={
            'username': 'testuser',
            'password': 'password123',
            'confirmation': 'password123'
        })

        # Then login
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Welcome back' in response.data

    def test_login_wrong_password(self, client):
        """Test login with wrong password."""
        # First register
        client.post('/register', data={
            'username': 'testuser',
            'password': 'password123',
            'confirmation': 'password123'
        })

        # Try wrong password
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })

        assert b'Invalid username or password' in response.data

    def test_logout(self, authenticated_client):
        """Test logout functionality."""
        response = authenticated_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'logged out' in response.data


class TestTaskRoutes:
    """Tests for task management routes."""

    def test_tasks_page_requires_login(self, client):
        """Test that tasks page requires authentication."""
        response = client.get('/tasks', follow_redirects=True)
        assert b'Sign in' in response.data

    def test_tasks_page_loads(self, authenticated_client):
        """Test tasks page loads for authenticated user."""
        response = authenticated_client.get('/tasks')
        assert response.status_code == 200
        assert b'My Tasks' in response.data

    def test_create_task(self, authenticated_client):
        """Test creating a new task."""
        response = authenticated_client.post('/tasks/add', data={
            'title': 'New Test Task',
            'description': 'A test description',
            'priority': 'high'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'Task created successfully' in response.data
        assert b'New Test Task' in response.data

    def test_create_task_without_title(self, authenticated_client):
        """Test creating task without title fails."""
        response = authenticated_client.post('/tasks/add', data={
            'title': '',
            'priority': 'medium'
        })

        assert b'Task title is required' in response.data


class TestDashboard:
    """Tests for dashboard."""

    def test_dashboard_requires_login(self, client):
        """Test dashboard requires authentication."""
        response = client.get('/', follow_redirects=True)
        assert b'Sign in' in response.data

    def test_dashboard_loads(self, authenticated_client):
        """Test dashboard loads for authenticated user."""
        response = authenticated_client.get('/')
        assert response.status_code == 200
        assert b'Pomodoro Timer' in response.data
