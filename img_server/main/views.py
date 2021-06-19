from django.shortcuts import render
from django.http import HttpResponse
from img_server.settings import BASE_DIR
from PIL import Image
from pyproj import Proj, transform
from osgeo import gdal
import os
import cv2
import numpy
# 76.86674473142777 29.35635551477078 78.88672199967831 28.124043591774523
# 78.75000000000001 27.05912578437406 81.56250000000001 24.527134822597805

def index(request):
    BBOX = request.GET.get('bbox', 'BBOX')
    dataset = gdal.Open(os.path.join(BASE_DIR, "main/images/newsat.tif"))
    inProj = Proj(init = 'epsg:3857')
    outProj = Proj(init = 'epsg:4326')

    request_bbox = [float(t) for t in BBOX.split(',')]
    request_bbox[0], request_bbox[1] = transform(inProj, outProj, request_bbox[0], request_bbox[1])
    request_bbox[2], request_bbox[3] = transform(inProj, outProj, request_bbox[2], request_bbox[3])
    print(request_bbox[0], request_bbox[3], request_bbox[2], request_bbox[1])
    print()
    out = gdal.Translate('',dataset, format='MEM', strict=True,width=256, height=256, projWin = [request_bbox[0], request_bbox[3], request_bbox[2], request_bbox[1]]) 

    # out_ds = out.ReadAsArray()[0,...]
    # img = Image.fromarray(out_ds).resize((256, 256), Image.NEAREST)
    # response = HttpResponse(content_type="image/png")
    # img.save(response, "PNG")
    red = request.GET.get('red', '')
    blue = request.GET.get('blue', '')
    green = request.GET.get('green', '')

    out_ds1 = out.ReadAsArray()[int(red)]
    out_ds2 = out.ReadAsArray()[int(blue)]
    out_ds3 = out.ReadAsArray()[int(green)]

    im = numpy.dstack((out_ds1, out_ds2, out_ds3))
    _, ar = cv2.imencode('.png', im)
    response = HttpResponse(ar.tobytes(), content_type='image/png')

    return response

