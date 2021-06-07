import requests
from bs4 import BeautifulSoup
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from core import models
from fb_parser.tasks import start_parsing_by_keyword, start_first_update_posts
from fb_parser.utils.find_data import find_value


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def test(request):
    url = 'https://m.facebook.com/profile.php?id=100019236511133'
    r = requests.get('https://m.facebook.com/profile.php?id=100019236511133').text
    href = url
    s = BeautifulSoup(r)

    if 'profile.php' in url:
        fb_id = url.split('id=')[1]
        try:
            href = s.find('link').attrs['href']
        except Exception:
            pass
    else:
        fb_id = find_value(r, 'userID', 3, separator='"')

    start_first_update_posts()
    # start_update_posts()
