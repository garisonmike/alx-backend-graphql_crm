# CRM Application - Celery Setup Guide

This guide walks you through setting up Celery with Celery Beat for automated CRM report generation in the Django GraphQL CRM application.

## Overview

The CRM application uses Celery for asynchronous task processing and Celery Beat for scheduled tasks. A weekly report task runs every Monday at 6:00 AM UTC, generating statistics about customers, orders, and revenue.

## Prerequisites

- Python 3.8+
- Django 4.2+
- Redis server

## Installation Steps

### 1. Install Redis

Redis is required as the message broker for Celery.

**On Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**On macOS (using Homebrew):**
```bash
brew install redis
brew services start redis
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### 2. Install Python Dependencies

Install all required packages from requirements.txt:

```bash
pip install -r requirements.txt
```

This installs:
- Django
- graphene-django
- celery
- django-celery-beat
- redis
- And other dependencies

### 3. Run Database Migrations

Apply migrations to create necessary database tables for django-celery-beat:

```bash
python manage.py migrate
```

This creates tables for:
- Periodic tasks
- Intervals and crontabs
- Task results

## Running the Application

You need to run multiple processes for the full setup:

### Terminal 1: Django Development Server

```bash
python manage.py runserver
```

This starts the Django web server at http://localhost:8000

### Terminal 2: Celery Worker

The worker processes tasks from the queue:

```bash
celery -A crm worker -l info
```

You should see output like:
```
[tasks]
  . crm.tasks.generate_crm_report
```

### Terminal 3: Celery Beat Scheduler

The beat scheduler triggers periodic tasks:

```bash
celery -A crm beat -l info
```

You should see the scheduled task:
```
Scheduler: Sending due task generate-crm-report
```

## Verifying the Setup

### 1. Check Celery Worker Status

In the worker terminal, you should see:
```
celery@hostname ready.
```

### 2. Check Scheduled Tasks

You can verify tasks are scheduled:

```bash
python manage.py shell
```

```python
from django_celery_beat.models import PeriodicTask
print(PeriodicTask.objects.all())
```

### 3. Manually Test the Report Task

Trigger the report generation manually:

```bash
python manage.py shell
```

```python
from crm.tasks import generate_crm_report
result = generate_crm_report.delay()
print(result.get())
```

### 4. Check the Report Log

The weekly report is logged to `/tmp/crm_report_log.txt`:

```bash
cat /tmp/crm_report_log.txt
```

Expected format:
```
2025-11-04 06:00:00 - Report: 150 customers, 320 orders, 45000.00 revenue
2025-11-11 06:00:00 - Report: 165 customers, 342 orders, 48500.00 revenue
```

## Task Schedule

The CRM report generation task runs:
- **When:** Every Monday at 6:00 AM UTC
- **Task:** `crm.tasks.generate_crm_report`
- **Output:** `/tmp/crm_report_log.txt`

To modify the schedule, edit `CELERY_BEAT_SCHEDULE` in `crm/settings.py`.

## Troubleshooting

### Celery can't connect to Redis

**Error:** `Error: Cannot connect to redis://localhost:6379/0`

**Solution:**
1. Check if Redis is running: `redis-cli ping`
2. Start Redis: `sudo systemctl start redis-server`
3. Check Redis port: `sudo netstat -tlnp | grep 6379`

### Task not executing

**Possible causes:**
1. Worker not running
2. Beat scheduler not running
3. Task not registered

**Check:**
```bash
celery -A crm inspect registered
```

### No output in log file

**Check:**
1. File permissions: `ls -l /tmp/crm_report_log.txt`
2. Worker logs for errors
3. Manually run task: `generate_crm_report.delay()`

### Database locked errors

If using SQLite, consider switching to PostgreSQL for production:
```python
# In settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'crm_db',
        ...
    }
}
```

## Production Deployment

For production, use a process manager like Supervisor or systemd:

### Example systemd service for Celery Worker

Create `/etc/systemd/system/celery.service`:

```ini
[Unit]
Description=Celery Worker for CRM
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/alx-backend-graphql_crm
ExecStart=/path/to/venv/bin/celery -A crm worker -l info --detach

[Install]
WantedBy=multi-user.target
```

### Example systemd service for Celery Beat

Create `/etc/systemd/system/celerybeat.service`:

```ini
[Unit]
Description=Celery Beat Scheduler for CRM
After=network.target redis.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/alx-backend-graphql_crm
ExecStart=/path/to/venv/bin/celery -A crm beat -l info

[Install]
WantedBy=multi-user.target
```

Enable and start services:
```bash
sudo systemctl enable celery celerybeat
sudo systemctl start celery celerybeat
```

## Additional Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Django-Celery-Beat Documentation](https://django-celery-beat.readthedocs.io/)
- [Redis Documentation](https://redis.io/documentation)

## Support

For issues or questions, refer to the project documentation or contact the development team.
