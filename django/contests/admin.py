from django.contrib import admin

from . import models


class TweetInline(admin.TabularInline):
    list_display = ('created_at', 'id', 'text',)
    model = models.Tweet


class TwitterUserAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'id', 'name',)
    model = models.TwitterUser
    inlines = [TweetInline]


class TweetAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'id', 'user',)


class BotAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'tweets_in_queue')
    filter_horizontal = ('search_queries', 'follow_keywords',
                         'fav_keywords', 'retweet_list',
                         'favorited_list', 'ignore_list',
                         'retweet_follow_list', 'post_list', 'tweet_generator')

    def tweets_in_queue(self, obj):
        return len(obj.post_list.all())


class LogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'type', 'event')

__custom_admins__ = {
    "Bot": BotAdmin,
    "TwitterUser": TwitterUserAdmin,
    "Tweet": TweetAdmin,
    "Mention": TweetAdmin,
    "Log": LogAdmin
}

for model in models.__admin__:
    params = [getattr(models, model)]
    if model in __custom_admins__:
        params.append(__custom_admins__[model])
    else:
        _dyn_class = type('%sAdmin' % ( model,), (admin.ModelAdmin,), {})
        params.append(_dyn_class)
    admin.site.register(*params)
