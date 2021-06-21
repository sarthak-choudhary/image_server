from django.shortcuts import render
from django.http import HttpResponse
from img_server.settings import BASE_DIR
from PIL import Image
from pyproj import Proj, transform
from osgeo import gdal
import matplotlib.pyplot as plt
from PIL import Image
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

    red = request.GET.get('red', '')
    blue = request.GET.get('blue', '')
    green = request.GET.get('green', '')

    request_bbox = [float(t) for t in BBOX.split(',')]
    request_bbox[0], request_bbox[1] = transform(inProj, outProj, request_bbox[0], request_bbox[1])
    request_bbox[2], request_bbox[3] = transform(inProj, outProj, request_bbox[2], request_bbox[3])
    
    out = gdal.Translate('',dataset, format='MEM', strict=True,width=256, height=256, projWin = [request_bbox[0], request_bbox[3], request_bbox[2], request_bbox[1]], scaleParams = [[]]) 

    # out_ds1 = out.ReadAsArray()[int(red)]
    # out_ds2 = out.ReadAsArray()[int(blue)]
    # out_ds3 = out.ReadAsArray()[int(green)]
    out_ds = out.ReadAsArray()


    # im = numpy.array([out_ds1, out_ds3, out_ds2])
    im = numpy.int16(numpy.dstack((out_ds[4,:,:], out_ds[3,:,:], out_ds[2,:,:])))
    print(im.shape)
    print()
    pil_image = Image.fromarray(im)
    # _, ar = cv2.imencode('.png', im)
    # im = cv2.imdecode(ar, cv2.IMREAD_ANYCOLOR)

    # plt.imshow(im)

    response = HttpResponse(content_type='image/png')
    pil_image.save(response, "PNG")

    return response

