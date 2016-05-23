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
from myapp.models import Image, Product, Brand
from django.conf import settings
import hashlib



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



def run(cmd):
  """Runs the given command locally and returns the output, err and exit_code."""
  if "|" in cmd:    
    cmd_parts = cmd.split('|')
    print cmd_parts
  else:
    cmd_parts = []
    cmd_parts.append(cmd)
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
      # Be happy :D
      print output



def test(request):
    path='/tmp/111'
    os.chdir(path)
    output, err, exit_code = run('grep -sRIEho "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" "/tmp/111" | sort | uniq')
    print_rez_cmd(exit_code,output,err)
    ips = output
    output2, err, exit_code = run('grep -sRIEoh ([[:alnum:]_.-]+@[[:alnum:]_.-]+?\.[[:alpha:].]{2,6}) "/tmp/111" | sort | uniq ')
    print_rez_cmd(exit_code,output2,err)
    addy=output2

    #fuck this one, some escaping error...comes from shlex I think
    # output, err, exit_code = run('grep -sRIEoh "(http|https)://[^/""]+" "/tmp/111" | sort | uniq ')
    # print_rez_cmd(exit_code,output,err)
    return JsonResponse({"ip": output, "mail":addy})


#lame find, probably won't use
# def test(s): 
#     path='/tmp/111'
#     patterns=['*.conf','*.cfg','*.ini','*.db','*.sqlite','*psk','*.pem','*.crt','*cer','*.key']
#     result = []
#     result = []
#     for root, dirs, files in os.walk(path):
#         for name in files:
#             if any(fnmatch.fnmatch(name, pattern) for pattern in patterns):
#                 print root,name

#     print result
#     print "heey"
#     return HttpResponse(result)


#Decompress extracted in tmp for analysis
def extract_tar_tmp(id):
    fname=str(id)+'.tar.gz'
    path='/tmp/'+fname
    tt = tarfile.open(settings.EXTRACTED_DIR+fname)
    tt.extractall(path)
    return path

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
    image = Image(filename=f.name,description=desc,brand_id=brand,hash=md5, rootfs_extracted=False, kernel_extracted=False)
    image.save()
    FILE_PATH = unicodedata.normalize('NFKD', settings.UPLOAD_DIR+image.filename).encode('ascii','ignore')

    #Add a product related to the image (commtented for easier debugging)
    # product = Product(iid=image,product=mode,version=vers)
    # product.save()    
    # print image
    # print product

    #rootfs=True, parallel=False, ,kernel=False, 
    print(brand)
    print(image.id)
    extract = Extractor(FILE_PATH, settings.EXTRACTED_DIR, True, False, False, '127.0.0.1' ,"Netgear")
    extract.extract()
    #extract_tar_tmp(image.id)

    os.chdir(settings.BASE_DIR)
    curimg=str(image.id)+".tar.gz"
    #run("./lib/getArch.sh ./extracted/"+curimg)
    outp = subprocess.check_output("./lib/getArch.sh ./extracted/"+curimg, shell=True)
    res = outp.split()

    tar2db(str(image.id),'./extracted/'+curimg)
    print(res)
    print("Architecture: "+res[0])
    print("IID: "+res[1])
    return HttpResponse("File uploaded // hash : %s" % md5)