import datetime
import json
import logging

import requests
import pyquery

from MyFacebookScraper import MyFacebookScraper
from core import models
from django.utils import timezone
from fb_parser.utils.find_data import find_value, update_time_timezone
from fb_parser.utils.proxy import get_proxy_str, get_proxy
from requests.cookies import cookiejar_from_dict

logger = logging.getLogger(__file__)


def check_bot(face_session, account):
    print("check_bot")
    ban = True
    try:
        if face_session.get_profile("nintendo").get("id") is not None:
            ban = False
    except Exception as e:
        print(f"check_bot: {e}")

    if ban:
        account.banned = 1
        account.save(update_fields=["banned"])
        raise Exception("banned")


def get_session(is_special=False, is_join=False):
    print(f"get_session is_special {is_special}")
    if is_join:
        account = models.Account.objects.filter(taken=False, banned=False,
                                                is_join_group=1,
                                                last_parsing__lte=update_time_timezone(
                                                    timezone.now() - datetime.timedelta(minutes=20)),
                                                proxy_id__isnull=False).order_by(
            'last_parsing').first()

    elif is_special:
        account = models.Account.objects.filter(taken=False, banned=False,
                                                is_join_group=0,
                                                special_group=1,
                                                last_parsing__lte=update_time_timezone(
                                                    timezone.now() - datetime.timedelta(minutes=20)),
                                                proxy_id__isnull=False).order_by(
            'last_parsing').first()
    else:
        account = models.Account.objects.filter(taken=False, banned=False,
                                                is_join_group=0,
                                                special_group=0,
                                                last_parsing__lte=update_time_timezone(
                                                    timezone.now() - datetime.timedelta(minutes=20)),
                                                proxy_id__isnull=False).order_by(
            'last_parsing').first()
    print(account)

    if account is None:
        return None, None
    try:
        print("account taken")
        # proxy = models.AllProxy.objects.get(id=account.proxy_id)
        account.taken = True
        account.start_parsing = update_time_timezone(timezone.now())
        account.last_parsing = update_time_timezone(timezone.now())
        account.save()
        proxy = models.AllProxy.objects.get(id=account.proxy_id)
        face = MyFacebookScraper()
        face.set_user_agent(
            'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.113 Mobile Safari/537.36')

        face.session.cookies.update(cookiejar_from_dict(json.loads(account.cookie)))
        # face.login("100081198725298", "howardsxfloyd271")
        face.set_proxy('http://{}:{}@{}:{}'.format(proxy.login, proxy.proxy_password, proxy.ip, proxy.port))

        # face.set_proxy('http://{}:{}@{}:{}'.format("franz_allan+dev_mati", "13d9bb5825", "85.31.49.213", "30001"))
        print(f"face, account, {account}")

        return face, account
    except Exception as e:
        print(e)
        account.banned = True
        account.save()
        return None, None


def login(session, email, password):
    try:
        # load Facebook's cookies.
        print('response 0')

        response = session.get('https://m.facebook.com')
        print('response 1')
        # login to Facebook
        response = session.post('https://m.facebook.com/login.php', data={
            'email': email,
            'pass': password
        }, allow_redirects=False)
        print('response 2')

        # If c_user cookie is present, login was successful
        try:
            # if 'c_user' in response.cookies:

            # Make a request to homepage to get fb_dtsg token
            homepage_resp = session.get('https://m.facebook.com/home.php')
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

    proxy = get_proxy(is_8080=True)
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

        if response.ok:
            if 'c_user' in response.cookies:
                start_page = session.get('https://www.facebook.com/')
                if 'checkpoint' not in start_page.url:
                    print("account ok " + email)
                    account.available = True
                    account.banned = False
                    account.save()
                    try:
                        models.WorkCred.objects.create(account_id=account.id, proxy_id=proxy.id, locked=False)

                    except Exception:
                        print("cannot create WorkCredentials ")
                    return True
                else:
                    account.available = False
                    account.save()
                print("account disable " + email)
            else:
                account.banned = False
                account.save()
        return False
    except Exception:
        proxy.available = False
        proxy.save()
        if attempt < 5:
            print("account Exception " + email)

            return check_accounts(account, attempt + 1)
        else:
            print("account Exception disable " + email)
            return False
