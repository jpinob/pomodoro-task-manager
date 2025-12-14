"""
Pomodoro Task Manager - CS50 Final Project

A web application for managing tasks with an integrated Pomodoro timer.
"""

import os
from datetime import datetime, date, timedelta

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from dotenv import load_dotenv

from models import db, User, Task, Pomodoro
from helpers import login_required

# Load environment variables from .env file
load_dotenv()

# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pomodoro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Secure session cookie configuration
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FORCE_HTTPS', 'False').lower() == 'true'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize Talisman for security headers
# Only force HTTPS in production
force_https = os.environ.get('FORCE_HTTPS', 'False').lower() == 'true'
Talisman(
    app,
    force_https=force_https,
    content_security_policy={
        'default-src': "'self'",
        'script-src': ["'self'", 'cdn.jsdelivr.net', "'unsafe-inline'"],
        'style-src': ["'self'", 'cdn.jsdelivr.net', "'unsafe-inline'"],
        'font-src': ["'self'", 'cdn.jsdelivr.net'],
        'img-src': ["'self'", 'data:'],
    }
)

# Initialize database
db.init_app(app)

# Create tables on first run
with app.app_context():
    db.create_all()


# =============================================================================
# Authentication Routes
# =============================================================================

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirmation = request.form.get('confirmation', '')

        # Validation
        if not username:
            flash('Username is required.', 'error')
            return render_template('register.html')

        if not password:
            flash('Password is required.', 'error')
            return render_template('register.html')

        if password != confirmation:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return render_template('register.html')

        # Check if username exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists.', 'error')
            return render_template('register.html')

        # Create new user
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    session.clear()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('login.html')

        user = User.query.filter_by(username=username).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash('Invalid username or password.', 'error')
            return render_template('login.html')

        session['user_id'] = user.id
        session['username'] = user.username
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# =============================================================================
# Main Routes
# =============================================================================

@app.route('/')
@login_required
def index():
    """Dashboard with timer and recent tasks."""
    user_id = session['user_id']

    # Get pending tasks for the timer dropdown
    pending_tasks = Task.query.filter_by(
        user_id=user_id,
        completed=False
    ).order_by(Task.deadline.asc().nullslast(), Task.priority.desc()).all()

    # Get today's stats
    today = date.today()
    today_pomodoros = Pomodoro.query.filter(
        Pomodoro.user_id == user_id,
        Pomodoro.completed == True,
        db.func.date(Pomodoro.started_at) == today
    ).count()

    today_tasks_completed = Task.query.filter(
        Task.user_id == user_id,
        Task.completed == True,
        db.func.date(Task.created_at) == today
    ).count()

    return render_template(
        'index.html',
        tasks=pending_tasks,
        today_pomodoros=today_pomodoros,
        today_tasks=today_tasks_completed
    )


# =============================================================================
# Task Routes
# =============================================================================

@app.route('/tasks')
@login_required
def tasks():
    """Display all tasks with filters."""
    user_id = session['user_id']

    # Get filter parameters
    status_filter = request.args.get('status', 'pending')
    priority_filter = request.args.get('priority', 'all')

    # Base query
    query = Task.query.filter_by(user_id=user_id)

    # Apply status filter
    if status_filter == 'pending':
        query = query.filter_by(completed=False)
    elif status_filter == 'completed':
        query = query.filter_by(completed=True)

    # Apply priority filter
    if priority_filter != 'all':
        query = query.filter_by(priority=priority_filter)

    # Order by deadline (nulls last) then by priority
    tasks_list = query.order_by(
        Task.completed.asc(),
        Task.deadline.asc().nullslast(),
        Task.created_at.desc()
    ).all()

    return render_template(
        'tasks.html',
        tasks=tasks_list,
        status_filter=status_filter,
        priority_filter=priority_filter
    )


