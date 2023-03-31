import re
import uuid

from facebook_scraper import get_posts
from facebook_scraper import get_posts, FacebookScraper
from facebook_scraper import get_group_info
from facebook_scraper import get_profile, get_posts_by_search
from facebook_scraper.page_iterators import PageParser
from requests.cookies import cookiejar_from_dict
import multiprocessing
import random
import time

import threading

from django.utils import timezone

import os

from django.db.models import Q

from MyFacebookScraper import MyFacebookScraper

cookies = {'c_user': '100067798487014', 'datr': 'qZJnYp7x6IuXV9AaELahfI-R',
           'fr': '0ECE2kUBrj2rKbpbr.AWVhMQFxbPx4U9kmS45-_DNCVGE.BiZ5Kp.qJ.AAA.0.0.BiZ5LB.AWWa3D_Ukfg',
           'sb': 'qZJnYgAmZVLGMBONB017QqTc', 'xs': '48%3AMOS3Drhz0ZOOLA%3A2%3A1650954924%3A-1%3A-1'}
cookies1 = {'c_user': '100077256379331', 'datr': 'q9VoYhOu7rLT763bNum5JWbK',
            'fr': '08930r9t19vvK9ObL.AWWf2YmwZxjedRvVTVwrTq7VRLQ.BiaNWr.C5.AAA.0.0.BiaNWu.AWWrVq0j_WY',
            'sb': 'q9VoYuWwX6NM0dRBAlsNdr5c', 'xs': '35%3Ah3Of_B4voITQ0g%3A2%3A1651037614%3A-1%3A-1'}
cookies2 = {'c_user': '100075883932859', 'datr': 'qtZoYuMOZ1VlzLV-lWqLZ9eG',
            'fr': '0GEG9xWbFDAZrJPMM.AWXhHJeaDHiOcszCyWsbcA202WQ.BiaNaq.mI.AAA.0.0.BiaNar.AWWxqYv0jmI',
            'sb': 'qtZoYgmnU2hHy9Mc3X0hq2hq', 'xs': '10%3ADdnGBgmDJMDRTw%3A2%3A1651037868%3A-1%3A-1'}

cookies4 = {'c_user': '100080693307667', 'datr': 'moN4YmFNdWp8irqyt3qy14Cz',
            'fr': '0546Ze7QWzbTgO5T5.AWUuz7DTIENiF1cYlc-7ElLdgVg.BieIOa.9W.AAA.0.0.BieIOa.AWXsBSRxhas',
            'xs': '36:0HKCauhnk3u1bw:2:1652065104:-1:-1'}
cookies5 = {"c_user": "100055228036894", "xs": "18:TO49QEwKtQHc7Q:2:1632427392:-1:-1",
            "fr": "0I5Wz2UJ6ZUiQBTMO.AWWkdkPW7GEbB69ptR-qSRIvNLg.BhTN1_.7h.AAA.0.0.BhTN1_.AWWPhy0U-QQ",
            "datr": "b91MYY8Shr_-QkzgydyQTAO3"}

cookies5 = {
    "c_user": "100055228036894",
    "xs": "18:TO49QEwKtQHc7Q:2:1632427392:-1:-1",
    "fr": "0I5Wz2UJ6ZUiQBTMO.AWWkdkPW7GEbB69ptR-qSRIvNLg.BhTN1_.7h.AAA.0.0.BhTN1_.AWWPhy0U-QQ",
    "datr": "b91MYY8Shr_-QkzgydyQTAO3"
}

