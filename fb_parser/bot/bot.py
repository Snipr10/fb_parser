import argparse
import json
import re
import time

import requests
import pyquery
from bs4 import BeautifulSoup

from fb_parser.utils.find_data import find_value


def get_session():
    # todo is bots?
    # return None, None, None, None
    # proxy
    email = "79663803199"
    password = "xEQpdFKGtFKGo26198"
    session = requests.session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:39.0) Gecko/20100101 Firefox/39.0'
    })

    fb_dtsg, user_id, xs, token = login(session, email, password)
    if fb_dtsg:
        return session, fb_dtsg, user_id, xs, token
    else:
        # return get_session()
        return None, None, None, None, None


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
