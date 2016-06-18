# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AuthGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=80)),
            ],
            options={
                'db_table': 'auth_group',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthGroupPermissions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'db_table': 'auth_group_permissions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('codename', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'auth_permission',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128)),
                ('last_login', models.DateTimeField(null=True, blank=True)),
                ('is_superuser', models.BooleanField()),
                ('username', models.CharField(unique=True, max_length=30)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('email', models.CharField(max_length=254)),
                ('is_staff', models.BooleanField()),
                ('is_active', models.BooleanField()),
                ('date_joined', models.DateTimeField()),
            ],
            options={
                'db_table': 'auth_user',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUserGroups',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'db_table': 'auth_user_groups',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='AuthUserUserPermissions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'db_table': 'auth_user_user_permissions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoAdminLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action_time', models.DateTimeField()),
                ('object_id', models.TextField(null=True, blank=True)),
                ('object_repr', models.CharField(max_length=200)),
                ('action_flag', models.SmallIntegerField()),
                ('change_message', models.TextField()),
            ],
            options={
                'db_table': 'django_admin_log',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoContentType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('app_label', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'django_content_type',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoMigrations',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('app', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('applied', models.DateTimeField()),
            ],
            options={
                'db_table': 'django_migrations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='DjangoSession',
            fields=[
                ('session_key', models.CharField(max_length=40, serialize=False, primary_key=True)),
                ('session_data', models.TextField()),
                ('expire_date', models.DateTimeField()),
            ],
            options={
                'db_table': 'django_session',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=255)),
            ],
            options={
                'db_table': 'brand',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('filename', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255, null=True, blank=True)),
                ('hash', models.CharField(max_length=255, unique=True, null=True, blank=True)),
                ('rootfs_extracted', models.NullBooleanField()),
                ('kernel_extracted', models.NullBooleanField()),
                ('arch', models.CharField(max_length=255, null=True, blank=True)),
                ('kernel_version', models.CharField(max_length=255, null=True, blank=True)),
                ('hierarchy', models.TextField(max_length=255, null=True, blank=True)),
                ('brand', models.ForeignKey(to='myapp.Brand')),
            ],
            options={
                'db_table': 'image',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Object',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hash', models.CharField(max_length=255, unique=True, null=True, blank=True)),
            ],
            options={
                'db_table': 'object',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ObjectToImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('filename', models.CharField(max_length=255)),
                ('regular_file', models.NullBooleanField()),
                ('permissions', models.IntegerField(null=True, blank=True)),
                ('uid', models.IntegerField(null=True, blank=True)),
                ('gid', models.IntegerField(null=True, blank=True)),
                ('content', models.TextField(null=True)),
                ('treasure', models.BooleanField(default=False)),
                ('iid', models.ForeignKey(to='myapp.Image', db_column='iid')),
                ('oid', models.ForeignKey(to='myapp.Object', db_column='oid')),
            ],
            options={
                'db_table': 'object_to_image',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=255)),
                ('mib_hash', models.CharField(max_length=255, null=True, blank=True)),
                ('mib_url', models.CharField(max_length=255, null=True, blank=True)),
                ('sdk_hash', models.CharField(max_length=255, null=True, blank=True)),
                ('sdk_url', models.CharField(max_length=255, null=True, blank=True)),
                ('product', models.CharField(max_length=255, null=True, blank=True)),
                ('version', models.CharField(max_length=255, null=True, blank=True)),
                ('build', models.CharField(max_length=255, null=True, blank=True)),
                ('date', models.DateTimeField(null=True, blank=True)),
                ('mib_filename', models.CharField(max_length=255, null=True, blank=True)),
                ('sdk_filename', models.CharField(max_length=255, null=True, blank=True)),
                ('iid', models.ForeignKey(to='myapp.Image', db_column='iid')),
            ],
            options={
                'db_table': 'product',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Treasure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.TextField(unique=True, null=True, blank=True)),
                ('mail', models.TextField(unique=True, null=True, blank=True)),
                ('uri', models.TextField(unique=True, null=True, blank=True)),
                ('oid', models.ForeignKey(db_column='oid', default=None, to='myapp.Image')),
            ],
            options={
                'db_table': 'treasure',
                'managed': True,
            },
        ),
    ]
