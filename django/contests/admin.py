from django.contrib import admin

from . import models

class BotAdmin(admin.ModelAdmin):
    list_display = ('name', 'status',)
    filter_horizontal = ('search_queries', 'follow_keywords', 'fav_keywords', 'retweet_list', 'favorited_list', 'ignore_list', 'retweet_follow_list')

__custom_admins__ = {
    "Bot": BotAdmin,
}

for model in models.__admin__:
    params = [getattr(models, model)]
    if model in __custom_admins__:
        params.append(__custom_admins__[model])
    else:
        _dyn_class = type('%sAdmin' % ( model,), (admin.ModelAdmin,), {})
        params.append(_dyn_class)
    admin.site.register(*params)
