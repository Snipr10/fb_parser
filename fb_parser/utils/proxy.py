import datetime

from core import models


def get_proxy():
    # proxy = models.AllProxy.objects.filter(failed=False)
    proxy = models.AllProxy.objects.filter().order_by('last_modified').first()
    return proxy


def get_proxy_str(proxy):
    proxy_str = f"{proxy.login}:{proxy.proxy_password}@{proxy.ip}:{proxy.port}"
    return {'http': f'http://{proxy_str}', 'https': f'https://{proxy_str}'}


def proxy_last_used(proxy):
    proxy.last_used = datetime.datetime.now()
    proxy.save()
