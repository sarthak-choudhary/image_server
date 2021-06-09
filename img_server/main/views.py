from django.shortcuts import render
from django.http import HttpResponse
from img_server.settings import BASE_DIR
from PIL import Image
from pyproj import Proj, transform
from osgeo import gdal
import os

def index(request):
    BBOX = request.GET.get('bbox', 'BBOX')
    dataset = gdal.Open(os.path.join(BASE_DIR, "main/images/sat.tif"))
    inProj = Proj(init = 'epsg:3857')
    outProj = Proj(init = 'epsg:4326')

    request_bbox = [float(t) for t in BBOX.split(',')]
    request_bbox[0], request_bbox[1] = transform(inProj, outProj, request_bbox[0], request_bbox[1])
    request_bbox[2], request_bbox[3] = transform(inProj, outProj, request_bbox[2], request_bbox[3])
    out = gdal.Translate('',dataset, format='MEM', strict=True,width=256, height=256, projWin=[request_bbox[0], request_bbox[3],request_bbox[2], request_bbox[1]]) 

    out_ds = out.ReadAsArray()[0,...]
    img = Image.fromarray(out_ds).resize((256, 256), Image.NEAREST)
    response = HttpResponse(content_type="image/png")
    img.save(response, "PNG")
    return response

