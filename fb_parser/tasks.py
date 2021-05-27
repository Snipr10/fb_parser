import datetime
from core import models
from fb_parser.bot.bot import get_session
from fb_parser.celery.celery import app
from fb_parser.parser_data.data import get_data, search
from fb_parser.settings import BATCH_SIZE


@app.task
def start_search_posts():
    # todo get key
    key = 'Тест'
    session, fb_dtsg, user_id, xs, token = get_session()
    if fb_dtsg is not None:
        result = search(session, fb_dtsg, user_id, xs, token, key, cursor=None, urls=[], result=[])
        posts = []
        for res in result:
            data_url = res.split('&amp;')
            posts.append(models.Post(id=data_url[1], group_id=data_url[0]))
        models.Post.objects.bulk_create(posts, batch_size=BATCH_SIZE, ignore_conflicts=True)
    # stop session
    # TASK OK OR NOT!


def start_update_posts():
    # todo get key
    post = models.Post.objects.filter(last_parsing__lte=datetime.date(2000, 1, 1),
                                                taken=0).order_by('found_date').last()
    if post is not None:


