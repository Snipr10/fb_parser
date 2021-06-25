import json
import re

import requests
from bs4 import BeautifulSoup
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core import models
from fb_parser.bot.bot import login
from fb_parser.tasks import start_parsing_by_keyword, start_first_update_posts, add_work_credential, add_proxy
from fb_parser.utils.find_data import find_value


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def test(request):
    proxy = {'http': 'http://test:test@125.25.33.212:8080', 'https': 'https://test:test@125.25.33.212:8080'}

    session = requests.session()
    session.proxies.update(proxy)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:39.0) Gecko/20100101 Firefox/39.0'
    })
    print('session start')

    fb_dtsg, user_id, xs, token = login(session, "79608541372", 'sBHsy86767')

    q = 'key'
    url = 'https://m.facebook.com/search/posts/?q=%s&source=filter&pn=8&isTrending=0&' \
          'fb_dtsg_ag=%s&__a=AYlcAmMg3mcscBWQCbVswKQbSUum-R7WYoZMoRSwBlJp6gjuv2v2LwCzB_1ZZe4khj4N2vM7UjQWttgYqsq7DxeUlgmEVmSge5LOz1ZdWHEGQQ' % (
              q, token)

    headers = {'cookie': 'c_user=' + user_id + '; xs=' + xs + ';'}

    res = requests.get(url, headers=headers, proxies=proxy)

    res_json = json.loads(res.text.replace("for (;;);", ''))
    last_story_fbid = None
    id = None
    print('get_ dataa')
    print(res.text)

    print('res_json')
    print(res_json)
    print("html")
    urls = []
    result= []
    for story in re.findall(r'story_fbid=\d+&amp;id=\d+', res_json['payload']['actions'][0]['html']):
        data_url = story.split('&amp;')
        if last_story_fbid != data_url[0] or id != data_url[1]:
            if story not in urls:
                last_story_fbid = data_url[0]
                id = data_url[1]
                result.append(data_url[0].replace('story_fbid=', '') + '&' + data_url[1].replace('id=', ''))
    for story in re.findall(r'groups/\d+/permalink/\d+', res_json['payload']['actions'][0]['html']):
        data_url = story.split('/permalink/')
        if last_story_fbid != data_url[0] or id != data_url[1]:
            if story not in urls:
                last_story_fbid = data_url[0].replace('groups/', '')
                id = data_url[1]
                urls.append(story)
                result.append(data_url[1] + '&' + data_url[0].replace('groups/', ''))

    cursor = find_value(res.text, 'cursor=', num_sep_chars=0, separator='&amp')
    print("RESULT")
    print(result)

    return Response(str(result))

    return models.Post.objects.all()
    start_first_update_posts()
