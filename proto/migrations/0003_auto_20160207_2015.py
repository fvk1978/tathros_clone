# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-07 20:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proto', '0002_auto_20160207_1743'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='geo_location',
            new_name='geo',
        ),
    ]