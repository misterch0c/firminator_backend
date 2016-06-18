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


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup)
    permission = models.ForeignKey('AuthPermission')

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        #unique_together = (('group_id', 'permission_id'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType')
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        #unique_together = (('content_type_id', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser)
    group = models.ForeignKey(AuthGroup)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        #unique_together = (('user_id', 'group_id'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser)
    permission = models.ForeignKey(AuthPermission)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        #unique_together = (('user_id', 'permission_id'),)


class Brand(models.Model):
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        managed = True
        db_table = 'brand'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', blank=True, null=True)
    user = models.ForeignKey(AuthUser)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        #unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


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

    def __str__(self):
        return '%s %s %s %s' % (self.id, self.filename, self.hash,self.hierarchy)
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
    r2i = models.TextField(null=True) #field for radar information 

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
