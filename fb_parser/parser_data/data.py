import datetime
import logging

import dateutil.parser

import json
import re

import django.db
import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from requests.exceptions import SSLError, ConnectTimeout, ProxyError
from urllib3 import HTTPSConnectionPool

from core import models
from fb_parser.parser_data.user import get_update_user
from fb_parser.settings import BATCH_SIZE, FIRST_DATE
from fb_parser.utils.find_data import find_value, update_time_timezone, get_sphinx_id, get_md5_text
from fb_parser.utils.proxy import get_proxy_str, get_proxy, proxy_last_used, stop_proxy

logger = logging.getLogger(__file__)

batch_size = 200


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
    print('get_data')
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
        return None, None, None, None, None, None, None, None, imgs, update_count(owner_id)
    return text, date, watch, like, share, comment, owner_name, owner_url, imgs, update_count(owner_id)


def search_by_word(work_credit, session, proxy, fb_dtsg_ag, user, xs, token, key_word, cursor=None, urls=[], result=[],
                   limit=0):
    try:
        print("start search")
        q = key_word.keyword
        url = 'https://m.facebook.com/search/posts/?q=%s&source=filter&pn=8&isTrending=0&' \
              'fb_dtsg_ag=%s&__a=AYlcAmMg3mcscBWQCbVswKQbSUum-R7WYoZMoRSwBlJp6gjuv2v2LwCzB_1ZZe4khj4N2vM7UjQWttgYqsq7DxeUlgmEVmSge5LOz1ZdWHEGQQ' % (
                  q, token)
        if cursor:
            url = url + "&cursor=" + cursor
        headers = {'cookie': 'c_user=' + user + '; xs=' + xs + ';'}
        res = requests.get(url, headers=headers, proxies=get_proxy_str(proxy))
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
        try:
            cursor = find_value(res.text, 'cursor=', num_sep_chars=0, separator='&amp')
        except Exception as e:
            print("cursos ex " + str(e))
            cursor = None
        print('cursor ' + str(cursor))
        if limit <= 10 and cursor is not None:
            try:
                search_by_word(work_credit, session, proxy, fb_dtsg_ag, user, xs, token, key_word, cursor, urls, result,
                               limit + 1)
            except Exception as e:
                logger.error(e)
                print(e)
        print("ok")
        print("ok res")
        print(result)
        print("ok res1")
        key_word.last_modified = update_time_timezone(timezone.localtime())
    except Exception as e:
        logger.error(e)
        print(e)
        pass
    return result


def search_source(face_session, account, source, retro):
    print("start  search source")
    print(retro)

    try:
        limit = 0
        results = []
        retro_post = 0
        try:
            parse_url = source.data
            if source.type == 6 or source.type == "6" or source.type == 7 or source.type == "7":
                parse_url = "groups/" + parse_url
            print(f"parse_url {parse_url}")
            # for p in face_session.get_posts(parse_url):
            try:
                group_id = save_group_info(face_session, source.data, parse_url)
            except Exception as e:
                print(f"error group_id {e}")
                group_id = None
            for p in face_session.get_posts(parse_url, page_limit=40, max_past_limit=10):
                try:
                    if p['time'] < retro:
                        retro_post += 1
                        print("not new")
                    else:
                        print("new")
                    print(p['time'])
                    if p['post_url'] is None:
                        p['post_url'] = face_session.base_url + "/" + parse_url + "/permalink/" + p['post_id']
                    if group_id:
                        p['page_id'] = group_id
                    results.append(p)
                    if limit > 250 or retro_post > 10:
                        break
                    limit += 1
                except Exception as e:
                    print(e)
        except Exception as e:
            print(f"search_source {source} {e}")
            # source.disabled = 1
            # source.save(update_fields=["disabled"])
            django.db.close_old_connections()
            if "Content Not Found" in str(e):
                source.taken = 0
                source.last_modified = update_time_timezone(timezone.localtime())
                source.save(update_fields=["last_modified", "taken"])
            elif "404 Client Error: Not Found for url: https://m.facebook.com/" in str(
                    e) or "Exceeded 30 redirects" in str(e) or "404 Client Error: Not Found for url:" in str(e):
                if len(results) < 1:
                    raise e
            # raise e
        if len(results) == 0:
            from fb_parser.bot.bot import check_bot
            check_bot(face_session, account)
        django.db.close_old_connections()

        print(f"saver account {account}")
        saver(results)
        source.taken = 0
        if len(results) >= 0:
            source.reindexing = 0
            source.last_modified = update_time_timezone(timezone.localtime())
        else:
            account.error = "Can not get result"

        source.save(update_fields=["last_modified", "taken", "reindexing"])
        account.last_parsing = update_time_timezone(timezone.localtime())
        account.taken = 0
        account.save(update_fields=["last_parsing", "taken"])
    except Exception as e:
        print(f"search_source {e}")
        account.last_parsing = update_time_timezone(timezone.localtime())
        account.error = str(e)
        account.taken = 0
        if "Temporarily Blocked" in str(e) or "banned" in str(e) or "Your Account Has Been Disabled" in str(e) or \
                "Exceeded 30 redirects" in str(e) or "404 Client Error: Not Found for url:" in str(e):
            account.banned = 1
            account.error = str(e)
            account.save(update_fields=["error", "taken", "last_parsing", "banned"])
        else:
            account.save(update_fields=["error", "taken", "last_parsing"])

        print(e)
    return True


