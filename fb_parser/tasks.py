import datetime

from django.db.models import Q
from django.utils import timezone
from concurrent.futures.thread import ThreadPoolExecutor

from core import models
from fb_parser.bot.bot import get_session
from fb_parser.celery.celery import app
from fb_parser.parser_data.data import search, parallel_parse_post
from fb_parser.utils.find_data import update_time_timezone


@app.task
def start_parsing_by_keyword():
    network_id = 1
    pool_source = ThreadPoolExecutor(10)
    select_sources = models.Sources.objects.filter(
        Q(retro_max__isnull=True) | Q(retro_max__gte=timezone.now()), published=1,
        status=1)
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
                if last_update is None or (last_update + datetime.timedelta(minutes=time) <
                                           update_time_timezone(timezone.localtime())):
                    work_credit, proxy, session, fb_dtsg, user_id, xs, token = get_session()
                    print("1")
                    if fb_dtsg is not None:
                        key_word.taken = 1
                        key_word.save()
                        pool_source.submit(search, work_credit, proxy, session, fb_dtsg, user_id, xs, token, key_word.keyword)
        except Exception as e:
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


def start_first_update_posts():
    pool_source = ThreadPoolExecutor(15)
    posts = models.Post.objects.filter(last_modified__lte=datetime.date(2000, 1, 1),
                                       taken=0).order_by('found_date')

    for post in posts:
        try:
            if post is not None:
                # todo get proxy
                pool_source.submit(parallel_parse_post, post)
        except Exception as e:
            print(e)
            # try:
            #     stop_proxy(proxy)
            # except Exception as e:
            #     logger.warning(e)
            post.taken = 0
            post.save()


