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
    dataset = gdal.Open(os.path.join(BASE_DIR, "main/images/newsat.tif"))
    inProj = Proj(init = 'epsg:3857')
    outProj = Proj(init = 'epsg:4326')

    red = request.GET.get('red', '')
    blue = request.GET.get('blue', '')
    green = request.GET.get('green', '')

    request_bbox = [float(t) for t in BBOX.split(',')]
    request_bbox[0], request_bbox[1] = transform(inProj, outProj, request_bbox[0], request_bbox[1])
    request_bbox[2], request_bbox[3] = transform(inProj, outProj, request_bbox[2], request_bbox[3])
    
    out = gdal.Translate('',dataset, format='MEM',outputType=gdal.GDT_Int16, strict=True,width=256, height=256, projWin = [request_bbox[0], request_bbox[3], request_bbox[2], request_bbox[1]], scaleParams = [[]]) 
    out_ds = (out.ReadAsArray())
    # im = numpy.uint16(numpy.dstack((out_ds[4,:,:], out_ds[3,:,:], out_ds[2,:,:])))
    im1 = numpy.dstack((out_ds[int(green),:,:], out_ds[int(blue),:,:], out_ds[int(red),:,:]))

    # print(im.shape)
    print()
    _, ar = cv2.imencode('.png',im1)
    response = HttpResponse(ar.tobytes(),content_type="image/png;base64")
    return response


def add(request):
    BBOX = request.GET.get('bbox', 'BBOX')
    dataset = gdal.Open(os.path.join(BASE_DIR, "main/images/newsat.tif"))
    inProj = Proj(init = 'epsg:3857')
    outProj = Proj(init = 'epsg:4326')

    band1 = request.GET.get('band1', '')
    band2 = request.GET.get('band2', '')

    request_bbox = [float(t) for t in BBOX.split(',')]
    request_bbox[0], request_bbox[1] = transform(inProj, outProj, request_bbox[0], request_bbox[1])
    request_bbox[2], request_bbox[3] = transform(inProj, outProj, request_bbox[2], request_bbox[3])

    out = gdal.Translate('',dataset, format='MEM',outputType=gdal.GDT_Int16, strict=True,width=256, height=256, projWin = [request_bbox[0], request_bbox[3], request_bbox[2], request_bbox[1]], scaleParams = [[]])
    out_ds = (out.ReadAsArray())

    layer = out_ds[int(band1),:,:] + out_ds[int(band2),:,:]
    im1 = numpy.dstack((layer, layer, layer))

    _, ar = cv2.imencode('.png',im1)
    response = HttpResponse(ar.tobytes(),content_type="image/png;base64")
    return response


def compute(request, ops):
    BBOX = request.GET.get('bbox', 'BBOX')
    dataset = gdal.Open(os.path.join(BASE_DIR, "main/images/newsat.tif"))
    inProj = Proj(init = 'epsg:3857')
    outProj = Proj(init = 'epsg:4326')

    request_bbox = [float(t) for t in BBOX.split(',')]
    request_bbox[0], request_bbox[1] = transform(inProj, outProj, request_bbox[0], request_bbox[1])
    request_bbox[2], request_bbox[3] = transform(inProj, outProj, request_bbox[2], request_bbox[3])

    out = gdal.Translate('',dataset, format='MEM',outputType=gdal.GDT_Int16, strict=True,width=256, height=256, projWin = [request_bbox[0], request_bbox[3], request_bbox[2], request_bbox[1]], scaleParams = [[]])
    out_ds = (out.ReadAsArray())

    stack = []
    openBrackets = []
    for i in range(len(ops)):
        if (ops[i] == '('):
            openBrackets.append(len(stack))
            stack.append(ops[i])
        elif (ops[i] == ')'):
            index = openBrackets.pop() + 1
            reduceIndex = index - 1
            layer = stack[index]
            index += 1

            while (index < len(stack)):
                if (stack[index] == '+'):
                    layer += stack[index + 1]
                elif (stack[index] == '-'):
                    layer -= stack[index + 1]
                elif (stack[index] == '*'):
                    layer *= stack[index + 1]
                else:
                    layer /= stack[index + 1]
                    
                index += 2

            while (len(stack) != reduceIndex):
                stack.pop()

            stack.append(layer)
        elif (ops[i] == '+' or ops[i] == '*' or ops[i] == '^' or ops[i] == '-'):
            stack.append(ops[i])
        else:
            stack.append(out_ds[int(ops[i]),:,:].astype(float))

    layer = stack.pop()

    im1 = numpy.dstack((layer, layer, layer))

    _, ar = cv2.imencode('.png',im1)
    response = HttpResponse(ar.tobytes(),content_type="image/png;base64")
    return response

def convolve2D(image, kernel, padding=0, strides=1):
    kernel = numpy.flipud(numpy.fliplr(kernel))

    xKernShape = kernel.shape[0]
    yKernShape = kernel.shape[1]
    xImgShape = image.shape[0]
    yImgShape = image.shape[1]

    xOutput = int(((xImgShape - xKernShape + 2 * padding) / strides) + 1)
    yOutput = int(((yImgShape - yKernShape + 2 * padding) / strides) + 1)
    output = numpy.zeros((xOutput, yOutput))

    if padding != 0:
        imagePadded = numpy.zeros((image.shape[0] + padding*2, image.shape[1] + padding*2))
        imagePadded[int(padding):int(-1 * padding), int(padding):int(-1 * padding)] = image[:,:,0]
        print(imagePadded)
    else:
        imagePadded = image

    for y in range(image.shape[1]):
        if y > image.shape[1] - yKernShape:
            break
        if y % strides == 0:
            for x in range(image.shape[0]):
                if x > image.shape[0] - xKernShape:
                    break
                try:
                    if x % strides == 0:
                        output[x, y] = (kernel * imagePadded[x: x + xKernShape, y: y + yKernShape]).sum()
                except:
                    break

    return output

def convolute(request):
    BBOX = request.GET.get('bbox', 'BBOX')
    dataset = gdal.Open(os.path.join(BASE_DIR, "main/images/newsat.tif"))
    inProj = Proj(init = 'epsg:3857')
    outProj = Proj(init = 'epsg:4326')

    band = request.GET.get('band', '')

    request_bbox = [float(t) for t in BBOX.split(',')]
    request_bbox[0], request_bbox[1] = transform(inProj, outProj, request_bbox[0], request_bbox[1])
    request_bbox[2], request_bbox[3] = transform(inProj, outProj, request_bbox[2], request_bbox[3])

    out = gdal.Translate('',dataset, format='MEM',outputType=gdal.GDT_Int16, strict=True,width=256, height=256, projWin = [request_bbox[0], request_bbox[3], request_bbox[2], request_bbox[1]], scaleParams = [[]])
    out_ds = (out.ReadAsArray())

    layer = out_ds[int(band),:,:]
    im = numpy.dstack((layer, layer, layer))

    kernel = numpy.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
    output = convolve2D(im, kernel, padding=2)

    im1 = numpy.dstack((output, output, output))

    _, ar = cv2.imencode('.png',im1)
    response = HttpResponse(ar.tobytes(),content_type="image/png;base64")
    return response