c = {"sb": "",
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
g1 = {"sb": "I_9mYp6HPFgdpL5oFgXXaTDv", "wd": "1920x1080", "datr": "J_9mYgwe_OOllb0Q4vAmUHHz",
      "c_user": "100080957851684",
      "xs": "34%3AMZuZnRbH2qvc8A%3A2%3A1650917155%3A-1%3A-1%3A%3AAcVrXUXGjjAeQ5vOZg_GHBaWt43FUxUwD8Km_XuuIA",
      "fr": "0MQQk7m39FsVaCSBA.AWVOcP88Q_3USiazsr9qN4zJTno.BiZv84.qr.AAA.0.0.BiZv84.AWVhtQNqfqk"}
c = {"datr": "Y3EvYuzq6F_VuH_lqgPOTlyg", "fr": "0BYVpAg3eng0caKes..BiL3Fj.Pi.AAA.0.0.BiL3Fj.AWUKEE7EtXA",
     "xs": "33%3AqvfQd4558mvkHQ%3A2%3A1654901215%3A-1%3A-1", "c_user": "100082332092316",
     "sb": "Y3EvYneIYwUZJGhWBxtZSNQ2", "wd": "1920x579"}
test = {"c_user": "100084593945657", "xs": "7:4n0CmeNONRnhzA:2:1660323778:-1:-1",
        "fr": "0WcYZitfQ3BA5haPm.AWU-eAERjdPgPZ_4wsC36o70KrM.Bi9ofC.DM.AAA.0.0.Bi9ofC.AWUIL2XEhBE",
        "datr": "rIf2YpVOFkWRcIZetGSPDGjS"}

test = {"c_user": "100084689405441", "xs": "41:o2MXdOM6IMT-Ng:2:1660461939:-1:-1",
        "fr": "02ze6a1AxGA6l5rag.AWV4lPX8wBOglkU0jNWaQ5842wc.Bi-KNy.R3.AAA.0.0.Bi-KNy.AWWOCLbK5_s",
        "datr": "ZaP4YrGAnUg1prEnOcrqLrbU"}
test = {"datr": "Y3EvYuzq6F_VuH_lqgPOTlyg", "fr": "0BYVpAg3eng0caKes..BiL3Fj.Pi.AAA.0.0.BiL3Fj.AWUKEE7EtXA",
        "xs": "8%3AQpY0jKr33b3wVQ%3A2%3A1655186587%3A-1%3A-1", "c_user": "100081943885995",
        "sb": "Y3EvYneIYwUZJGhWBxtZSNQ2", "wd": "1920x579"}


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

    # from facebook_scraper import _scraper
    # _scraper.set_proxy('http://{}:{}@{}:{}'.format("gusevoleg96_gmail_com", "bba10694c3", "45.134.28.220", "30011"))
    # _scraper.login("6285604649532", "ui82MZ7QIM")
    # from facebook_scraper import *
    # face = FacebookScraper()
    # face.session.cookies.update(cookiejar_from_dict(c))
    face.set_proxy('http://{}:{}@{}:{}'.format("gusevoleg96_gmail_com", "bba10694c3", "193.192.1.58", "30011"))
    face.session.cookies.update(
        {"sb": "b3f6Y2WNQxwVA4C6SgFppxzi", "wd": "1132x719", "dpr": "1.25", "datr": "b3f6YyewAqXP_l4Th7LSulbI",
         "c_user": "100071125037608", "xs": "27%3AQC7bfEBVkXe-sQ%3A2%3A1677358989%3A-1%3A-1",
         "fr": "01QnUuYC1d4S7btvh.AWXcT990kvyumhPcD4OKpeLp74g.Bj-ndv.yI.AAA.0.0.Bj-neQ.AWVpw81OLt0",
         "presence": "C%7B%22t3%22%3A%5B%5D%2C%22utc3%22%3A1677358998830%2C%22v%22%3A1%7D"}
        )
    next(face.get_posts_by_search("комитет"))

    next(face.get_posts('nintendo', pages=1))
    face.login("6283899120989", "B2uS6ukB")
    next(face.get_posts_by_search("spb"))
    #     print(z)
    results = []

    "http://gusevoleg96_gmail_com:bba10694c3@45.134.28.220:30011"
    face.set_proxy('http://{}:{}@{}:{}'.format("gusevoleg96_gmail_com", "bba10694c3", "45.134.28.220", "30011"))
    try:
        for s in face.get_posts('180832818999519'):
            s
        for s in face.get_posts_by_search("икт школы 416 денис давыдов провел для участников", page_limit=40,
                                          max_past_limit=10):
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
    # z['uspip install facebook-scraperer_id']
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

    futures = []
    #
    # x = threading.Thread(target=update_, args=(0,))
    # x.start()
    from core.models import Account, Keyword, Sources, SourcesItems, AllProxy
    from fb_parser.tasks import start_parsing_by_keyword, start_parsing_by_source, start_parsing_account_source
    from fb_parser.utils.find_data import update_time_timezone
    import datetime
    from fb_parser.settings import network_id
    # fb_parse()

    # fb_parse()
    import base64
    import json
    import requests

    z = []
    l = []
    p = []

    try:
        with open("fb_1.txt", 'r') as f:

            # with open("fb_1.txt", 'r', encoding='utf-8') as f:
            for line in f:
                domains = json.loads(line.split("|")[-1])
                r = {}
                # domains = base64.b64decode(line.split("|")[-1]).decode("utf-8")
                # domains  = json.loads(base64.b64decode(    line.split(":")[-1]).decode("utf-8"))
                # for d in json.loads(domains):
                for d in domains:
                    r[d["name"]] = d["value"]

                # for d in domains.split(";"):
                #     if d.split("=")[0]:
                #         r[d.split("=")[0]] = d.split("=")[-1]
                k = str(r).replace("'", '"')
                a = line.split(":")[0]
                b = line.split(":")[1]
                Account.objects.create(

                    login=a,
                    password=b,
                    cookie=k,
                    proxy_id=1

                )
                z.append(k)
    except Exception as e:
        print(e)
    raise Exception("stop")

    # with open("ok.txt", 'r', encoding='utf-8') as f:
    #     for line in f:
    #         l.append(line.split(":")[0])
    #         p.append(line.split(":")[-1].rstrip('\n')    )
    # for l_ in l:
    #     print(l_)
    # for l_ in p:
    #     print(l_)

    res = []
    try:
        with open("fb_2.txt", "r") as f:
            for line in f:
                split_ = line.split("|")
                username, password = split_[0].split(":")
                _, app_version, _ = split_[1][:split_[1].find("(")].strip().split(" ")
                android_, dpi, resolution, manufacturer, model, device, cpu, _, version_code = split_[1][
                                                                                               split_[1].find("(") + 1:
                                                                                               split_[
                                                                                                   1].find(")")].split(
                    ";")
                android_version, android_release = android_.split("/")

                device_id, phone_id, client_session_id, advertising_id = split_[2].split(";")
                for s in split_[3].split(";"):
                    if "session" in s:
                        sessionid = s.split("=")[-1]
                        break
                settings = {
                    "uuids": {
                        "phone_id": phone_id,
                        "uuid": uuid.uuid4().urn[9:],
                        "client_session_id": client_session_id,
                        "advertising_id": advertising_id,
                        "device_id": device_id
                    },
                    'authorization_data': {'ds_user_id': sessionid.split("%")[0],
                                           'sessionid': sessionid,
                                           },
                    'cookies': {
                        'sessionid': sessionid
                    },  # set here your saved cookies
                    "last_login": None,
                    "device_settings": {
                        "cpu": cpu.strip(),
                        "dpi": dpi.strip(),
                        "model": model.strip(),
                        "device": device.strip(),
                        "resolution": resolution.strip(),
                        "app_version": app_version,
                        "manufacturer": manufacturer.strip(),
                        "version_code": version_code.strip(),
                        "android_release": android_release,
                        "android_version": android_version
                    },
                    "user_agent": split_[1]
                }
                res.append(settings)
    except Exception as e:
        print(e)
    #
    # try:
    #     with open("fb_1.txt", 'r') as f:
    #
    #     # with open("fb_1.txt", 'r', encoding='utf-8') as f:
    #         for line in f:
    #             domains = json.loads(line.split("|")[1])
    #             r = {}
    #             # domains = base64.b64decode(line.split("|")[-1]).decode("utf-8")
    #
    #             # for d in json.loads(domains):
    #             for d in domains:
    #
    #                 r[d["name"]] = d["value"]
    #
    #             # for d in domains.split(";"):
    #             #     if d.split("=")[0]:
    #             #         r[d.split("=")[0]] = d.split("=")[-1]
    #             k = str(r).replace("'", '"')
    #             print(line.split(":")[0])
    #             print(line.split(":")[1])
    #             print(k)
    #             z.append(k)
    # except Exception as e:
    #     print(e)
    # try:
    #     with open("fb_2.txt", 'r') as f:
    #         for line in f:
    #             # domains = json.loads(line.split("::")[4])
    #             user = line.split("|")[0].split(":")[0]
    #             pass_ = line.split("|")[0].split(":")[-1]
    #             session = line.split("|")[3].split(";")[8].replace("sessionid=", '').replace(" ", "")
    #             if "=" in session:
    #                 session =  line.split("|")[3].split(";")[7].replace("sessionid=", '').replace(" ", "")
    #             user, pass_, session
    #             z.append("")
    # except Exception as e:
    #     print(e)
    #
    # try:
    #     with open("fb_1.txt", 'r', encoding='utf-8') as f:
    #         for line in f:
    #             # domains = json.loads(line.split("::")[4])
    #             r = {}
    #             domains = base64.b64decode(line.split("|")[-1]).decode("utf-8")
    #
    #             for d in json.loads(domains):
    #                 r[d["name"]] = d["value"]
    #
    #             # for d in domains.split(";"):
    #             #     if d.split("=")[0]:
    #             #         r[d.split("=")[0]] = d.split("=")[-1]
    #             k = str(r).replace("'", '"')
    #             z.append(k)
    # except Exception as e:
    #     print(e)
    # try:
    #     with open("fb_1.txt", 'r', encoding='utf-8') as f:
    #         for line in f:
    #             domains = json.loads(base64.b64decode(
    #                 line.split("|")[-1]
    #             ).decode("utf-8"))
    #             r = {}
    #             # domains = base64.b64decode(line.split("|")[-1]).decode("utf-8")
    #
    #             for d in domains:
    #                 r[d["name"]] = d["value"]
    #
    #             # for d in domains.split(";"):
    #             #     if d.split("=")[0]:
    #             #         r[d.split("=")[0]] = d.split("=")[-1]
    #             k = str(r).replace("'", '"')
    #             z.append(k)
    # except Exception as e:
    #     print(e)
    # try:
    #     fb_parse()
    # except Exception as e:
    #     print(e)
    #
    #     {"sb": "yf6xYuYqGh1HN6pazRp26Jlb", 'wd': '1920x1080', 'datr': 'z_6xYs7zKTGHzOgQS8XcTu2q',
    #      'c_user': '100082538532245',
    #      'xs': '41%3A7yzjUDRI8vBDwA%3A2%3A1655832266%3A-1%3A-1%3A%3AAcU1CP4KzHy1nfFTPJJrFfrSKVazPIO6eFQO3NVqgA',
    #      'spin': '', 'fr': '0GhUlfOob60v7Cwyk.AWXuvawJlb_ltL8IB-9LTRypSgo.Bisf8w.2J.AAA.0.0.Bisf8w.AWXEV37sSP0'}
