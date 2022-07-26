import logging

import requests
from bs4 import BeautifulSoup
from requests.exceptions import SSLError, ConnectTimeout, ProxyError
from urllib3 import HTTPSConnectionPool

from core import models
from django.utils import timezone
from fb_parser.utils.find_data import find_value, get_sphinx_id
from fb_parser.utils.proxy import get_proxy, get_proxy_str, stop_proxy
import datetime

logger = logging.getLogger(__file__)


def get_update_user(user_id):
    if user_id is not None:
        user = models.User.objects.filter(id=user_id)
        if user.exists():
            return
        else:
            name = ""
            username, fb_id, href, logo = get_user_data('https://www.facebook.com/profile.php?id=' + user_id)
            if user_id in username:
                username = user_id
            else:
                name = username
                sp = href.split('/')
                if href[-1] == '/':
                    username = sp[-2]
                else:
                    username = sp[-1]
            if username is not None:
                print(username)
                user = models.User.objects.filter(screen_name=username)
                if user.exists():
                    return
            if username is not None or fb_id is not None or href is not None:
                models.User.objects.create(id=user_id, screen_name=username, name=name, url=href, sphinx_id=get_sphinx_id(href),
                                           logo=logo, last_modify=timezone.now(), last_modified=datetime.datetime.now())


def get_user_data(url, attempt=0):
    if attempt >= 5:
        return None, None, None, None
    proxy = get_proxy()
    if proxy is None:
        return None, None, None, None
    try:
        res = requests.get(url,  proxies=get_proxy_str(proxy), timeout=60)
        # res = requests.get('https://www.facebook.com/profile.php?id=100034163134835',  proxies=get_proxy_str(proxy))
        if res:
            s = BeautifulSoup(res.text)
            href = url
            if 'profile.php' in url:
                fb_id = url.split('id=')[1]
                try:
                    href = s.find_all('meta', property="og:url")[0]['content']
                except Exception:
                    try:
                        href = s.find('link').attrs['href']
                    except Exception:
                        pass
            else:
                fb_id = find_value(res.text, 'userID', 3, separator='"')
            avatar = None
            try:
                avatar = s.find_all('meta', property="og:image")[0]['content']
            except Exception:
                pass
            return s.find("title").text, fb_id, href, avatar
        else:
            return get_user_data(url, attempt+1)
    except (SSLError, ConnectionError, ConnectTimeout) as e:
        stop_proxy(proxy)
        return get_user_data(url, attempt)
    except ProxyError:
        stop_proxy(proxy)
        return get_user_data(url, attempt)
    except HTTPSConnectionPool:
        stop_proxy(proxy)
        return get_user_data(url, attempt)
    except Exception as e:
        logger.error(e)
        return get_user_data(url, attempt + 1)

