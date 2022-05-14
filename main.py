import json
import multiprocessing
import random
import time

from concurrent.futures.thread import ThreadPoolExecutor
import threading
import concurrent

import telebot
from django.utils import timezone

import os

from django.db.models import Q, F
from facebook_scraper import FacebookScraper
from requests.cookies import cookiejar_from_dict

BOT = None

Task = []

if __name__ == '__main__':

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fb_parser.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    print(1)
    import django

    django.setup()

    futures = []
    #
    # x = threading.Thread(target=update_, args=(0,))
    # x.start()
    from core.models import Account
    from fb_parser.tasks import start_parsing_by_keyword, start_parsing_by_source

    while True:
        try:
            start_parsing_by_keyword()
            start_parsing_by_source()
            Account.objects.all().update(taken=0)
        except Exception as e:
            print(e)
    # a = Account.objects.get(id=321)
    # print(a)
    # print(a.cookie)
    # json.loads(a.cookie)
    # print(json.loads(a.cookie))
    # face = FacebookScraper()
    # face.session.cookies.update(cookiejar_from_dict(json.loads(a.cookie)))
    # # face.login("100081198725298", "howardsxfloyd271")
    # face.set_proxy('http://{}:{}@{}:{}'.format("franz_allan+dev_mati", "13d9bb5825", "85.31.49.213", "30001"))
    # for z in face.get_posts_by_search("авто"):
    #     print(z)


    a = Account.objects.get(id=321)
    print(a)
    print(a.cookie)
    json.loads(a.cookie)
    print(json.loads(a.cookie))