@app.route('/tasks/add', methods=['GET', 'POST'])
@login_required
def add_task():
    """Add a new task."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'medium')
        deadline_str = request.form.get('deadline', '')

        if not title:
            flash('Task title is required.', 'error')
            return render_template('task_form.html', task=None)

        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format.', 'error')
                return render_template('task_form.html', task=None)

        new_task = Task(
            user_id=session['user_id'],
            title=title,
            description=description,
            priority=priority,
            deadline=deadline
        )
        db.session.add(new_task)
        db.session.commit()

        flash('Task created successfully!', 'success')
        return redirect(url_for('tasks'))

    return render_template('task_form.html', task=None)


@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """Edit an existing task."""
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first_or_404()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'medium')
        deadline_str = request.form.get('deadline', '')

        if not title:
            flash('Task title is required.', 'error')
            return render_template('task_form.html', task=task)

        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format.', 'error')
                return render_template('task_form.html', task=task)

        task.title = title
        task.description = description
        task.priority = priority
        task.deadline = deadline
        db.session.commit()

        flash('Task updated successfully!', 'success')
        return redirect(url_for('tasks'))

    return render_template('task_form.html', task=task)


@app.route('/tasks/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    """Toggle task completion status."""
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first_or_404()
    task.completed = not task.completed
    db.session.commit()

    status = 'completed' if task.completed else 'pending'
    flash(f'Task marked as {status}.', 'success')
    return redirect(request.referrer or url_for('tasks'))


@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    """Delete a task."""
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first_or_404()
    db.session.delete(task)
    db.session.commit()

    flash('Task deleted.', 'success')
    return redirect(url_for('tasks'))


# =============================================================================
# Pomodoro Routes
# =============================================================================

@app.route('/pomodoro/start', methods=['POST'])
@login_required
def start_pomodoro():
    """Start a new pomodoro session."""
    task_id = request.form.get('task_id')
    duration = request.form.get('duration', 25, type=int)

    # Validate task belongs to user if provided
    if task_id:
        task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first()
        if not task:
            return jsonify({'error': 'Invalid task'}), 400
        task_id = task.id
    else:
        task_id = None

    pomodoro = Pomodoro(
        user_id=session['user_id'],
        task_id=task_id,
        duration=duration,
        completed=False
    )
    db.session.add(pomodoro)
    db.session.commit()

    return jsonify({'pomodoro_id': pomodoro.id, 'duration': duration})


@app.route('/pomodoro/<int:pomodoro_id>/complete', methods=['POST'])
@login_required
def complete_pomodoro(pomodoro_id):
    """Mark a pomodoro session as completed."""
    pomodoro = Pomodoro.query.filter_by(
        id=pomodoro_id,
        user_id=session['user_id']
    ).first_or_404()

    pomodoro.completed = True
    db.session.commit()

    return jsonify({'success': True})


# =============================================================================
# Statistics Routes
# =============================================================================

@app.route('/stats')
@login_required
def stats():
    """Display productivity statistics."""
    user_id = session['user_id']
    today = date.today()

    # Today's stats
    today_pomodoros = Pomodoro.query.filter(
        Pomodoro.user_id == user_id,
        Pomodoro.completed == True,
        db.func.date(Pomodoro.started_at) == today
    ).count()

    # This week's stats (last 7 days)
    week_ago = today - timedelta(days=7)
    week_pomodoros = Pomodoro.query.filter(
        Pomodoro.user_id == user_id,
        Pomodoro.completed == True,
        db.func.date(Pomodoro.started_at) >= week_ago
    ).all()

    # Calculate total focus time this week
    total_focus_minutes = sum(p.duration for p in week_pomodoros)
    total_focus_hours = total_focus_minutes // 60
    total_focus_remaining_minutes = total_focus_minutes % 60

    # Daily breakdown for chart
    daily_stats = []
    for i in range(7):
        day = today - timedelta(days=6-i)
        count = Pomodoro.query.filter(
            Pomodoro.user_id == user_id,
            Pomodoro.completed == True,
            db.func.date(Pomodoro.started_at) == day
        ).count()
        daily_stats.append({
            'date': day.strftime('%a'),
            'count': count
        })

    # Task stats
    total_tasks = Task.query.filter_by(user_id=user_id).count()
    completed_tasks = Task.query.filter_by(user_id=user_id, completed=True).count()
    pending_tasks = total_tasks - completed_tasks

    return render_template(
        'stats.html',
        today_pomodoros=today_pomodoros,
        week_pomodoros=len(week_pomodoros),
        total_focus_hours=total_focus_hours,
        total_focus_minutes=total_focus_remaining_minutes,
        daily_stats=daily_stats,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks
    )


@app.route('/api/stats/weekly')
@login_required
def api_weekly_stats():
    """API endpoint for weekly statistics (for Chart.js)."""
    user_id = session['user_id']
    today = date.today()

    daily_stats = []
    for i in range(7):
        day = today - timedelta(days=6-i)
        count = Pomodoro.query.filter(
            Pomodoro.user_id == user_id,
            Pomodoro.completed == True,
            db.func.date(Pomodoro.started_at) == day
        ).count()
        daily_stats.append({
            'date': day.strftime('%a %d'),
            'count': count
        })

    return jsonify(daily_stats)


# =============================================================================
# Run Application
# =============================================================================

if __name__ == '__main__':
    app.run(debug=True)
