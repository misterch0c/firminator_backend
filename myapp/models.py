# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = True` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class Brand(models.Model):
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = True
        db_table = 'brand'


class Image(models.Model):
    id = models.AutoField(primary_key=True)
    filename = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True, null=True)
    brand = models.ForeignKey(Brand)
    hash = models.CharField(unique=True, max_length=255, blank=True, null=True)
    rootfs_extracted = models.NullBooleanField()
    kernel_extracted = models.NullBooleanField()
    arch = models.CharField(max_length=255, blank=True, null=True)
    kernel_version = models.CharField(max_length=255, blank=True, null=True)
    hierarchy = models.TextField(blank = True, null = True)
    filesize = models.TextField(blank = True, null = True)

    def __str__(self):
        return '%s %s %s %s %s %s' % (self.id, self.filename, self.brand, self.hash, self.rootfs_extracted,self.hierarchy)
    class Meta:
        managed = True
        db_table = 'image'


class Treasure(models.Model):
    oid = models.ForeignKey(Image, db_column='oid',default=None)
    ip = models.TextField(unique=True, blank=True, null=True)
    mail = models.TextField(unique=True, blank=True, null=True)
    uri = models.TextField(unique=True, blank=True, null=True)

    def __str__(self):
        return '%s' % (self.ip)
    class Meta:
        managed = True
        db_table = 'treasure'

class Object(models.Model):
    hash = models.CharField(unique=True, max_length=255, blank=True, null=True)

    def __str__(self):
        return '%s' % (self.hash)
    class Meta:
        managed = True
        db_table = 'object'


class ObjectToImage(models.Model):
    oid = models.ForeignKey(Object, db_column='oid')
    iid = models.ForeignKey(Image, db_column='iid')
    filename = models.CharField(max_length=255)
    regular_file = models.NullBooleanField()
    permissions = models.IntegerField(blank=True, null=True)
    uid = models.IntegerField(blank=True, null=True)
    gid = models.IntegerField(blank=True, null=True)
    content = models.TextField(null=True) #new field for file content
    treasure = models.BooleanField(default=False)
    r2i = models.TextField(null=True) #field for radar ii 
    insecure = models.TextField(null=True)  

    def __str__(self):
        return '%s %s %s %s %s %s' % (self.iid, self.filename, self.regular_file,
        self.permissions, self.uid, self.gid)

    class Meta:
        managed = True
        db_table = 'object_to_image'
        #unique_together = (('oid', 'iid', 'filename'),)


class Product(models.Model):
    iid = models.ForeignKey(Image, db_column='iid')
    url = models.CharField(max_length=255)
    mib_hash = models.CharField(max_length=255, blank=True, null=True)
    mib_url = models.CharField(max_length=255, blank=True, null=True)
    sdk_hash = models.CharField(max_length=255, blank=True, null=True)
    sdk_url = models.CharField(max_length=255, blank=True, null=True)
    product = models.CharField(max_length=255, blank=True, null=True)
    version = models.CharField(max_length=255, blank=True, null=True)
    build = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    mib_filename = models.CharField(max_length=255, blank=True, null=True)
    sdk_filename = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return '%s %s %s' % (self.iid, self.product, self.version)

    class Meta:
        managed = True
        db_table = 'product'
        #unique_together = (('iid', 'product', 'version', 'build'),)
