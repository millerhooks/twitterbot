from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Bot(model.Model):
    title = models.CharField()
    status = models.CharField()
    retweet_list = models.ForeignKey()
    retweete_follow_list = models.ForeignKey()
    ignore_list = models.ForeignKey()


