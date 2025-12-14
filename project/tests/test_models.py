"""
Tests for database models.
"""

import pytest
from datetime import datetime, date

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, Task, Pomodoro


@pytest.fixture
def client():
    """Create test client and database."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def sample_user(client):
    """Create a sample user for testing."""
    with app.app_context():
        user = User(
            username='testuser',
            password_hash='hashed_password'
        )
        db.session.add(user)
        db.session.commit()
        return user.id


class TestUserModel:
    """Tests for User model."""

    def test_create_user(self, client):
        """Test creating a new user."""
        with app.app_context():
            user = User(
                username='newuser',
                password_hash='password123'
            )
            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.username == 'newuser'

    def test_username_unique(self, client, sample_user):
        """Test that usernames must be unique."""
        with app.app_context():
            duplicate_user = User(
                username='testuser',
                password_hash='another_password'
            )
            db.session.add(duplicate_user)

            with pytest.raises(Exception):
                db.session.commit()


class TestTaskModel:
    """Tests for Task model."""

    def test_create_task(self, client, sample_user):
        """Test creating a new task."""
        with app.app_context():
            task = Task(
                user_id=sample_user,
                title='Test Task',
                description='A test task',
                priority='high'
            )
            db.session.add(task)
            db.session.commit()

            assert task.id is not None
            assert task.title == 'Test Task'
            assert task.completed is False

    def test_task_default_priority(self, client, sample_user):
        """Test default priority is medium."""
        with app.app_context():
            task = Task(
                user_id=sample_user,
                title='Task with default priority'
            )
            db.session.add(task)
            db.session.commit()

            assert task.priority == 'medium'

    def test_task_with_deadline(self, client, sample_user):
        """Test task with deadline."""
        with app.app_context():
            deadline = date(2025, 12, 31)
            task = Task(
                user_id=sample_user,
                title='Task with deadline',
                deadline=deadline
            )
            db.session.add(task)
            db.session.commit()

            assert task.deadline == deadline


class TestPomodoroModel:
    """Tests for Pomodoro model."""

    def test_create_pomodoro(self, client, sample_user):
        """Test creating a pomodoro session."""
        with app.app_context():
            pomodoro = Pomodoro(
                user_id=sample_user,
                duration=25
            )
            db.session.add(pomodoro)
            db.session.commit()

            assert pomodoro.id is not None
            assert pomodoro.duration == 25
            assert pomodoro.completed is False

    def test_pomodoro_with_task(self, client, sample_user):
        """Test pomodoro linked to task."""
        with app.app_context():
            task = Task(user_id=sample_user, title='Task for pomodoro')
            db.session.add(task)
            db.session.commit()

            pomodoro = Pomodoro(
                user_id=sample_user,
                task_id=task.id,
                duration=25
            )
            db.session.add(pomodoro)
            db.session.commit()

            assert pomodoro.task_id == task.id
