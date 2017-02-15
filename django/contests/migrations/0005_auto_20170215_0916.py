# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-15 09:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contests', '0004_auto_20170215_0908'),
    ]

    operations = [
        migrations.AddField(
            model_name='twitteruser',
            name='contributors_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='twitteruser',
            name='created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='twitteruser',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='twitteruser',
            name='followers_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='twitteruser',
            name='friends_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='twitteruser',
            name='is_translator',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='twitteruser',
            name='profile_banner_url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='twitteruser',
            name='protected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='twitteruser',
            name='screen_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='twitteruser',
            name='statuses_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='twitteruser',
            name='url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='twitteruser',
            name='location',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='twitteruser',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='twitteruser',
            name='profile_image_url',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='twitteruser',
            name='twitter_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
