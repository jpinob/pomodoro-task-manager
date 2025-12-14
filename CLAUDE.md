# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Pomodoro Task Manager** - A web application for managing tasks with an integrated Pomodoro timer, built as CS50x 2025 Final Project.

### Tech Stack
- **Backend**: Flask + SQLite (SQLAlchemy ORM)
- **Frontend**: HTML/CSS/JS + Bootstrap 5
- **Charts**: Chart.js
- **Package Manager**: UV (Python)

## Project Structure

```
project/
├── app.py              # Flask routes and main application
├── models.py           # SQLAlchemy models (User, Task, Pomodoro)
├── helpers.py          # Utility functions (login_required decorator)
├── requirements.txt    # Python dependencies
├── static/
│   ├── css/styles.css  # Custom styles
│   └── js/pomodoro.js  # Timer JavaScript logic
├── templates/          # Jinja2 HTML templates
└── tests/              # Pytest test files
```

## Development Commands

```bash
# Navigate to project directory
cd project

# Create virtual environment (first time)
uv venv

# Install dependencies
uv pip install -r requirements.txt

# Run development server
uv run flask run --debug

# Run tests
uv run pytest tests/ -v
```

## Database Schema

- **users**: id, username, password_hash, created_at
- **tasks**: id, user_id, title, description, priority, deadline, completed, created_at
- **pomodoros**: id, user_id, task_id, duration, completed, started_at

## Key Features

1. **Authentication**: User registration/login with password hashing
2. **Task Management**: CRUD operations, priority levels, deadlines, filters
3. **Pomodoro Timer**: 25/50 min sessions, pause/resume, linked to tasks
4. **Statistics**: Daily/weekly charts, focus time tracking

## CS50 Submission Requirements

1. **Video Demo**: Max 3 minutes on YouTube (can be unlisted)
2. **README.md**: Project description (~750 words minimum)
3. **Submit**: `submit50 cs50/problems/2025/x/project`
