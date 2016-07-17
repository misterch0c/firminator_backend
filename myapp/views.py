from __future__ import division

import subprocess
import uuid
import unicodedata
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

def isText(filename,iid):
    """ Check if file content is printable (text)
    """
    with open("/tmp/"+str(iid)+filename) as fd:
        data = fd.read(512)
        return all(c in string.printable for c in data)


def get_brand(brand):
    """ Return brand id
    """
    b = Brand.objects.filter(name__icontains=brand)
    if not b:
        try:
            brand = Brand.objects.get(name="Unknown")
        except Brand.DoesNotExist:
            brand = Brand(name="Unknown")
            brand.save()
    else:
        brand = b
    return brand

def run(cmd_parts):
  """Runs the given command locally and returns the output, err and exit_code."""
  i = 0
  p = {}
  for cmd_part in cmd_parts:
    cmd_part = cmd_part.strip()
    if i == 0:
      p[i]=Popen(shlex.split(cmd_part),shell=False, stdin=None, stdout=PIPE, stderr=PIPE)
    else:
      p[i]=Popen(shlex.split(cmd_part), shell=False, stdin=p[i-1].stdout, stdout=PIPE, stderr=PIPE)
    i = i +1
  (output, err) = p[i-1].communicate()
  exit_code = p[0].wait()
  return str(output), str(err), exit_code


