import datetime
import logging

import dateutil.parser

import json
import re

import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from requests.exceptions import SSLError, ConnectTimeout, ProxyError
from urllib3 import HTTPSConnectionPool

from core import models
from fb_parser.parser_data.user import get_update_user
from fb_parser.settings import BATCH_SIZE
from fb_parser.utils.find_data import find_value, update_time_timezone, get_sphinx_id, get_md5_text
from fb_parser.utils.proxy import get_proxy_str, get_proxy, proxy_last_used, stop_proxy

logger = logging.getLogger(__file__)


def get_class_text(soup, class_name):
    try:
        return soup.find_all("div", {"class": class_name})[0].text
    except Exception as e:
        logger.error(e)
        return None


def get_data(url, proxy):
    # user Proxy
    imgs = []
    owner_id = None

    try:
        # todo time out requests
        # time.sleep(60)
        # test
        res = requests.get(url, proxies=get_proxy_str(proxy), timeout=60)

        res_text = res.text
        try:
            soup = BeautifulSoup(res_text)
        except Exception as e:
            logger.error(e)
            print(e)
            return None, None, None, None, None, None, None, None, imgs, owner_id
        try:
            fb_photo_class = None
            all_imgs = soup.find_all('img')
            for img in all_imgs:
                try:
                    if 'https://scontent.frix7-1.fna.fbcdn.net/v' in img['src'] and not 'alt' in img.attrs:
                        if fb_photo_class is None:
                            fb_photo_class = img.attrs['class'][0]
                            imgs.append(img['src'].replace('amp;', ''))
                        elif fb_photo_class == img.attrs['class'][0]:
                            imgs.append(img['src'].replace('amp;', ''))
                except KeyError:
                    pass
        except Exception as e:
            logger.error(e)
            pass
        # text = get_class_text(soup, 'bx')
        # if text is None:
        #     text = get_class_text(soup, 'bw')
        text = None
        if text is None:
            try:
                divs = soup.find_all("div")
                try:
                    divs[20].find('p')
                    text = divs[20].text
                except Exception:
                    for p in soup.find_all("div")[1:]:
                        try:
                            p.find('p').find('span').text
                            text = p.text
                            break
                        except Exception:
                            pass
                    if text is None:
                        for p in soup.find_all("div")[1:]:
                            try:
                                text = p.find('p').text
                                break
                            except Exception:
                                pass
            except Exception:
                try:
                    text = soup.find_all("title")[0].text
                except Exception:
                    text = soup.text
        date = None
        try:
            date = find_value(res_text, 'dateCreated', 3, separator='"')
        except Exception:
            try:
                date = soup.find_all("abbr")[0].text
            except Exception:
                pass
        watch = find_value(res_text, 'WatchAction"', 24, separator='}')
        if watch is not None:
            watch.replace(":", '')
        like = find_value(res_text, 'LikeAction"', 24, separator='}')
        if like is not None:
            like.replace(":", '')
        share = find_value(res_text, 'ShareAction"', 24, separator='}')
        if share is not None:
            share.replace(":", '')
        comment = find_value(res_text, 'CommentAction"', 24, separator='}')
        if comment is not None:
            comment.replace(":", '')
        try:
            owner = soup.find_all("h3", {'class': ['bt', 'bu', 'bv', 'bw']})[0]
            try:
                owner_name = owner.contents[0].text
            except Exception:
                owner_name = owner.text
            try:
                owner = owner.find_all('a', href=True)
                owner_url = owner[0]['href']
                owner_url = owner_url[:owner_url.find('&')].replace("?refid=52", "")
                owner_id_all = owner[1]['href']
                owner_id = owner_id_all[owner_id_all.find('&id=') + 4:].replace('&refid=18&__tn__=C-R', '')

            except Exception as e:
                print(e)
                owner_id = url[url.find("&id=") + 4:]

                owner_url = '/profile.php?' + url[url.find("&id=") + 1:]
        except Exception as e:
            logger.error(e)
            print(e)
            owner_name = None
            owner_id = url[url.find("&id=") + 1:]
            owner_url = '/profile.php?' + url[url.find("&id=") + 1:]
        try:
            if owner_id is None:
                owner_id = find_value(find_value(res_text, 'owning_profile', 1, separator='}'), 'id:', 1, separator='"')
        except Exception as e:
            print(e)
    except (SSLError, ConnectionError, ConnectTimeout):
        stop_proxy(proxy)
        return get_data(url, get_proxy())
    except ProxyError:
        stop_proxy(proxy)
        return get_data(url, get_proxy())
    # except HTTPSConnectionPool:
    #     stop_proxy(proxy)
    #     return get_data(url, get_proxy())
    except Exception as e:
        logger.error(e)
        print(e)
        return None, None, None, None, None, None, None, None, imgs, owner_id
    return text, date, watch, like, share, comment, owner_name, owner_url, imgs, owner_id