def search(face_session, account, keyword):
    try:
        print("start  search")
        limit = 0
        results = []
        print(keyword.keyword)
        search_key = keyword.keyword
        if len(search_key) > 10:
            white_space = search_key.find(" ", 10)
            if white_space > 10:
                search_key = search_key[:white_space]
        try:
            for p in face_session.get_posts_by_search(search_key, page_limit=3, max_past_limit=10):
                try:
                    results.append(p)
                    if limit > 250:
                        break
                    limit += 1
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
        if len(results) == 0:
            from fb_parser.bot.bot import check_bot
            check_bot(face_session, account)
        saver(results)
        django.db.close_old_connections()
        keyword.taken = 0
        keyword.reindexing = 0
        keyword.last_modified = update_time_timezone(timezone.localtime())
        keyword.save(update_fields=["taken", "last_modified", "reindexing"])

        account.last_parsing = update_time_timezone(timezone.localtime())
        account.taken = 0
        account.save(update_fields=["last_parsing", "taken"])

    except Exception as e:
        account.last_parsing = update_time_timezone(timezone.localtime())
        account.error = str(e)
        account.taken = 0
        if "Temporarily Blocked" in str(e) or "banned" in str(e) or "Your Account Has Been Disabled" in str(e):
            account.banned = 1
            account.save(update_fields=["error", "taken", "last_parsing", "banned"])
        else:
            account.save(update_fields=["error", "taken", "last_parsing"])

        print(e)
    return True


def saver(results):
    post_content = []
    users = []
    posts = []
    django.db.close_old_connections()
    print("saver")
    for z in results:
        print(z)
        try:
            print("FIRST_DATE")
            if z['time'] < FIRST_DATE:
                continue
            print("z['time'] < FIRST_DATE")

            post_id = z['post_id']
            content = z['post_text']
            if content is None:
                content = z['text']
            user_id = z['user_id']
            post_url = z['post_url']
            group_id = z['page_id'] if z['page_id'] else user_id

            user_url = z['user_url'].split("?")[0]
            if user_url[-1] == "/":
                user_url = user_url[:-1]
            try:
                username = user_url.split("/")[-1]
            except Exception as e:
                print(f"Exception save  {e}")

                username = None
            if not user_id:
                user_id = get_sphinx_id(username)

            post_content.append(models.PostContent(post_id=post_id, content=content))
            posts.append(
                models.Post(id=post_id,
                            user_id=user_id,
                            group_id=group_id,
                            created_date=z['time'],
                            sphinx_id=get_sphinx_id(post_url),
                            likes_count=z['likes'],
                            comments_count=z['comments'],
                            repost_count=z['shares'],
                            url=post_url,
                            content_hash=get_md5_text(content)
                            )
            )

            users.append(models.User(id=user_id, username=user_id, screen_name=username, logo="", url=user_url,
                                     sphinx_id=get_sphinx_id(user_url), last_modified=datetime.datetime.now(),
                                     name=z['username']))
        except Exception as e:
            print(f"Exception save append {e}")

    try:
        django.db.close_old_connections()

        models.User.objects.bulk_create(users, batch_size=batch_size, ignore_conflicts=True)
    except Exception as e:
        print(f"user bulk create  {e}")
    try:
        django.db.close_old_connections()
        models.User.objects.bulk_update(users,
                                        [
                                            'logo', 'name', 'followers', 'username', 'screen_name',
                                            'last_modified'
                                        ],
                                        batch_size=batch_size)
    except Exception as e:
        print(f"user bulk update {e}")
    try:
        django.db.close_old_connections()

        for u in users:
            try:
                u.save()
            except Exception as e:
                print(f"u save {e}")
    except Exception as e:
        print(f"u saver {e}")
    try:
        django.db.close_old_connections()

        models.Post.objects.bulk_update(posts, [
            'created_date', 'likes_count', 'comments_count', 'repost_count',
            'last_modified', 'user_id', 'group_id'
        ], batch_size=batch_size)
    except Exception as e:
        print(f"Post bulk_update {e}")

    try:
        django.db.close_old_connections()

        models.Post.objects.bulk_create(posts, batch_size=batch_size, ignore_conflicts=True)
    except Exception as e:
        print(f"Post bulk_create {e}")

    try:
        django.db.close_old_connections()

        models.PostContent.objects.bulk_create(post_content, batch_size=batch_size, ignore_conflicts=True)
    except Exception as e:
        print(f"PostContent bulk_create {e}")


