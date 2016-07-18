from __future__ import division

import subprocess
import uuid
import os, fnmatch
import tarfile
import shlex
from django.http import JsonResponse
from subprocess import Popen, PIPE
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from lib.extractor import Extractor, ExtractionItem
from lib.tar2db import tar2db, isElf
from django.http import HttpResponse
from myapp.models import Image, Product, Brand, ObjectToImage, Object, Treasure
from django.db import IntegrityError
from django.conf import settings
from django.db.models import Q
import hashlib
from django.core import serializers
import json
from lib.util import parseFilesToHierarchy
from django.core.files import File
import string

        # -=Making Pasta=-


        #                                                      |||
        #                                                      |||||,
        #                                                     \|||||/
        #                    /)                               `|||||/
        #               ,-""//-. ______                       |`"""'|
        #            ==|`-.//.-'|,-----'======================|  P  |====
        #              |        |---,---,  .---,((--------.   |  A  |
        #              |        |  /(_)/  /   (()))` ;'", \   |  S  |
        #              `-.____.-' /_  /  /  /| `;',`;; ,/( \  |  T  |
        #                        /(_)/  /  //  ; ` "  ((()) \ |  A  |
        #              .-::-.   /_  /  /  /)   "' ;" ; `;"'  \`-...-'
        #             (::::::) /(_)/   `=//==================='  
        #              `-::-' /   /     (/
        #          ----------'---'

def deleteOld(md5):
    try:
        #For debugging purpose, put the hash of the firmware you're testing here to automatically delete it from the db everytime
        if md5 == "51eddc7046d77a752ca4b39fbda50aff":
            print "[Testing] Removing existing firmware (hash 51eddc7046d77a752ca4b39fbda50aff)"
            Image.objects.filter(hash="51eddc7046d77a752ca4b39fbda50aff").delete()
        if md5 == "3861871dfdbacb96a26372410dcf6b07":
            print "[Testing] Removing existing firmware (hash 3861871dfdbacb96a26372410dcf6b07)"
            Image.objects.filter(hash="3861871dfdbacb96a26372410dcf6b07").delete()
        if md5 == "352bcfa477b545cdb649527d84508daf":
            print "[Testing] Removing existing firmware (hash 352bcfa477b545cdb649527d84508daf)"
            Image.objects.filter(hash="352bcfa477b545cdb649527d84508daf").delete()
        if md5 == "97a7c7fdb4a858e169cb09468bdf749e":
            print "[Testing] Removing existing firmware (hash 97a7c7fdb4a858e169cb09468bdf749e)"
            Image.objects.filter(hash="97a7c7fdb4a858e169cb09468bdf749e").delete()
    except:
        print("deleteOld failed...")


def write_file(data, path):
    """ Write data to destination (path)
    """
    with open(path, 'wb+') as destination:
        for chunk in data.chunks():
            destination.write(chunk)


def read_file(path):
    """ read data from destination (path)
    """
    data = None
    with open(path, 'r') as fd:
        data = fd.read()
    return data

def get_brand(brand_name):
    """ Return brand
    """
    b = Brand.objects.filter(name__icontains=brand_name)
    if not b:
        try:
            brand = Brand.objects.get(name="Unknown")
        except Brand.DoesNotExist:
            brand = Brand(name="Unknown")
            brand.save()
    else:
        brand = b
    return brand

