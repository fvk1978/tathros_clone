# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-17 03:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proto', '0014_auto_20160217_0210'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='category',
            name='disabled',
            field=models.BooleanField(default=False),
        ),
    ]