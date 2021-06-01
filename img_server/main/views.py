from django.shortcuts import render
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework import status
from wsgiref.util import FileWrapper
from img_server.settings import BASE_DIR
import base64
import os

from rest_framework import renderers

class PNGRenderer(renderers.BaseRenderer):
    media_type = 'image/png'
    format = 'png'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data

# Create your views here.
@api_view(["GET", ])
@renderer_classes([PNGRenderer])
def index(request):
    img = open(os.path.join(BASE_DIR, "main/images/map.png"), "rb")
    
    return Response(FileWrapper(img), status = status.HTTP_200_OK)
