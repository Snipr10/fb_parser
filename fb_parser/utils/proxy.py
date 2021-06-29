import datetime

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
    return proxy


def get_proxy_str(proxy):
    proxy_str = f"{proxy.login}:{proxy.proxy_password}@{proxy.ip}:{proxy.port}"
    return {'http': f'http://{proxy_str}', 'https': f'https://{proxy_str}'}


def proxy_last_used(proxy):
    proxy.last_used = datetime.datetime.now()
    proxy.save()


def stop_proxy(proxy):
    proxy.banned_fb = True
    proxy.save()
