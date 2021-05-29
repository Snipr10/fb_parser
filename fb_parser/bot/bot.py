import datetime
import requests
import pyquery

from core import models
from fb_parser.utils.find_data import find_value
from fb_parser.utils.proxy import get_proxy_str, proxy_last_used


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
    work_credit.save()
    try:
        account = models.Account.objects.get(id=work_credit.account_id)
    except Exception:
        work_credit.locked = True
        work_credit.save()
        return get_session()
    try:
        proxy = models.AllProxy.objects.get(id=work_credit.proxy_id)
    except Exception:
        work_credit.delete()
        return get_session()
    session = requests.session()
    session.proxies.update(get_proxy_str(proxy))
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:39.0) Gecko/20100101 Firefox/39.0'
    })

    fb_dtsg, user_id, xs, token = login(session, account.login, account.password)
    if fb_dtsg:
        account.availability_check = datetime.datetime.now()
        account.save()
        proxy_last_used(proxy)
        return work_credit, proxy, session, fb_dtsg, user_id, xs, token
    else:
        work_credit.delete()
        return get_session()


def login(session, email, password):
    # load Facebook's cookies.
    response = session.get('https://m.facebook.com')

    # login to Facebook
    response = session.post('https://m.facebook.com/login.php', data={
        'email': email,
        'pass': password
    }, allow_redirects=False)

    # If c_user cookie is present, login was successful
    if 'c_user' in response.cookies:

        # Make a request to homepage to get fb_dtsg token
        homepage_resp = session.get('https://m.facebook.com/home.php')

        dom = pyquery.PyQuery(homepage_resp.text.encode('utf8'))
        fb_dtsg = dom('input[name="fb_dtsg"]').val()
        token = find_value(homepage_resp.text, 'dtsg_ag":{"token":')
        return fb_dtsg, response.cookies['c_user'], response.cookies['xs'], token
    else:
        return False, None, None, None