@csrf_exempt
def getAnalysis(request, hash):
    """ Return treasures for a given hash
    """
    print hash
    juicy=[]
    fnames = []
    filescont = ""
    try:
        myimg=Image.objects.get(hash=hash)
        
        try:
            print("retrieving treasures for hash" + hash)
            treasures = Treasure.objects.get(oid=myimg)
            tr = ObjectToImage.objects.filter(treasure=True, iid=myimg)

            for treasure in tr:
                fnames.append(treasure.filename)

            filescont = getFileContent(fnames, myimg.id)

            juicy.append(treasures.ip)
            juicy.append(treasures.mail)
            juicy.append(treasures.uri)

        except Treasure.DoesNotExist:
            fnames = []

        return JsonResponse({"imageFileName": myimg.filename,
                             "hash": myimg.hash,
                             "status": myimg.status,
                             "hierarchy": myimg.hierarchy,
                             "juicy": juicy,
                             "filenames": fnames,
                             "arch": myimg.arch,
                             "rootfs_extracted": myimg.rootfs_extracted,
                             "status": myimg.status,
                             "fileContent": filescont,
                             "filesize": myimg.filesize,
                             "brand":str(myimg.brand.name)}, safe=False)

    except Image.DoesNotExist:
        return JsonResponse({"error": "image not found"}, safe=False)


@csrf_exempt
def getLatest(request):
    """ Return lasts images
    """
    lasts = Image.objects.all().values("filename","hash","brand__name")
    return JsonResponse(list(lasts), safe=False)


@csrf_exempt
def getFileById(request, id):
    """ To get more information about a particular file
    """
    obj = ObjectToImage.objects.get(id=id)
    return JsonResponse({"id": obj.id,
                         "permissions": obj.permissions,
                         "gid": obj.gid,
                         "uid": obj.uid,
                         "r2i": obj.r2i,
                         "insecure": obj.insecure})


def getFileContent(filenames,iid):
    """ For now let's just take some file in tmp
        but later the files should be on aws or something
    """
    path='/tmp/'+str(iid)
    os.chdir(path)
    rez=[]
    print(filenames)
    for fn in filenames:
        rez.append(read_file(path+fn))
    return rez

def emul(arch,iid):
    #what could go wrong? :^ )
    outp3=subprocess.call(["sudo","./scripts/makeImage.sh", iid, arch])
    outp3=subprocess.call(["sudo","./scripts/inferNetwork.sh", iid, arch])
    print(outp2)
    print(outp3)

    #run the fw
    # outp4=subprocess.call(["sudo","./scratch/"+iid+"/run.sh"])
    # print(outp4)


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

@csrf_exempt
def search(request):
    try:
        k = request.GET.get('keyword', False);
        if k is False:
            return JsonResponse({"Error": "missing keyword argument"})

        firmwares = Image.objects.filter(Q(filename__icontains=k) | 
                                         Q(description__icontains=k) | 
                                         Q(brand__name__icontains=k)).values("hash", "description", "brand__name", "filename")
        print firmwares
        response = []
        for firmware in firmwares:
            response.append({"hash": firmware["hash"],
                             "brand": firmware["brand__name"],
                             "filename": firmware["filename"],
                             "description": firmware["description"]})
        return JsonResponse({"results": response})

    except NotImplementedError:
        return JsonResponse({"Error": "unknown error"})

@csrf_exempt
def upload(request):

    if not request.method == 'POST':
        return HttpResponse("POST only")

    if not 'file' in request.FILES:
        return HttpResponse("No file")


    desc = request.POST['description']
    brand = request.POST['brand']
    vers = request.POST['version']
    mode = request.POST['model']
    f = request.FILES['file']
    file_name = f.name

    path = settings.UPLOAD_DIR + file_name
    write_file(f, path)

    md5 = Extractor.io_md5(path)

    brand_obj = get_brand(brand)
    brand_id = brand_obj.id
    print("Brand: " + str(brand_id))
    deleteOld(md5)
    image = Image(filename = file_name,
                  description = desc,
                  brand_id = brand_id,
                  hash = md5,
                  rootfs_extracted=False,
                  kernel_extracted=False)

    fsize = sizeof_fmt(os.path.getsize(path))
    image.filesize = fsize
    try:
        image.save()
        return JsonResponse({"status": "new", "hash": md5})
    except IntegrityError:
        # Firmware already processed
        #return JsonResponse({"status": "repost", "hash": md5})
        print ("repost")
