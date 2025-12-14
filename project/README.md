# Pomodoro Task Manager

#### Video Demo: <URL HERE>

#### Description:

Pomodoro Task Manager is a web-based productivity application that combines task management with the popular Pomodoro Technique for time management. Built using Python, Flask, and SQLite, this application helps users stay focused and organized by allowing them to create, manage, and track tasks while using timed work sessions to boost productivity.

## Why This Project?

As a student, I often struggled with managing my time effectively while working on multiple assignments and projects. I discovered the Pomodoro Technique, a time management method that uses 25-minute focused work sessions followed by short breaks. However, I found it difficult to combine this technique with my task lists, often losing track of which tasks I had worked on and for how long. This project was born from the desire to create a unified solution that brings together task management and time tracking in one seamless application.

## Features

### User Authentication
The application includes a complete user authentication system with registration and login functionality. Passwords are securely hashed using Werkzeug's security functions before being stored in the database. Each user has their own private space for tasks and statistics, ensuring data privacy and personalized experience.

### Task Management
Users can create, edit, and delete tasks with various attributes:
- **Title and Description**: Clear identification of what needs to be done
- **Priority Levels**: Tasks can be marked as low, medium, or high priority, with visual indicators (color-coded badges) to help users identify urgent items at a glance
- **Deadlines**: Optional due dates can be set for tasks, and the application sorts tasks with upcoming deadlines first
- **Completion Status**: Tasks can be marked as complete with a single click, providing immediate visual feedback

The tasks page includes filtering capabilities, allowing users to view only pending tasks, only completed tasks, or filter by priority level. This makes it easy to focus on what matters most.

### Pomodoro Timer
The heart of the application is the Pomodoro timer, implemented entirely in JavaScript for a smooth, real-time countdown experience. Key features include:
- **Configurable Duration**: Users can choose between 25-minute (standard Pomodoro) or 50-minute (extended focus) sessions
- **Task Association**: Before starting a timer, users can optionally link the session to a specific task, making it easy to track time spent on different activities
- **Start, Pause, and Reset Controls**: Full control over the timer with intuitive button controls
- **Audio Notification**: When a Pomodoro session completes, an audio alert plays to notify the user
- **Browser Notifications**: The application requests permission to send browser notifications, providing alerts even when the tab is not in focus

Each completed Pomodoro session is automatically saved to the database, creating a detailed record of productive time.

### Statistics Dashboard
Understanding productivity patterns is crucial for improvement. The statistics page provides:
- **Daily Summary**: Number of Pomodoros completed today and tasks finished
- **Weekly Overview**: A bar chart showing Pomodoros completed each day of the past week, built with Chart.js
- **Focus Time Tracking**: Total hours and minutes spent in focused work sessions
- **Task Completion Rate**: A doughnut chart showing the ratio of completed to pending tasks
- **Daily Breakdown Table**: A detailed table showing each day's productivity with progress bars

## Technical Implementation

### File Structure

- **app.py**: The main Flask application containing all route handlers for authentication, task management, Pomodoro sessions, and statistics. It handles form validation, database operations, and session management.

- **models.py**: Defines the SQLAlchemy ORM models for the three main database tables: Users (for authentication), Tasks (for task management), and Pomodoros (for tracking work sessions). Each model includes appropriate relationships and default values.

- **helpers.py**: Contains utility functions, primarily the `login_required` decorator that protects routes requiring authentication by checking for a valid session.

- **templates/**: Contains Jinja2 HTML templates that extend a base layout. The layout includes the navigation bar, flash message display, and footer. Individual templates handle specific pages like login, registration, dashboard, tasks list, task forms, and statistics.

- **static/css/styles.css**: Custom CSS styles that complement Bootstrap 5, including the timer display styling, card hover effects, responsive adjustments, and custom scrollbar styling.

- **static/js/pomodoro.js**: JavaScript code for the Pomodoro timer functionality, handling the countdown logic, button interactions, API calls to save sessions, and browser notifications.

- **tests/**: Contains Pytest test files for both models and routes, ensuring the application functions correctly.

### Design Decisions

I chose Flask for this project because of its simplicity and the solid foundation provided by CS50's Finance problem set. SQLAlchemy was selected as the ORM to provide a clean, Pythonic way to interact with the SQLite database while avoiding raw SQL queries and potential injection vulnerabilities.

For the frontend, I used Bootstrap 5 for rapid UI development with a professional appearance. Chart.js was chosen for statistics visualization due to its simplicity and beautiful default styling.

The Pomodoro timer was implemented in JavaScript rather than server-side to provide real-time updates without requiring constant server requests. This approach also allows the timer to continue running even if the network connection is temporarily lost.

## Getting Started

1. Navigate to the project directory: `cd project`
2. Create a virtual environment: `uv venv`
3. Install dependencies: `uv pip install -r requirements.txt`
4. Run the application: `uv run flask run --debug`
5. Open http://127.0.0.1:5000 in your browser

## Future Improvements

Potential features for future development include:
- Break timer after Pomodoros
- Task categories/tags
- Data export functionality
- Mobile app version
- Team collaboration features

---

This project was developed as the final project for CS50x 2025. AI tools (Claude Code) were used as a coding assistant during development.
