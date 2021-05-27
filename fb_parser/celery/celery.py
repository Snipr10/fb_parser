import os
from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fb_parser.settings')

import django

django.setup()

app = Celery('fb_parser', include=['fb_parser.tasks'])
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'start_search_posts': {
        'task': 'fb_parser.tasks.start_search_posts',
        'schedule': crontab(minute='*/5')
    },
}
