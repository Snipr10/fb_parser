import multiprocessing
import random
import time

import threading

from django.utils import timezone

import os

from django.db.models import Q

BOT = None

Task = []


def new_process_key(i, special_group=False):
    for i in range(2):
        time.sleep(random.randint(3, 9))

        print(f"multiprocessing {i}")
        x = multiprocessing.Process(target=start_parsing_by_keyword_while, args=(special_group, ))
        x.start()


def start_parsing_by_keyword_while(special_group=False):
    while True:
        try:
            start_parsing_by_keyword(special_group)
        except Exception as e:
            print(e)
            time.sleep(5 * 60)


def new_process_source(i, special_group=False):
    for i in range(2):
        time.sleep(random.randint(3, 9))

        print(f"multiprocessing {i}")
        x = multiprocessing.Process(target=start_parsing_by_source_while, args=(special_group,))
        x.start()


def new_process_account_item(i):
    x = multiprocessing.Process(target=start_parsing_account_source_while, args=())
    x.start()


def start_parsing_by_source_while(special_group=False):
    print(special_group)
    while True:
        try:
            start_parsing_by_source(special_group)
        except Exception as e:
            print(e)
            time.sleep(5 * 60)


def start_parsing_account_source_while():
    print("start_parsing_account_source_while")
    while True:
        try:
            start_parsing_account_source()
            time.sleep(60)
        except Exception as e:
            print(e)
            time.sleep(5 * 60)


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
    from core.models import Account, Keyword, Sources, SourcesItems
    from fb_parser.tasks import start_parsing_by_keyword, start_parsing_by_source, start_parsing_account_source
    from fb_parser.utils.find_data import update_time_timezone
    import datetime
    from fb_parser.settings import network_id

    x = threading.Thread(target=new_process_account_item, args=(0, ))
    x.start()
    #
    # for i in range(2):
    #     time.sleep(10)
    #     print("thread new_process_source " + str(i))
    #     x = threading.Thread(target=new_process_source, args=(i, True,))
    #     x.start()
    #
    # for i in range(2):
    #     time.sleep(10)
    #     print("thread new_process_source " + str(i))
    #     x = threading.Thread(target=new_process_source, args=(i, False,))
    #     x.start()
    #
    # for i in range(2):
    #     time.sleep(10)
    #     print("thread new_process_key " + str(i))
    #     x = threading.Thread(target=new_process_key, args=(i, False,))
    #     x.start()
    #
    # for i in range(2):
    #     time.sleep(10)
    #     print("thread new_process_key " + str(i))
    #     x = threading.Thread(target=new_process_key, args=(i, True,))
    #     x.start()
    #
    #
    # i = 1
    # while True:
    #     i += 1
    #     time.sleep(180)
    #     try:
    #         django.db.close_old_connections()
    #         try:
    #             Account.objects.filter(taken=1,
    #                                    last_parsing__lte=update_time_timezone(
    #                                        timezone.now() - datetime.timedelta(minutes=60)),
    #                                    ).update(taken=0, banned=0)
    #         except Exception as e:
    #             print(e)
    #         try:
    #             if i == 100:
    #                 try:
    #                     Keyword.objects.filter(network_id=network_id, enabled=1, taken=1).update(taken=0)
    #                 except Exception as e:
    #                     print(e)
    #                 try:
    #                     Sources.objects.filter(network_id=network_id, taken=1).update(taken=0)
    #                 except Exception as e:
    #                     print(e)
    #                 i = 0
    #         except Exception as e:
    #             print(e)
    #         try:
    #             select_sources = Sources.objects.filter(status=0)
    #             sources_item = SourcesItems.objects.filter(network_id=3, disabled=0, taken=0,
    #                                                        last_modified__isnull=False,
    #                                                        source_id__in=list(
    #                                                            select_sources.values_list('id', flat=True))
    #                                                        )
    #             sources_item.update(disabled=1)
    #         except Exception as e:
    #             print(e)
    #     except Exception as e:
    #         print(e)