def get_data_from_url(post, proxy):
    url = 'https://m.facebook.com/story.php?story_fbid=%s&id=%s' % (post.id, post.group_id)
    return get_data(url, proxy)


def post_taken(post, taken=0):
    post.taken = taken
    post.save()


def parallel_parse_post(post):
    try:
        proxy = get_proxy()
    except Exception:
        post_taken(post)
        return
    print("proxy")
    print(proxy)
    if proxy is None:
        post_taken(post)
        return

    try:

        try:
            text, date, watch, like, share, comment, owner_name, owner_url, imgs, owner_id = get_data_from_url(post,
                                                                                                               proxy)
            if text is not None:
                # if owner_id is None or owner_id == post.group_id:

                # get_user_data(url, attempt + 1)
                print(owner_id)
                print("owner_id")

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
                post.taken = -1
                post.save()
                try:
                    models.PostContent.objects.create(post_id=post.id, content=text)
                except Exception as e:
                    logger.error(e)
                    pass
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
    post.taken = -1
    post.save()
    proxy_last_used(proxy)


def update_count(data):
    if data is not None:
        return re.sub('\D', '', data)
    return data


def save_group_info(face, group, parse_url):
    try:
        url = parse_url
        resp = face.get(url).html
        try:
            url = resp.find("a[href*='?view=info']", first=True).attrs["href"]
        except AttributeError:
            return None
        logger.debug(f"Requesting page from: {url}")
        resp = face.get(url).html
        result = {}
        result["id"] = re.search(r'/groups/(\d+)', url).group(1)
        try:
            result["name"] = resp.find("header h3", first=True).text
            result["type"] = resp.find("header div", first=True).text
        except AttributeError:
            return result["id"]
        try:
            int(group)
            username = None
        except Exception:
            username = group
        user_url = "https://www.facebook.com" + f'/{parse_url}'
        try:
            models.User.objects.create(id=result["id"], screen_name=username, username=result["id"], logo="",
                                       url=user_url,
                                       sphinx_id=get_sphinx_id(user_url), last_modified=datetime.datetime.now(),
                                       name=result["name"])
        except Exception:
            if username:
                try:
                    user = models.User.objects.filter(screen_name=username).first()
                    if user:
                        if user.id != result["id"]:
                            user.id = result["id"]
                            user.username = result["id"]
                            user.save()
                except Exception as e:
                    print(f"save_group_info 1 {e}")

            models.User.objects.bulk_update(
                [models.User(id=result["id"], screen_name=username, username=result["id"], logo="", url=user_url,
                             sphinx_id=get_sphinx_id(user_url), last_modified=datetime.datetime.now(),
                             name=result["name"])],
                [
                    'screen_name', 'logo', 'name', 'followers', 'username', 'screen_name',
                    'last_modified'
                ],
                batch_size=batch_size)
    except Exception as e:
        print(f"save_group_info 2 {e}")
    try:
        return result["id"]
    except Exception as e:
        print(f"save_group_info 3 {e}")
        return None
