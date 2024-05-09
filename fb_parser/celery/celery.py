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
    # 'start_first_update_posts': {
    #     'task': 'fb_parser.tasks.start_first_update_posts',
    #     # 'schedule': crontab(minute='*/10')
    #     'schedule': crontab(minute='*/37')
    #
    # },
    # 'start_parsing_by_keyword': {
    #     'task': 'fb_parser.tasks.start_parsing_by_keyword',
    #     'schedule': crontab(minute='*/5')
    #     # 'schedule': crontab(minute='*/47')
    #
    # },
    'start_parsing_by_source': {
        'task': 'fb_parser.tasks.start_parsing_by_source',
        'schedule': crontab(minute='*/5')
    },
    # 'update_proxy': {
    #     # 'task': 'fb_parser.tasks.add_proxy',
    #     'task': 'fb_parser.tasks.update_proxy',
    #     # 'schedule': crontab(minute='*/4')
    #     'schedule': crontab(minute='*/29')
    #
    # },
    #
    # 'check_not_available_accounts': {
    #     'task': 'fb_parser.tasks.check_not_available_accounts',
    #     'schedule': crontab(
    #         minute='*/35')
    #     # minute = '*/5')

}
