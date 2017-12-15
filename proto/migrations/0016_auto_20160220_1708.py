# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-20 17:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proto', '0015_auto_20160217_0305'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photographer',
            name='categories',
        ),
        migrations.AddField(
            model_name='category',
            name='photographers',
            field=models.ManyToManyField(related_name='categories', related_query_name='category', to='proto.Photographer'),
        ),
        migrations.AddField(
            model_name='category',
            name='photos',
            field=models.ManyToManyField(related_name='categories', related_query_name='category', to='proto.Photo'),
        ),
    ]
