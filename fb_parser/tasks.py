import datetime
import json
import logging
from datetime import timedelta

import requests
from django.db.models import Q
from django.utils import timezone
from concurrent.futures.thread import ThreadPoolExecutor

from core import models
from core.models import WorkCred
from fb_parser.bot.bot import get_session, check_accounts
from fb_parser.celery.celery import app
from fb_parser.parser_data.data import search, parallel_parse_post
from fb_parser.utils.find_data import update_time_timezone

logger = logging.getLogger(__file__)


@app.task
def start_parsing_by_keyword():
    network_id = 8
    print('start')
    pool_source = ThreadPoolExecutor(10)
    select_sources = models.Sources.objects.filter(
        Q(retro_max__isnull=True) | Q(retro_max__gte=timezone.now()), published=1,
        status=1)
    if not select_sources.exists():
        return
    key_source = models.KeywordSource.objects.filter(source_id__in=list(select_sources.values_list('id', flat=True)))

    key_words = models.Keyword.objects.filter(network_id=network_id, enabled=1, taken=0,
                                              id__in=list(key_source.values_list('keyword_id', flat=True))
                                              ).order_by('last_modified')
    for key_word in key_words:
        try:
            if key_word is not None:
                select_source = select_sources.get(id=key_source.filter(keyword_id=key_word.id).first().source_id)
                last_update = key_word.last_modified
                time = select_source.sources
                if time is None:
                    time = 0
                print('time')
                if last_update is None or (last_update + datetime.timedelta(minutes=time) <
                                           update_time_timezone(timezone.localtime())):
                    print('get get_session')
                    work_credit, proxy, session, fb_dtsg, user_id, xs, token = get_session()
                    print("1")
                    if fb_dtsg is not None:
                        key_word.taken = 1
                        key_word.save()
                        pool_source.submit(search, work_credit, session, proxy, fb_dtsg, user_id, xs, token, key_word)
        except Exception as e:
            logger.error(e)
            print(e)
            try:
                pass
                # stop_session()
            except Exception as e:
                print(e)
            try:
                key_word.taken = 0
                key_word.save()
            except Exception:
                pass


# @app.task
# def start_search_posts():
#     # todo get key
#     key = 'Тест'
#     session, fb_dtsg, user_id, xs, token = get_session()
#     print("1")
#     if fb_dtsg is not None:
#         print("2")
#         result = search(session, fb_dtsg, user_id, xs, token, key, cursor=None, urls=[], result=[])
#         posts = []
#         for res in result:
#             data_url = res.split('&')
#             try:
#
#                 posts.append(models.Post(id=int(data_url[0]),
#                                          group_id=int(data_url[1])))
#             except Exception as e:
#                 print(e)
#         print("ok")
#         models.Post.objects.bulk_create(posts, batch_size=BATCH_SIZE, ignore_conflicts=True)
#     # stop session
#     # TASK OK OR NOT!

@app.task
def start_first_update_posts():
    pool_source = ThreadPoolExecutor(15)
    print("start")
    posts = models.Post.objects.filter(last_modified__lte=datetime.datetime.now(),
                                       taken=0).order_by('found_date')[:100]
    print("posts")
    for post in posts:
        print(post)
        try:
            if post is not None:
                # todo get proxy
                # parallel_parse_post(post)
                pool_source.submit(parallel_parse_post, post)
        except Exception as e:
            logger.error(e)
            print(e)
            # try:
            #     stop_proxy(proxy)
            # except Exception as e:
            #     logger.warning(e)
            print('post bad')
            post.taken = 0
            post.save()


@app.task
def add_work_credential():
    account_work_ids = models.WorkCred.objects.filter().values_list('account_id', flat=True)
    account_work = models.Account.objects.filter(available=True, banned=False).exclude(id__in=account_work_ids)
    for account in account_work:
        check_accounts(account, attempt=0)


@app.task
def add_proxy():
    print("update_proxy")
    # key = models.Keys.objects.all().first().proxykey
    key = 'd73007770373106ac0256675c604bc22'
    new_proxy = requests.get("https://api.best-proxies.ru/proxylist.json?key=%s&twitter=1&type=http&speed=1" % key,
                             timeout=60)

    proxies = []
    for proxy in json.loads(new_proxy.text):
        ip = proxy['ip']
        port = proxy['port']
        if not models.AllProxy.objects.filter(ip=ip, port=port).exists():
            proxies.append(models.AllProxy(ip=ip, port=port, login="test", proxy_password="test", last_used=timezone.now(),
                                           failed=0, errors=0, foregin=0, banned_fb=0, banned_y=0, banned_tw=0,
                                           valid_untill=timezone.now() + timedelta(days=3), v6=0, last_modified=timezone.now(),
                                           checking=0

                                           ))
    models.AllProxy.objects.bulk_create(proxies, batch_size=200, ignore_conflicts=True)
