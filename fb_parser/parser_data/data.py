import json
import re

import requests
from bs4 import BeautifulSoup
from django.utils import timezone

from fb_parser.utils.find_data import find_value, update_time_timezone


def get_class_text(soup, class_name):
    try:
        return soup.find_all("div", {"class": class_name})[0].text
    except Exception:
        return None


def get_data(url):
    # user Proxy
    imgs = []
    owner_id = None

    try:
        # todo time out requests
        # time.sleep(60)
        # test
        res = requests.get(url)
        res_text = res.text
        try:
            soup = BeautifulSoup(res_text)
        except Exception as e:
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
        except Exception:
            pass
        text = get_class_text(soup, 'bx')
        if text is None:
            text = get_class_text(soup, 'bw')
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
        like = find_value(res_text, 'LikeAction"', 24, separator='}')
        share = find_value(res_text, 'ShareAction"', 24, separator='}')
        comment = find_value(res_text, 'CommentAction"', 24, separator='}')
        try:
            group = soup.find_all("h3", {'class': ['bt', 'bu', 'bv', 'bw']})[0]
            group_name = group.text
            try:

                group_url = group.find_all('a', href=True)[0]['href']
                group_url = group_url[:group_url.find('&')].replace("?refid=52", "")
            except Exception as e:
                print(e)
                group_url = '/profile.php?' + url[url.find("&id=") + 1:]
        except Exception as e:
            print(e)
            group_name = None
            group_url = '/profile.php?' + url[url.find("&id=") + 1:]
        try:
            owner_id = find_value(find_value(res_text, 'owning_profile', 1, separator='}'), 'id:', 1, separator='"')
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
        return None, None, None, None, None, None, None, None, imgs, owner_id
    return text, date, watch, like, share, comment, group_name, group_url, imgs, owner_id


def search(session, fb_dtsg_ag, user, xs, token, key_word, cursor=None, urls=[], result=[], limit=0):
    try:
        q = key_word.keyword
        url = 'https://m.facebook.com/search/posts/?q=%s&source=filter&pn=8&isTrending=0&' \
              'fb_dtsg_ag=%s&__a=AYlcAmMg3mcscBWQCbVswKQbSUum-R7WYoZMoRSwBlJp6gjuv2v2LwCzB_1ZZe4khj4N2vM7UjQWttgYqsq7DxeUlgmEVmSge5LOz1ZdWHEGQQ' % (
              key_word.k, token)
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
                    result.append(data_url[0].replace('story_fbid=', '')+'&'+ data_url[1].replace('id=', ''))
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
                search(session, fb_dtsg_ag, user, xs, token, q, cursor, urls, result, limit+1)
            except Exception as e:
                print(e)
        key_word.last_modified = update_time_timezone(timezone.localtime())
    except Exception as e:
        print(e)
        pass
    key_word.taken = 0
    key_word.save()
    return result


def get_data_from_url(post):
    url = 'https://m.facebook.com/story.php?story_fbid=%s&id=%s' % (post.id, post.group_id)

    return get_data(url)

    # text, date, watch, like, share, comment, owner_name, owner_url, imgs, owner_id = get_data(story)
    # if text is not None:
    #     result.append({
    #         'id': data_url[1],
    #         'story': story,
    #         'text': text,
    #         'date': date,
    #         'watch': watch,
    #         'like': like,
    #         'share': share,
    #         'comment': comment,
    #         'group_name': owner_name,
    #         'group_url': owner_url,
    #         'group_id': data_url[0],
    #         'owner_id': owner_id,
    #         'photo': imgs
    #     })