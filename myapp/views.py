import subprocess
import unicodedata

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from lib.extractor import Extractor, ExtractionItem
from django.http import HttpResponse
from myapp.models import Image, Product, Brand
from django.conf import settings



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


def get_brand(brand):
    b = Brand.objects.filter(name__icontains=brand)
    #Brand id 99 is for all unknown ones
    if not b:
        return 99
    else:
        return b[0].id

@csrf_exempt
def upload(request):
    desc = request.POST['description']
    brnd = request.POST['brand']
    vers = request.POST['version']  
    mode = request.POST['model']  

    if not request.method == 'POST':
        return HttpResponse("POST only")

    if not 'file' in request.FILES:
        return HttpResponse("No file")

    f = request.FILES['file']
    path = 'uploads/' + f.name
    handle_uploaded_file(f, path)
    md5 = io_md5(path)
    image = Image(filename=f.name,description=desc,brand_id=get_brand(brnd),hash=md5, rootfs_extracted=False, kernel_extracted=False)
    image.save()
    FILE_PATH = unicodedata.normalize('NFKD', settings.UPLOAD_DIR+image.filename).encode('ascii','ignore')

    #Add a product related to the image (commtented for easier debugging)
    # product = Product(iid=image,product=mode,version=vers)
    # product.save()    
    # print image
    # print product

    #rootfs=True, parallel=False, ,kernel=False, 
    extract = Extractor(FILE_PATH, settings.EXTRACTED_DIR, True, False, False, '127.0.0.1' ,'NetGear')
    extract.extract()

    return HttpResponse("File uploaded // hash : %s" % md5)


def test(request):
    wut = settings.UPLOAD_DIR
    return HttpResponse(wut)