@csrf_exempt
def getAnalysis(request, hash):
    """ Return treasures for a given hash
    """
    print hash
    juicy=[]
    try:
        myimg=Image.objects.get(hash=hash)

        print("retrieving treasures for hash" + hash)
        treasures = Treasure.objects.get(oid=myimg)
        tr = ObjectToImage.objects.filter(treasure=True, iid=myimg)

        fnames = []
        for treasure in tr:
            fnames.append(treasure.filename)

        filescont = getFileContent(fnames, myimg.id)
        juicy.append(treasures.ip)
        juicy.append(treasures.mail)
        juicy.append(treasures.uri)

        return JsonResponse({"imageFileName": myimg.filename,
                             "hash": myimg.hash,
                             "hierarchy": myimg.hierarchy,
                             "juicy": juicy,
                             "filenames": fnames,
                             "arch": myimg.arch,
                             "rootfs_extracted": myimg.rootfs_extracted,
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


def grepfs(img):
    """
    grep in filesystem for passwords, emails.. and add it in database
    """
    print("--grepfs--")
    myimg = img
    path='/tmp/'+str(img.id)
    os.chdir(path)

    #TODO: remove all useless ip like broadcast & find a way to get the file/path too
    arg1=['grep -sRIEho "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" '+path,'sort','uniq']
    output, err, exit_code = run(arg1)
    arg2=['grep -sRIEoh ([[:alnum:]_.-]+@[[:alnum:]_.-]+?\.[[:alpha:].]{2,6}) '+path,'sort','uniq']
    output2, err, exit_code = run(arg2)
    #had to modify run because of the | in the third one
    arg3=['grep -sRIEoh "(http|https)://[^/]+" '+path,'sort','uniq']
    output3, err, exit_code = run(arg3)

    ips=output.split()
    addy=output2.split()
    uris=output3.split()

    t, created=Treasure.objects.get_or_create(oid=img)
    t.ip=', '.join([str(x) for x in ips])
    t.mail=', '.join([str(x) for x in addy])
    t.uri=', '.join([str(x) for x in uris])
    t.save()

    return JsonResponse({"ip": ips, "mail":addy, "uri":uris })


def find_treasures(image): 
    path='/tmp/'+str(image.id)

    ssl=['*.pem','*.crt','*p7b','*p12','*.cer']
    conf=['*.conf','*.cfg','*.ini']
    ssh=['authorized_keys','*authorized_keys*','host_key','*host_key*','id_rsa','*id_rsa*','id_dsa','*id_dsa*','*.pub']
    db=['*.db','*.sqlite']
    dpass=['passwd','shadow','*.psk']
    webserv=['apache','lighttpd','alphapd','httpd']
    patterns=ssl+conf+ssh+db+dpass+webserv
    result = []

    for root, dirs, files in os.walk(path):
        for name in files:
            if any(fnmatch.fnmatch(name, pattern) for pattern in patterns):
                tmppath=root+"/"+name
                goodpath="/"+os.path.relpath(tmppath, '/tmp/'+str(image.id))
                print(goodpath)
                print(isElf(goodpath,image.id))
                print(isText(goodpath,image.id))
                #Maybe merge those two in one function?
                if(isElf(goodpath,image.id)==False and isText(goodpath,image.id)==True):
                    result.append(goodpath)
    #print result
    print('find treasures')
    save_treasures(result,image)


def save_treasures(treasures,image):
    fnames = ""
    print('save treasures')
    print(treasures)
    for fname in treasures:
        print('-------------')
        ojj = ObjectToImage.objects.get(iid=image, filename=fname)
        ojj.treasure=True
        ojj.save()

#Decompress extracted in tmp for analysis
def extract_tar_tmp(id):
    fname=str(id)+'.tar.gz'
    path='/tmp/'+str(id)+"/"
    print(id)
    print(fname)
    with tarfile.open(settings.EXTRACTED_DIR+fname, 'r:gz') as tar:
        for file_ in tar:
            if file_.name in [".", ".."]:
                continue
            try:
                tar.extract(file_, path=path)
            except IOError:
                os.remove(path + file_.name)
                tar.extract(file_, path)
            finally:
                try:
                    os.chmod(path + file_.name, file_.mode)
                except:
                    """ If anyone asks, i've never wrote that
                    """
                    pass
    return path

def object_to_img(iid,files2oids,links):
        files = []
        for x in files2oids:
            oj = Object.objects.get(id=x[1])
            imj = Image.objects.get(id=iid)
            ojtimj= ObjectToImage(iid=imj, oid=oj,filename=x[0][0], regular_file=True, uid=x[0][1], gid=x[0][2], permissions=x[0][3], r2i=x[0][4],insecure=x[0][5])
            ojtimj.save()
            files.append(ojtimj)

        for x in links:
            oj2 = Object.objects.get(id=1)
            imj2 = Image.objects.get(id=iid)
            li = ObjectToImage(iid=imj2, oid=oj2, filename=x[0],regular_file=False)
            li.save()  
            files.append(li)
        return files


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
                  rootfs_extracted = False,
                  kernel_extracted=False)

    fsize = sizeof_fmt(os.path.getsize(path))
    image.filesize = fsize
    try:
        image.save()
    except IntegrityError:
        # Firmware already processed
        #return JsonResponse({"status": "repost", "hash": md5})
        print ("repost")

    FILE_PATH = unicodedata.normalize('NFKD', unicode(settings.UPLOAD_DIR+image.filename)).encode('ascii','ignore')
    #Add a product related to the image 
    # product = Product(iid=image,product=mode,version=vers)
    # product.save()    
    print("Image ID: "+str(image.id))

    
    #Extract filesystem from firmware file
    print(FILE_PATH)
    print(settings.EXTRACTED_DIR)
    try:
        extract = Extractor(FILE_PATH, settings.EXTRACTED_DIR, True, False, False, '127.0.0.1' ,brand_obj.name)
        print('extract--------------------------//')
        #We should handle possible errors here
        extract.extract()
        os.chdir(settings.BASE_DIR)
        curimg=str(image.id)+".tar.gz"
        print image.id
        extract_tar_tmp(image.id)
    except NotImplementedError:
        return JsonResponse({"error": "extract error"})

    print(os.getcwd())

    iid, files2oids, links, cur = tar2db(str(image.id),'./extracted/'+curimg)
    files = object_to_img(iid,files2oids,links)
    hierarchy = parseFilesToHierarchy(files)   
    myimg=Image.objects.get(hash=md5)

    myimg.hierarchy = "[" + (', '.join([json.dumps(x) for x in hierarchy])) + "]"
    myimg.save()
    #Get architecture and add it in db 
    try:
        outp = subprocess.check_output("./lib/getArch.sh extracted/"+curimg, shell=True)
        print(outp)
        find_treasures(image)
        grepfs(image)

        res = outp.split()
        print("Architecture: "+res[0])
        print("IID: "+res[1])
        print('----------------------')
    except subprocess.CalledProcessError as e:
        print("GetArch failed a bit...")
    """
    print(os.environ["FIRMWARE_DIR"])
    os.chdir(os.environ["FIRMWARE_DIR"])
    print(os.getcwd())
    """
    return JsonResponse({"status": "new", "hash": md5})
