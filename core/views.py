from django.shortcuts import render

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from core import models
from fb_parser.tasks import start_parsing_by_keyword, start_first_update_posts


@csrf_exempt
@api_view(["GET"])
@permission_classes((AllowAny,))
def test(request):
    start_first_update_posts()
    # start_update_posts()
