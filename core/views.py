import requests
from bs4 import BeautifulSoup
from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core import models
from fb_parser.tasks import start_parsing_by_keyword, start_first_update_posts, add_work_credential, add_proxy
from fb_parser.utils.find_data import find_value


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def test(request):
    return Response({'token': models.Post.objects.all().first()})

    return models.Post.objects.all()
    start_first_update_posts()
