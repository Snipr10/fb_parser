import datetime
import logging

import requests
import pyquery

from core import models
from django.utils import timezone
from fb_parser.utils.find_data import find_value
from fb_parser.utils.proxy import get_proxy_str, proxy_last_used, get_proxy

logger = logging.getLogger(__file__)


def get_session():
    # todo is bots?
    # return None, None, None, None
    # proxy
    work_credit = models.WorkCred.objects.filter(in_progress=False, locked=False).order_by('last_parsing').first()
    if work_credit is None:
        return None, None, None, None, None, None, None
    # email = "79663803199"
    # password = "xEQpdFKGtFKGo26198"
    work_credit.in_progress = True
    work_credit.start_parsing = timezone.now()
    work_credit.last_parsing = timezone.now()

    work_credit.save()
    try:
        account = models.Account.objects.get(id=work_credit.account_id)
    except Exception as e:
        logger.error(e)
        print(e)
        work_credit.delete()
        return get_session()
    try:
        proxy = models.AllProxy.objects.get(id=work_credit.proxy_id)
    except Exception as e:
        logger.error(e)

        print(e)
        work_credit.delete()
        return get_session()
    print('session')
    session = requests.session()
    session.proxies.update(get_proxy_str(proxy))
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:39.0) Gecko/20100101 Firefox/39.0'
    })
    print('session start')

    fb_dtsg, user_id, xs, token = login(session, account.login, account.password)
    if fb_dtsg is not None and token is not None:
        account.availability_check = datetime.datetime.now()
        account.save()
        proxy_last_used(proxy)
        print('session ok')

        return work_credit, proxy, session, fb_dtsg, user_id, xs, token
    elif user_id is not None and xs is not None:
        account.banned = True
        account.save()
    else:
        proxy.banned_fb = True
        proxy.save()
    work_credit.delete()
    return get_session()


def login(session, email, password):
    try:
        proxy = {'http': 'http://test:test@14.207.202.160:8080', 'https': 'https://test:test@14.207.202.160:8080'}

        # load Facebook's cookies.
        print('response 0')

        response = session.get('https://m.facebook.com', proxies=proxy)
        print('response 1')
        # login to Facebook
        response = session.post('https://m.facebook.com/login.php', data={
            'email': email,
            'pass': password
        }, proxies=proxy, allow_redirects=False)
        print('response 2')

        # If c_user cookie is present, login was successful
        try:
            # if 'c_user' in response.cookies:

            # Make a request to homepage to get fb_dtsg token
            homepage_resp = session.get('https://m.facebook.com/home.php', proxies=proxy)
            dom = pyquery.PyQuery(homepage_resp.text.encode('utf8'))
            fb_dtsg = dom('input[name="fb_dtsg"]').val()
            token = find_value(homepage_resp.text, 'dtsg_ag":{"token":')
            print('response ok')

            return fb_dtsg, response.cookies['c_user'], response.cookies['xs'], token
        except Exception as e:
            logger.error(e)
            print(e)
            # return fb_dtsg, response.cookies['c_user'], response.cookies['xs'], token
            print('response ok1')

            return None, None, None, None
    except Exception as e:
        logger.error(e)
        print(e)
        print('response ok2')

        return None, None, None, None


def check_accounts(account, attempt=0):
    email = account.login
    password = account.password
    session = requests.session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:39.0) Gecko/20100101 Firefox/39.0'
    })

    proxy = get_proxy()
    if proxy is None:
        print('add proxy')
        return
    print("proxy.id")
    print(proxy.id)
    try:
        session.proxies.update(get_proxy_str(proxy))
        response = session.get('https://m.facebook.com', timeout=60)

        # login to Facebook
        response = session.post('https://m.facebook.com/login.php', data={
            'email': email,
            'pass': password
        }, allow_redirects=False)

        # If c_user cookie is present, login was successful
        print("check cookies")
        if 'c_user' in response.cookies:
            print("account ok " + email)
            # account.available = True
            # account.banned = False
            # account.save()
            try:
                models.WorkCred.objects.create(account_id=account.id, proxy_id=proxy.id, locked=False)
            except Exception:
                print("cannot create WorkCredentials ")
            return True
        else:
            print("account disable " + email)

            return False
    except Exception as e:
        logger.error(e)
        proxy.failed = True
        proxy.banned_fb = True
        proxy.save()
        print(e)
        if attempt < 5:
            print("account Exception " + email)

            return check_accounts(account, attempt + 1)
        else:
            print("account Exception disable " + email)
            return False
