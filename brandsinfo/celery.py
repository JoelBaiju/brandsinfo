import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brandsinfo.settings')

app = Celery('communications')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Configure beat schedule
app.conf.beat_schedule = {
    'send-events-every-second': {
        'task': 'communications.tasks.QueuedEventPublisher.send_events',
        'schedule': 1.0,  # Every second
        'options': {'expires': 30}  # Prevent task pile-up
    },
}

app.autodiscover_tasks()