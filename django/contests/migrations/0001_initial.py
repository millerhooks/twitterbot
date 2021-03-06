# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-02-15 08:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('photo', models.FileField(blank=True, upload_to='bots/photos')),
                ('status', models.CharField(blank=True, choices=[('0', 'New'), ('1', 'Processed'), ('2', 'Reprocess'), ('x', 'Failed')], default='0', max_length=1)),
                ('consumer_key', models.CharField(max_length=255)),
                ('consumer_secret', models.CharField(max_length=255)),
                ('access_token_key', models.CharField(max_length=255)),
                ('access_token_secret', models.CharField(max_length=255)),
                ('retweet_update_time', models.IntegerField(default=1300, help_text='how often to update retweets')),
                ('scan_update_time', models.IntegerField(default=1500, help_text='how often to scan for contest tweets')),
                ('rate_limit_update_time', models.IntegerField(default=10, help_text='how often to scan for contest tweets')),
                ('min_ratelimit', models.IntegerField(default=10, help_text='minimum rate limit')),
                ('min_ratelimit_retweet', models.IntegerField(default=20, help_text='minimum rate limit for retweets')),
                ('min_ratelimit_search', models.IntegerField(default=40, help_text='minimum rate limit for search')),
            ],
        ),
        migrations.CreateModel(
            name='FavoriteKeyword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='FollowKeyword',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='SearchQuery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('in_reply_to_screen_name', models.CharField(blank=True, max_length=255)),
                ('in_reply_to_status_id', models.IntegerField(blank=True, null=True)),
                ('contributors', models.CharField(max_length=255)),
                ('is_quote_status', models.BooleanField(default=False)),
                ('in_reply_to_status_id_str', models.CharField(max_length=255)),
                ('place', models.CharField(max_length=255)),
                ('post_id', models.IntegerField(blank=True, null=True)),
                ('favorited', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(blank=True, null=True)),
                ('retweet_count', models.IntegerField(blank=True, null=True)),
                ('retweeted', models.BooleanField(default=False)),
                ('coordinates', models.CharField(blank=True, max_length=255)),
                ('source', models.CharField(blank=True, max_length=255)),
                ('lang', models.CharField(blank=True, max_length=255)),
                ('favorite_count', models.IntegerField(blank=True, null=True)),
                ('geo', models.CharField(blank=True, max_length=255)),
                ('in_reply_to_user_id', models.IntegerField(blank=True, null=True)),
                ('possibly_sensitive', models.BooleanField(default=False)),
                ('truncated', models.BooleanField(default=False)),
                ('in_reply_to_user_id_str', models.CharField(blank=True, max_length=255)),
                ('id_str', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='TwitterUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('verified', models.BooleanField(default=False)),
                ('geo_enabled', models.BooleanField(default=False)),
                ('twitter_id', models.IntegerField()),
                ('location', models.CharField(max_length=255)),
                ('default_profile_image', models.BooleanField(default=False)),
                ('profile_image_url', models.CharField(max_length=255)),
                ('follow_request_sent', models.BooleanField(default=False)),
                ('following', models.BooleanField(default=False)),
                ('photo', models.FileField(blank=True, null=True, upload_to='twits/photos')),
            ],
        ),
        migrations.AddField(
            model_name='tweet',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contests.TwitterUser'),
        ),
        migrations.AddField(
            model_name='bot',
            name='fav_keywords',
            field=models.ManyToManyField(to='contests.FavoriteKeyword'),
        ),
        migrations.AddField(
            model_name='bot',
            name='favorited_list',
            field=models.ManyToManyField(related_name='favorited_list', to='contests.Tweet'),
        ),
        migrations.AddField(
            model_name='bot',
            name='follow_keywords',
            field=models.ManyToManyField(to='contests.FollowKeyword'),
        ),
        migrations.AddField(
            model_name='bot',
            name='ignore_list',
            field=models.ManyToManyField(related_name='ignore_list', to='contests.TwitterUser'),
        ),
        migrations.AddField(
            model_name='bot',
            name='retweet_follow_list',
            field=models.ManyToManyField(related_name='retweet_follow_list', to='contests.Tweet'),
        ),
        migrations.AddField(
            model_name='bot',
            name='retweet_list',
            field=models.ManyToManyField(related_name='retweet_list', to='contests.Tweet'),
        ),
        migrations.AddField(
            model_name='bot',
            name='search_queries',
            field=models.ManyToManyField(to='contests.SearchQuery'),
        ),
    ]
