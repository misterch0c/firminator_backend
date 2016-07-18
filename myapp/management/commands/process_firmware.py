from django.core.management.base import BaseCommand, CommandError
from subprocess import Popen, PIPE
import string
import unicodedata
import shlex
import fnmatch
from myapp.models import Image, Object, ObjectToImage, Treasure
import subprocess
from lib.extractor import Extractor
import json
import tarfile
from lib.tar2db import tar2db, isElf
from django.conf import settings
import os
from lib.util import parseFilesToHierarchy
import shutil
import uuid

class Command(BaseCommand):
    help = 'process firmware'

    def handle(self, *args, **options):
        try:
            firmware = Image.objects.filter(status="waiting")[0]
            self.process(firmware)

        except IndexError:
            self.stdout.write("No waiting firmwares")

    def process(self, image):
        self.set_image_status(image, "processing")


        FILE_PATH = unicodedata.normalize('NFKD', unicode(settings.UPLOAD_DIR+image.filename)).encode('ascii','ignore')
        self.stdout.write("Image ID: "+str(image.id))

        #Extract filesystem from firmware file
        self.stdout.write(FILE_PATH)
        self.stdout.write(settings.EXTRACTED_DIR)
        try:
            brand_obj = image.brand
            extract = Extractor(FILE_PATH, settings.EXTRACTED_DIR, True, False, False, '127.0.0.1' ,brand_obj.name)
            self.stdout.write('extract--------------------------//')
            #We should handle possible errors here
            extract.extract()
            os.chdir(settings.BASE_DIR)
            curimg=str(image.id)+".tar.gz"
            self.extract_tar_tmp(image.id)
        except NotImplementedError:
            self.set_image_status(image, "extract failed")
            self.stdout.write("Error")

        self.set_image_status(image, "30")

        self.stdout.write(os.getcwd())

        iid, files2oids, links, cur = tar2db(str(image.id),'./extracted/'+curimg)
        files = self.object_to_img(iid,files2oids,links)
        hierarchy = parseFilesToHierarchy(files)   

        image.hierarchy = "[" + (', '.join([json.dumps(x) for x in hierarchy])) + "]"
        image.save()
        #Get architecture and add it in db 

        self.set_image_status(image, "60")

        try:
            outp = subprocess.check_output("./lib/getArch.sh extracted/"+curimg, shell=True)
            self.find_treasures(image)
            self.grepfs(image)

            res = outp.split()
            self.stdout.write("Architecture: "+res[0])
            self.stdout.write("IID: "+res[1])
            self.stdout.write('----------------------')
        except subprocess.CalledProcessError as e:
            self.set_image_status(image, "arch detection failed")
            self.stdout.write("GetArch failed a bit...")

        self.set_image_status(image, "done")

    def set_image_status(self, image, status):
        image.status = status
        image.save()

    #Decompress extracted in tmp for analysis
    def extract_tar_tmp(self, id):
        fname=str(id)+'.tar.gz'
        path='/tmp/'+str(id)+"/"
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

    def object_to_img(self, iid,files2oids,links):
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

    def isText(self, filename,iid):
        """ Check if file content is printable (text)
        """
        with open("/tmp/"+str(iid)+filename) as fd:
            data = fd.read(512)
            return all(c in string.printable for c in data)

    def find_treasures(self, image): 
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
                    self.stdout.write(goodpath)
                    self.stdout.write("is ELF : %s " % isElf(goodpath,image.id))
                    self.stdout.write("is text : %s" % self.isText(goodpath,image.id))
                    #Maybe merge those two in one function?
                    if(isElf(goodpath,image.id)==False and self.isText(goodpath,image.id)==True):
                        result.append(goodpath)
        #print result
        self.stdout.write('find treasures')
        self.save_treasures(result,image)


    def save_treasures(self, treasures,image):
        fnames = ""
        self.stdout.write('save treasures')
        self.stdout.write(','.join(treasures))
        for fname in treasures:
            self.stdout.write('-------------')
            ojj = ObjectToImage.objects.get(iid=image, filename=fname)
            ojj.treasure=True
            ojj.save()


    def grepfs(self, img):
        """
        grep in filesystem for passwords, emails.. and add it in database
        """
        self.stdout.write("--grepfs--")
        myimg = img
        path='/tmp/'+str(img.id)
        os.chdir(path)

        #TODO: remove all useless ip like broadcast & find a way to get the file/path too
        arg1=['grep -sRIEho "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}" '+path,'sort','uniq']
        output, err, exit_code = self.run(arg1)
        arg2=['grep -sRIEoh ([[:alnum:]_.-]+@[[:alnum:]_.-]+?\.[[:alpha:].]{2,6}) '+path,'sort','uniq']
        output2, err, exit_code = self.run(arg2)
        #had to modify run because of the | in the third one
        arg3=['grep -sRIEoh "(http|https)://[^/]+" '+path,'sort','uniq']
        output3, err, exit_code = self.run(arg3)

        ips=output.split()
        addy=output2.split()
        uris=output3.split()

        t, created=Treasure.objects.get_or_create(oid=img)
        t.ip=', '.join([str(x) for x in ips])
        t.mail=', '.join([str(x) for x in addy])
        t.uri=', '.join([str(x) for x in uris])
        t.save()

    def run(self, cmd_parts):
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
