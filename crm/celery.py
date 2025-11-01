import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql.settings')

# Create the Celery app instance
app = Celery('crm')

# Load configuration from Django settings with CELERY namespace
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all installed Django apps
app.autodiscover_tasks()

# Optional: Test task to verify Celery is working
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
