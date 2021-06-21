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
import base64

def index(request):
    BBOX = request.GET.get('bbox', 'BBOX')
    dataset = gdal.Open(os.path.join(BASE_DIR, "main/images/out2019.tif"))
    inProj = Proj(init = 'epsg:3857')
    outProj = Proj(init = 'epsg:4326')

    red = request.GET.get('red', '')
    blue = request.GET.get('blue', '')
    green = request.GET.get('green', '')

    request_bbox = [float(t) for t in BBOX.split(',')]
    request_bbox[0], request_bbox[1] = transform(inProj, outProj, request_bbox[0], request_bbox[1])
    request_bbox[2], request_bbox[3] = transform(inProj, outProj, request_bbox[2], request_bbox[3])
    
    out = gdal.Translate('',dataset, format='MEM', strict=True,width=256, height=256, projWin = [request_bbox[0], request_bbox[3], request_bbox[2], request_bbox[1]], scaleParams = [[20, 3000]]) 
    out_ds = (out.ReadAsArray())
    im = numpy.uint8(numpy.dstack((out_ds[4,:,:], out_ds[3,:,:], out_ds[2,:,:])))
    im1 = numpy.int16(numpy.dstack((out_ds[2,:,:], out_ds[3,:,:], out_ds[4,:,:])))

    print(im.shape)
    print()
    _, ar = cv2.imencode('.png',im1)
    response = HttpResponse(ar.tobytes(),content_type="image/png;base64")
    return response
    # pil_image = Image.fromarray(im)
    # response = HttpResponse(content_type='image/png')
    # pil_image.save(response, "PNG")
    # return response

