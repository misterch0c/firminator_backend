from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from django.http import HttpResponse
#import datetime


import hashlib
def io_md5(target):
    """
    Performs MD5 with a block size of 64kb.
    """
    blocksize = 65536
    hasher = hashlib.md5()
    with open(target, 'rb') as ifp:
        buf = ifp.read(blocksize)
        while buf:
            hasher.update(buf)
            buf = ifp.read(blocksize)
        return hasher.hexdigest()


def handle_uploaded_file(f, path):
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


"""
TODO
get brand, model, version, description from request.POST[]
MODEL:
    Image
        filename
        description
        brand (foreign key)
        hash
        rootfs_extracted False
        kernel_extracted False
    Brand
        name
    Product
        product (model)
        version
"""
@csrf_exempt
def upload(request):
    if not request.method == 'POST':
        return HttpResponse("POST only")

    if not 'file' in request.FILES:
        return HttpResponse("No file")

    f = request.FILES['file']
    path = 'uploads/' + f.name
    handle_uploaded_file(f, path)
    md5 = io_md5(path)
    return HttpResponse("File uploaded // hash : %s" % md5)


def test(request):
    wut = "hello world"
    return HttpResponse(wut)
