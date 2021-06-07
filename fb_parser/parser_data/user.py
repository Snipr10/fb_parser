import requests
from bs4 import BeautifulSoup

from core import models
from fb_parser.utils.find_data import find_value, get_sphinx_id
from fb_parser.utils.proxy import get_proxy, get_proxy_str


def get_update_user(user_id):
    if user_id is not None:
        user = models.User.objects.filter(id=user_id)
        if user.exists():
            return
        else:
            username, fb_id, href = get_user_data('https://www.facebook.com/profile.php?id=' + user_id)
            if username is not None or fb_id is not None or href is not None:
                models.User.objects.create(id=user_id, screen_name=username, url=href, sphinx_id=get_sphinx_id(href))


def get_user_data(url, attempt=0):
    if attempt >= 5:
        return None
    proxy = get_proxy()
    if proxy is None:
        return None, None, None
    try:
         # get proxy
        # r = requests.get(url,  proxies=get_proxy_str(proxy)).text
        res = requests.get('https://www.facebook.com/profile.php?id=100034163134835',  proxies=get_proxy_str(proxy))
        if res:
            s = BeautifulSoup(res.text)
            href = url
            if 'profile.php' in url:
                fb_id = url.split('id=')[1]
                try:
                    href = s.find('link').attrs['href']
                except Exception:
                    pass
            else:
                fb_id = find_value(res.text, 'userID', 3, separator='"')
            return s.find("title").text, fb_id, href
        else:
            return get_user_data(url, attempt+1)
    except Exception:
        return get_user_data(url, attempt + 1)
