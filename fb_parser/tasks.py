import datetime
import dateutil.parser
from core import models
from fb_parser.bot.bot import get_session
from fb_parser.celery.celery import app
from fb_parser.parser_data.data import get_data, search, get_data_from_url
from fb_parser.settings import BATCH_SIZE
from fb_parser.utils.find_data import get_sphinx_id, get_md5_text


@app.task
def start_search_posts():
    # todo get key
    key = 'Тест'
    session, fb_dtsg, user_id, xs, token = get_session()
    print("1")
    if fb_dtsg is not None:
        print("2")
        result = search(session, fb_dtsg, user_id, xs, token, key, cursor=None, urls=[], result=[])
        posts = []
        for res in result:
            data_url = res.split('&')
            try:

                posts.append(models.Post(id=int(data_url[0]),
                                         group_id=int(data_url[1])))
            except Exception as e:
                print(e)
        print("ok")
        models.Post.objects.bulk_create(posts, batch_size=BATCH_SIZE, ignore_conflicts=True)
    # stop session
    # TASK OK OR NOT!


def start_update_posts():
    # todo get proxy
    post = models.Post.objects.filter(last_modified__lte=datetime.date(2000, 1, 1),
                                      taken=0).order_by('found_date').last()
    if post is not None:
        post.taken = 1
        post.save()
        try:
            text, date, watch, like, share, comment, owner_name, owner_url, imgs, owner_id = get_data_from_url(post)
            if text is not None:
                if owner_id is None:
                    post.user_id = post.group_id
                else:
                    post.user_id = owner_id
                post.created_date = dateutil.parser.parse(date)
                post.likes_count = like
                post.comments_count = comment
                post.repost_count = share
                post.last_modified = datetime.datetime.now()
                post.sphinx_id = get_sphinx_id(post.id, post.group_id)
                post.content_hash = get_md5_text(text)
                post.taken = 0
                post.save()
                models.PostContent.objects.create(post_id=post.id, content=text)
        except Exception:
            post.taken = 0
            post.save()
        post.taken = 0
        post.save()
