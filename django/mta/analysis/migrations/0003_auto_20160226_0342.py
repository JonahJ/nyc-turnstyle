# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-26 03:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0002_auto_20160226_0322'),
    ]

    operations = [
        migrations.AddField(
            model_name='stats',
            name='cummulative_flow',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='stats',
            name='entries',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='stats',
            name='exits',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='stats',
            name='net_flow',
            field=models.IntegerField(blank=True, default=0),
        ),
        migrations.AddField(
            model_name='stats',
            name='net_time',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
