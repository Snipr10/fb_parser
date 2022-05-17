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


def new_process_key(i):
    for i in range(5):
        time.sleep(random.randint(3, 9))

        print(f"multiprocessing {i}")
        x = multiprocessing.Process(target=start_parsing_by_keyword, args=())
        x.start()


def new_process_source(i):
    for i in range(5):
        time.sleep(random.randint(3, 9))

        print(f"multiprocessing {i}")
        x = multiprocessing.Process(target=start_parsing_by_source, args=())
        x.start()


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

    for i in range(2):
        time.sleep(10)
        print("thread new_process_key " + str(i))
        x = threading.Thread(target=new_process_key, args=(i,))
        x.start()
    for i in range(2):
        time.sleep(10)
        print("thread new_process_source " + str(i))
        x = threading.Thread(target=new_process_source, args=(i,))
        x.start()

    # while True:
    #     try:
    #         print("start_parsing_by_source")
    #         start_parsing_by_source()
    #         print("start_parsing_by_keyword")
    #         start_parsing_by_keyword()
    #         django.db.close_old_connections()
    #     except Exception as e:
    #         print(e)
        # time.sleep(5*60)
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


