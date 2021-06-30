import datetime
import json
import logging
from datetime import timedelta
import random

import requests
from django.db.models import Q
from django.utils import timezone
from concurrent.futures.thread import ThreadPoolExecutor

from core import models
from core.models import WorkCred
from fb_parser.bot.bot import get_session, check_accounts
from fb_parser.celery.celery import app
from fb_parser.parser_data.data import search, parallel_parse_post
from fb_parser.settings import network_id
from fb_parser.utils.find_data import update_time_timezone
from fb_parser.utils.proxy import generate_proxy_session, check_facebook_url

logger = logging.getLogger(__file__)


@app.task
def start_parsing_by_keyword():
    print('start')
    pool_source = ThreadPoolExecutor(10)
    select_sources = models.Sources.objects.filter(
        Q(retro_max__isnull=True) | Q(retro_max__gte=timezone.now()), published=1,
        status=1)
    if not select_sources.exists():
        return
    key_source = models.KeywordSource.objects.filter(source_id__in=list(select_sources.values_list('id', flat=True)))
    # delete id
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
                if last_update is None or (last_update + datetime.timedelta(minutes=time) <
                                           update_time_timezone(timezone.localtime())):
                    print('get get_session')
                    print(key_word.keyword)
                    work_credit, proxy, session, fb_dtsg, user_id, xs, token = get_session()
                    if fb_dtsg is not None:
                        key_word.taken = 1
                        key_word.save()
                        search(work_credit, session, proxy, fb_dtsg, user_id, xs, token, key_word)
                        # pool_source.submit(search, work_credit, session, proxy, fb_dtsg, user_id, xs, token, key_word)
                    else:
                        if work_credit is not None:
                            work_credit.delete()
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
    posts = models.Post.objects.filter(id=195972819052075, last_modified__lte=datetime.date(2000, 1, 1),
                                       taken=0).order_by('found_date')[:100]
    print("posts")
    print(posts)
    for post in posts:
        post.taken = 1
        post.save()
        print(post.id)
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
        print(ip)
        print(port)
        if not models.AllProxy.objects.filter(ip=ip, port=port).exists():
            proxies.append(models.AllProxy(ip=ip, port=port, login="test", proxy_password="test", last_used=timezone.now(),
                                           failed=0, errors=0, foregin=0, banned_fb=0, banned_y=0, banned_tw=0,
                                           valid_untill=timezone.now() + timedelta(days=3), v6=0, last_modified=timezone.now(),
                                           checking=0

                                           ))
    models.AllProxy.objects.bulk_create(proxies, batch_size=200, ignore_conflicts=True)


@app.task
def update_proxy():
    print("update_proxy")
    # key = models.Keys.objects.all().first().proxykey
    key = 'd73007770373106ac0256675c604bc22'

    new_proxy = requests.get(
        "https://api.best-proxies.ru/proxylist.json?key=%s&twitter=1&type=http,https&speed=1,2" % key,
        timeout=60)

    proxies = []
    limit = 0
    for proxy in json.loads(new_proxy.text):
        host = proxy['ip']
        port = proxy['port']
        print(host)
        print(port)

        session = generate_proxy_session('test', 'test', host, port)
        if not models.AllProxy.objects.filter(ip=host, port=port).exists():
            if check_facebook_url(session):
                if port == '8080':
                    if check_proxy_available_for_facebook(session):
                        proxies.append(models.AllProxy(ip=host, port=port, login="test", proxy_password="test",
                                                       last_used=timezone.now(),
                                                       failed=0, errors=0, foregin=0, banned_fb=0, banned_y=0,
                                                       banned_tw=0,
                                                       valid_untill=timezone.now() + timedelta(days=3), v6=0,
                                                       last_modified=timezone.now(),
                                                       checking=0
                                                       ))
                        # models.Proxy.objects.create(host=host, port=port, login="test", password="test")
                else:
                    proxies.append(models.AllProxy(ip=host, port=port, login="test", proxy_password="test",
                                                   last_used=timezone.now(),
                                                   failed=0, errors=0, foregin=0, banned_fb=0, banned_y=0,
                                                   banned_tw=0,
                                                   valid_untill=timezone.now() + timedelta(days=3), v6=0,
                                                   last_modified=timezone.now(),
                                                   checking=0

                                                   ))


def check_proxy_available_for_facebook(session):
    try:
        accounts = models.Account.objects.filter(banned=False).order_by('id')[:500]
        account = random.choice(accounts)
        # login = "+79910404158"
        # password = "yBZHsBZHou761"
        print(account.id)
        response = session.post('https://m.facebook.com/login.php', data={
            'email': account.login,
            'pass': account.password,
            # 'email': login,
            # 'pass': password
        }, allow_redirects=False, timeout=10)
        start_page = session.get('https://www.facebook.com/', timeout=10)
        print(start_page)
        if 'login/?privacy_mutation_token' in start_page.url:
            account.banned = True
            account.save()
            return check_proxy_available_for_facebook(session)
        if 'checkpoint' not in start_page.url and '/login/device-based/regulr/' not in start_page.url:
            print(str(account.id) + " ok")
            return True
    except Exception as e:
        print(e)
        pass
    print(str(account.id) + " bad")
    return False


@app.task
def check_not_available_accounts():
    for account in models.Account.objects.filter().order_by("-id")[:500]:
        if not models.WorkCred.objects.filter(account_id=account.id).exists():
            check_accounts(account, attempt=0)