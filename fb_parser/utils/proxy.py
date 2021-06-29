import datetime

import requests
from django.db.models import Q
from django.utils import timezone

from core import models


def get_proxy():
    print('get proxy')
    # proxy = models.AllProxy.objects.filter(failed=False)
    proxy = models.AllProxy.objects.filter(Q(last_used__isnull=True)
                                           | Q(last_used__lte=(timezone.localtime()) - datetime.timedelta(minutes=4),
                                               banned_fb=False, login='test', port=8080),
                                           ).order_by('last_used').first()
    if proxy is not None:
        proxy_last_used(proxy)
        session = generate_proxy_session('test', 'test', proxy.ip, proxy.port)
        if check_facebook_url(session):
            return proxy
        else:
            proxy.banned_fb = True
            proxy.save()
            return get_proxy()
    return None

def check_facebook_url(session):
    try:
        response = session.get('https://m.facebook.com', timeout=15)
        if response.ok:
            return True
    except Exception as e:
        print(e)
        pass
    return False


def generate_proxy_session(proxy_login, proxy_password, proxy_host, proxy_port):
    session = requests.session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:39.0) Gecko/20100101 Firefox/39.0'
    })
    proxy_str = f"{proxy_login}:{proxy_password}@{proxy_host}:{proxy_port}"
    proxies = {'http': f'http://{proxy_str}', 'https': f'https://{proxy_str}'}

    session.proxies.update(proxies)
    return session


def get_proxy_str(proxy):
    proxy_str = f"{proxy.login}:{proxy.proxy_password}@{proxy.ip}:{proxy.port}"
    return {'http': f'http://{proxy_str}', 'https': f'https://{proxy_str}'}


def proxy_last_used(proxy):
    proxy.last_used = datetime.datetime.now()
    proxy.save()


def stop_proxy(proxy):
    proxy.banned_fb = True
    proxy.save()
