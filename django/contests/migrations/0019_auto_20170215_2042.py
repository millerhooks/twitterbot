# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-15 20:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0018_auto_20170215_2040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tweet',
            name='created_at',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='twitteruser',
            name='created_at',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
