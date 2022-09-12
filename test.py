from facebook_scraper import get_posts
from facebook_scraper import get_posts, FacebookScraper
from facebook_scraper import get_group_info
from facebook_scraper import get_profile, get_posts_by_search
from requests.cookies import cookiejar_from_dict
import multiprocessing
import random
import time

import threading

from django.utils import timezone

import os

from django.db.models import Q

from MyFacebookScraper import MyFacebookScraper

cookies = {'c_user': '100067798487014', 'datr': 'qZJnYp7x6IuXV9AaELahfI-R', 'fr': '0ECE2kUBrj2rKbpbr.AWVhMQFxbPx4U9kmS45-_DNCVGE.BiZ5Kp.qJ.AAA.0.0.BiZ5LB.AWWa3D_Ukfg', 'sb': 'qZJnYgAmZVLGMBONB017QqTc', 'xs': '48%3AMOS3Drhz0ZOOLA%3A2%3A1650954924%3A-1%3A-1'}
cookies1 = {'c_user': '100077256379331', 'datr': 'q9VoYhOu7rLT763bNum5JWbK', 'fr': '08930r9t19vvK9ObL.AWWf2YmwZxjedRvVTVwrTq7VRLQ.BiaNWr.C5.AAA.0.0.BiaNWu.AWWrVq0j_WY', 'sb': 'q9VoYuWwX6NM0dRBAlsNdr5c', 'xs': '35%3Ah3Of_B4voITQ0g%3A2%3A1651037614%3A-1%3A-1'}
cookies2 = {'c_user': '100075883932859', 'datr': 'qtZoYuMOZ1VlzLV-lWqLZ9eG', 'fr': '0GEG9xWbFDAZrJPMM.AWXhHJeaDHiOcszCyWsbcA202WQ.BiaNaq.mI.AAA.0.0.BiaNar.AWWxqYv0jmI', 'sb': 'qtZoYgmnU2hHy9Mc3X0hq2hq', 'xs': '10%3ADdnGBgmDJMDRTw%3A2%3A1651037868%3A-1%3A-1'}

cookies4 = {'c_user': '100080693307667', 'datr': 'moN4YmFNdWp8irqyt3qy14Cz', 'fr': '0546Ze7QWzbTgO5T5.AWUuz7DTIENiF1cYlc-7ElLdgVg.BieIOa.9W.AAA.0.0.BieIOa.AWXsBSRxhas', 'xs': '36:0HKCauhnk3u1bw:2:1652065104:-1:-1'}
cookies5 = {"c_user": "100055228036894", "xs": "18:TO49QEwKtQHc7Q:2:1632427392:-1:-1", "fr": "0I5Wz2UJ6ZUiQBTMO.AWWkdkPW7GEbB69ptR-qSRIvNLg.BhTN1_.7h.AAA.0.0.BhTN1_.AWWPhy0U-QQ", "datr": "b91MYY8Shr_-QkzgydyQTAO3"}




cookies5 = {
    "c_user": "100055228036894",
    "xs": "18:TO49QEwKtQHc7Q:2:1632427392:-1:-1",
    "fr": "0I5Wz2UJ6ZUiQBTMO.AWWkdkPW7GEbB69ptR-qSRIvNLg.BhTN1_.7h.AAA.0.0.BhTN1_.AWWPhy0U-QQ",
    "datr": "b91MYY8Shr_-QkzgydyQTAO3"
}

c ={"sb": "",
    "wd": "1920x1080",
    "datr": "oHBqYqwUK1uvcET8YC2WPAoz",
    "c_user": "100080453063096"
    , "xs": "44%3A79SwuaP_IvOKAA%3A2%3A1651142813%3A-1%3A-1%3A%3AAcVyzf0OfVpbIkT2JzV98fYCOP7pSA_BaMRDqnQ89A",
    "spin": "",
    "fr": "0gUjvQLnQ0QEYTzCH.AWVIVkS2mGVu66L8CD7iS_K1aAg.BianCk.cR.AAA.0.0.BianCk.AWW_cgInPsU"}

