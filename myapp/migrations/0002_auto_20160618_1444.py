# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='objecttoimage',
            name='r2i',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='hierarchy',
            field=models.TextField(null=True, blank=True),
        ),
    ]
