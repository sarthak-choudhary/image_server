from django.shortcuts import render
from django.http import HttpResponse
from img_server.settings import BASE_DIR
from PIL import Image
import os

def index(request):
    # img = open(os.path.join(BASE_DIR, "main/images/map.png"), "rb")
    # return Response(FileWrapper(img), content_type="image/jpeg",  status = status.HTTP_200_OK)
    try:
        with open(os.path.join(BASE_DIR, "main/images/map.png"), "rb") as f:
            return HttpResponse(f.read(), content_type="image/jpeg")
    except IOError:
        red = Image.new('RGBA', (1, 1), (255,0,0,0))
        response = HttpResponse(content_type="image/jpeg")
        red.save(response, "JPEG")
        return response