cookies5 = {
    "sb": "I_9mYp6HPFgdpL5oFgXXaTDv",
    "wd": "1920x1080",
    "datr": "J_9mYgwe_OOllb0Q4vAmUHHz",
    "c_user": "100080957851684",
    "xs": "34%3AMZuZnRbH2qvc8A%3A2%3A1650917155%3A-1%3A-1%3A%3AAcVrXUXGjjAeQ5vOZg_GHBaWt43FUxUwD8Km_XuuIA",
    "fr": "0MQQk7m39FsVaCSBA.AWVOcP88Q_3USiazsr9qN4zJTno.BiZv84.qr.AAA.0.0.BiZv84.AWVhtQNqfqk"
}
g1 = {"sb": "I_9mYp6HPFgdpL5oFgXXaTDv", "wd": "1920x1080", "datr": "J_9mYgwe_OOllb0Q4vAmUHHz", "c_user": "100080957851684", "xs": "34%3AMZuZnRbH2qvc8A%3A2%3A1650917155%3A-1%3A-1%3A%3AAcVrXUXGjjAeQ5vOZg_GHBaWt43FUxUwD8Km_XuuIA", "fr": "0MQQk7m39FsVaCSBA.AWVOcP88Q_3USiazsr9qN4zJTno.BiZv84.qr.AAA.0.0.BiZv84.AWVhtQNqfqk"}
c = {"datr": "Y3EvYuzq6F_VuH_lqgPOTlyg", "fr": "0BYVpAg3eng0caKes..BiL3Fj.Pi.AAA.0.0.BiL3Fj.AWUKEE7EtXA", "xs": "33%3AqvfQd4558mvkHQ%3A2%3A1654901215%3A-1%3A-1", "c_user": "100082332092316", "sb": "Y3EvYneIYwUZJGhWBxtZSNQ2", "wd": "1920x579"}
test ={"sb": "_udqYsR1xVx7it5DcqRjoMfx", "wd": "1920x1080", "datr": "BehqYsXh4qxj6eys1r35U1Pp", "c_user": "100080513720722", "xs": "44%3AHto7m3-IBzvcQA%3A2%3A1651173375%3A-1%3A-1%3A%3AAcXO3Q4Z59FGQ3cy2nryWpkboh8sNa1EdJLPPQ6T_w", "spin": "", "fr": "05TnaiSlWS4N9IPi4.AWXnMLRwRFKduwSbL9JctWonnSo.BiauhK.yF.AAA.0.0.BiauhK.AWWS7-zRw4c"}

def fb_parse():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fb_parser.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    print(1)
    import django

    django.setup()

    face = MyFacebookScraper()

    # face.session.cookies.update(cookiejar_from_dict(c))
    face.session.cookies.update(test)
    #     print(z)
    results = []
    face.set_proxy('http://{}:{}@{}:{}'.format("franz_allan_mati_io", "1926ad016e", "84.54.11.163", "30001"))
    try:
        for s in face.get_posts('nintendo'):
            s
        # for s in face.get_posts('nintendo'):
        from fb_parser.parser_data.data import save_group_info
        # save_group_info(face, 'tverskoy')
        for post in face.get_posts('groups/tverskoy', page_limit=30, max_past_limit=10):
            results.append(post)
            print(post['text'][:50])
        for s in face.get_posts('nintendo'):
            s
    except Exception as e:
        print(e)
    from fb_parser.parser_data.data import saver
    saver(results)
    #
    # z['likes']
    # z['comments']
    # z['shares']
    # z['post_url']
    # z['user_id']
    # z['username']
    # z['user_url']
    # z['page_id']
    # # face = FacebookScraper()
    # # face.login("100077835392612", "135xyT_AE_Hm644")
    # # face.session.cookies.get_dict()
    # # for post in get_posts('720002121403767', cookies=cookies2):
    # #      print(post['text'])
    # for post in get_posts_by_search('игра', cookies=cookies3):
    #     print(post['text'])
    # face = FacebookScraper()
    # face.login("gennadiyoa5pan@rambler.ru", "GTpM0ijRG9")
    # face.session.cookies.get_dict()
    # for post in face.get_posts('nintendo'):
    #     print(post['text'][:50])
    #
    # print(1)

if __name__ == '__main__':
    import base64
    import json
    import requests
    z = []
    try:
        with open("order2712884.txt", 'r', encoding='utf-8') as f:
            for line in f:
                domains = json.loads(base64.b64decode(
                    line.split(":")[-1]
                ).decode("utf-8"))
                r = {}
                # domains = base64.b64decode(line.split("|")[-1]).decode("utf-8")

                for d in domains:
                    r[d["name"]] = d["value"]

                # for d in domains.split(";"):
                #     if d.split("=")[0]:
                #         r[d.split("=")[0]] = d.split("=")[-1]
                k = str(r).replace("'", '"')
                z.append(k)
    except Exception as e:
        print(e)
    try:
        fb_parse()
    except Exception as e:
        print(e)

        {"sb": "yf6xYuYqGh1HN6pazRp26Jlb", 'wd': '1920x1080', 'datr': 'z_6xYs7zKTGHzOgQS8XcTu2q',
         'c_user': '100082538532245',
         'xs': '41%3A7yzjUDRI8vBDwA%3A2%3A1655832266%3A-1%3A-1%3A%3AAcU1CP4KzHy1nfFTPJJrFfrSKVazPIO6eFQO3NVqgA',
         'spin': '', 'fr': '0GhUlfOob60v7Cwyk.AWXuvawJlb_ltL8IB-9LTRypSgo.Bisf8w.2J.AAA.0.0.Bisf8w.AWXEV37sSP0'}