def search_by_word(work_credit, session, proxy, fb_dtsg_ag, user, xs, token, key_word, cursor=None, urls=[], result=[],
                   limit=0):
    try:
        q = key_word.keyword
        url = 'https://m.facebook.com/search/posts/?q=%s&source=filter&pn=8&isTrending=0&' \
              'fb_dtsg_ag=%s&__a=AYlcAmMg3mcscBWQCbVswKQbSUum-R7WYoZMoRSwBlJp6gjuv2v2LwCzB_1ZZe4khj4N2vM7UjQWttgYqsq7DxeUlgmEVmSge5LOz1ZdWHEGQQ' % (
                  q, token)
        if cursor:
            url = url + "&cursor=" + cursor
        headers = {'cookie': 'c_user=' + user + '; xs=' + xs + ';'}

        res = requests.get(url, headers=headers)
        res_json = json.loads(res.text.replace("for (;;);", ''))
        last_story_fbid = None
        id = None
        for story in re.findall(r'story_fbid=\d+&amp;id=\d+', res_json['payload']['actions'][0]['html']):
            data_url = story.split('&amp;')
            if last_story_fbid != data_url[0] or id != data_url[1]:
                if story not in urls:
                    last_story_fbid = data_url[0]
                    id = data_url[1]
                    result.append(data_url[0].replace('story_fbid=', '') + '&' + data_url[1].replace('id=', ''))
        for story in re.findall(r'groups/\d+/permalink/\d+', res_json['payload']['actions'][0]['html']):
            data_url = story.split('/permalink/')
            if last_story_fbid != data_url[0] or id != data_url[1]:
                if story not in urls:
                    last_story_fbid = data_url[0].replace('groups/', '')
                    id = data_url[1]
                    urls.append(story)
                    result.append(data_url[1] + '&' + data_url[0].replace('groups/', ''))

        cursor = find_value(res.text, 'cursor=', num_sep_chars=0, separator='&amp')
        if limit <= 10:
            try:
                search_by_word(work_credit, proxy, session, fb_dtsg_ag, user, xs, token, key_word, cursor, urls, result,
                               limit + 1)
            except Exception as e:
                logger.error(e)
                print(e)
        key_word.last_modified = update_time_timezone(timezone.localtime())
    except Exception as e:
        logger.error(e)
        print(e)
        pass
    return result


def search(work_credit, session, proxy, fb_dtsg_ag, user, xs, token, key_word, cursor=None, urls=[], result=[],
           limit=0):
    result = search_by_word(work_credit, session, proxy, fb_dtsg_ag, user, xs, token, key_word, cursor=None, urls=[],
                            result=[], limit=0)
    posts = []

    for res in result:
        data_url = res.split('&')
        try:

            posts.append(models.Post(id=int(data_url[0]),
                                     group_id=int(data_url[1])))
        except Exception as e:
            logger.error(e)
            print(e)
    models.Post.objects.bulk_create(posts, batch_size=BATCH_SIZE, ignore_conflicts=True)
    key_word.taken = 0
    key_word.save()
    work_credit.last_parsing = datetime.datetime.now()
    work_credit.in_progress = False
    work_credit.save()
    proxy.last_used = datetime.datetime.now()
    proxy.save()
    return result


def get_data_from_url(post, proxy):
    url = 'https://m.facebook.com/story.php?story_fbid=%s&id=%s' % (post.id, post.group_id)
    return get_data(url, proxy)


def parallel_parse_post(post):
    proxy = get_proxy()
    print("proxy")
    if proxy is None:
        post.taken = 0
        post.save()
        return
    print("start")

    try:

        try:
            text, date, watch, like, share, comment, owner_name, owner_url, imgs, owner_id = get_data_from_url(post,
                                                                                                               proxy)
            if text is not None:
                # if owner_id is None or owner_id == post.group_id:

                # get_user_data(url, attempt + 1)

                if owner_id is None:
                    post.user_id = post.group_id
                else:
                    post.user_id = owner_id
                try:
                    post.created_date = dateutil.parser.parse(date)
                except TypeError:
                    pass
                post.likes_count = update_count(like)
                post.comments_count = update_count(comment)
                post.repost_count = update_count(share)
                post.last_modified = datetime.datetime.now()
                post.sphinx_id = get_sphinx_id(post.id)
                post.content_hash = get_md5_text(text)
                post.taken = 0
                post.save()
                models.PostContent.objects.create(post_id=post.id, content=text)
                get_update_user(post.user_id)
                get_update_user(owner_id)
                fb_photo = []
                for img in imgs:
                    fb_photo.append(models.Photo(id=post.id, href=img))
                models.Photo.objects.bulk_create(fb_photo, batch_size=BATCH_SIZE, ignore_conflicts=True)
        except Exception as e:
            logger.error(e)
            pass
    except Exception as e:
        logger.error(e)
        pass
    post.taken = 0
    post.save()
    proxy_last_used(proxy)


def update_count(data):
    if data is not None:
        return re.sub('\D', '', data)
    return data
