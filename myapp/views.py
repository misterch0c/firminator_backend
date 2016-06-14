import subprocess
import unicodedata
import os, fnmatch
import tarfile
import shlex    
from django.http import JsonResponse
from subprocess import Popen, PIPE
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from lib.extractor import Extractor, ExtractionItem
from lib.tar2db import tar2db
from django.http import HttpResponse
from myapp.models import Image, Product, Brand, ObjectToImage, Object, Treasure
from django.conf import settings
import hashlib
from django.core import serializers
import json
from lib.util import parseFilesToHierarchy
from django.core.files import File




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


def print_rez_cmd(exit_code,output,err):
    if exit_code != 0:
      print "Output:"
      print output
      # print "Error:"
      # print exit_code
      # print err
      # Handle error here
    else:
      print output

@csrf_exempt
def getAnalysis(request): 
    """ return treasures for a given hash """
    hsh= json.loads(request.body).get('hash', None)
    #hsh = request.POST['hash']
    juicy=[]
    print request
    #print(hsh)

    myimg=Image.objects.get(hash=hsh)
    print("retrieving trasures for hash" + hsh)
    trz=Treasure.objects.get(oid=myimg)
    tr=ObjectToImage.objects.filter(treasure=True)
    fnames=[]
    for trez in tr:
        fnames.append(trez.filename)
    #print fnames
    filescont=getFileContent(fnames)
    juicy.append(trz.ip)
    juicy.append(trz.mail)
    juicy.append(trz.uri)


    return JsonResponse({"imageFileName":myimg.filename,"hash":myimg.hash,"hierarchy":myimg.hierarchy,
        "juicy":juicy,"filenames":fnames,
        "arch":myimg.arch, "rootfs_extracted":myimg.rootfs_extracted,
        "fileContent":filescont}, safe=False)

def getFileContent(filenames):
    """For now let's just take some file in tmp but later the files should be on aws or something"""
    path='/tmp/111'
    os.chdir(path)
    rez=[]
    for fn in filenames:
        #print(path+fn)
        content=open(path+fn,'r')
        rez.append(content.read())
    #print(rez)
    return rez




#grep in filesystem for passwords, emails.. and add it in database
def grepfs(img):
    print("--grepfs--")
    #path = request.POST['path']
    #myimg=Image.objects.get(hash="51eddc7046d77a752ca4b39fbda50aff")
    myimg=img
    path='/tmp/111'
    os.chdir(path)

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


def test(request):

    return "sup"

def find_treasures(image): 
    path='/tmp/111'
    patterns=['passwd','shadow','*.conf','*.cfg','*.ini','*.db','*.sqlite','*psk','*.pem','*.crt','*cer','*.key']
    result = []
    for root, dirs, files in os.walk(path):
        for name in files:
            if any(fnmatch.fnmatch(name, pattern) for pattern in patterns):
                tmppath=root+"/"+name
                goodpath="/"+os.path.relpath(tmppath, '/tmp/111')
                print(goodpath)
                result.append(goodpath)
    #print result
    print('find treasures')
    #print(result)
    rez=parse_treasures(result)
    save_treasures(rez,image)

def parse_treasures(result):
    print('oooo')
    print(result)
    patterns=['*.conf','*.txt','/etc/shadow','/etc/passwd']
    result2=[]
    for filename in result:
        if any(fnmatch.fnmatch(filename,pattern) for pattern in patterns):
            # print('_________')
            # print(filename)
            result2.append(filename)
    #print(result2)
    return result2


def save_treasures(treasures,image):
    fnames=""
    print('save treasures')
    for fname in treasures:
        ojj=ObjectToImage.objects.get(iid=image,filename=fname)
        ojj.treasure=True
        ojj.save()
        print(ojj.filename)

#Decompress extracted in tmp for analysis
def extract_tar_tmp(id):
    fname=str(id)+'.tar.gz'
    path='/tmp/'+fname
    tt = tarfile.open(settings.EXTRACTED_DIR+fname)
    tt.extractall(path)
    return path


def object_to_img(iid,files2oids,links):
        for x in files2oids:
            oj = Object.objects.get(id=x[1])
            imj = Image.objects.get(id=iid)
           # print x[1] 
            ojtimj= ObjectToImage(iid=imj, oid=oj,filename=x[0][0], regular_file=True, uid=x[0][1], gid=x[0][2], permissions=x[0][3])
            ojtimj.save()

        for x in links:
            oj2 = Object.objects.get(id=1)
            imj2 = Image.objects.get(id=iid)
            li = ObjectToImage(iid=imj2, oid=oj2, filename=x[0],regular_file=False)
            li.save()  

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
    path = settings.UPLOAD_DIR + f.name
    handle_uploaded_file(f, path)
    md5 = Extractor.io_md5(path)
    brand=get_brand(brnd)
    print("Brand: " + str(brand))
    image = Image(filename=f.name,description=desc,brand_id=brand,hash=md5, rootfs_extracted=False, kernel_extracted=False)
    image.save()
    FILE_PATH = unicodedata.normalize('NFKD', settings.UPLOAD_DIR+image.filename).encode('ascii','ignore')

    #Add a product related to the image (commtented for easier debugging)
    # product = Product(iid=image,product=mode,version=vers)
    # product.save()    
    # print image
    # print product

    #rootfs=True, parallel=False, ,kernel=False, 
    print("Image ID: "+str(image.id))

    #Extract filesystem from firmware file
    extract = Extractor(FILE_PATH, settings.EXTRACTED_DIR, True, False, False, '127.0.0.1' ,"Netgear")
    extract.extract()

    #To decompress .tar.gz in /tmp
    #extract_tar_tmp(image.id)

    os.chdir(settings.BASE_DIR)
    curimg=str(image.id)+".tar.gz"
    
    #Get architecture and add it in db 
    outp = subprocess.check_output("./lib/getArch.sh ./extracted/"+curimg, shell=True)
    res = outp.split()
    iid, files2oids, links, cur = tar2db(str(image.id),'./extracted/'+curimg)

    #Get file hierarchy and save it in db
    hierarchy = parseFilesToHierarchy(files2oids, links)    
    #print(hierarchy)
    image.hierarchy = ', '.join([str(x) for x in hierarchy])
    image.save()

    #Add filenames/path in db
    object_to_img(iid,files2oids,links)

    find_treasures(image)
    grepfs(image)

    print("Architecture: "+res[0])
    print("IID: "+res[1])
    return HttpResponse("File uploaded // hash : %s" % md5)