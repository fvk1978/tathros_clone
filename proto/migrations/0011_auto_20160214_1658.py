# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-14 16:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('proto', '0010_auto_20160214_1509'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhotographerSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('program', models.CharField(max_length=100)),
                ('start', models.DateField(auto_now=True)),
                ('end', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('photographer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='proto.Photographer')),
            ],
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='end',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='photographer',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='program',
        ),
        migrations.RemoveField(
            model_name='subscription',
            name='start',
        ),
        migrations.AddField(
            model_name='subscription',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='subscription',
            name='description',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='subscription',
            name='likes',
            field=models.IntegerField(default=1000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subscription',
            name='name',
            field=models.CharField(default='Subscription 1000', max_length=150),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subscription',
            name='photos',
            field=models.IntegerField(default=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='subscription',
            name='price',
            field=models.IntegerField(default=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='photographersubscription',
            name='subscription',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='proto.Subscription'),
        ),
    ]
