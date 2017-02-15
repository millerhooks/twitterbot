from __future__ import unicode_literals

from django.db import models
from TwitterAPI import TwitterAPI
import threading
import time
import json
import os.path
import sys

__admin__ = [
    'SearchQuery',
    'FollowKeyword',
    'FavoriteKeyword',
    'Bot',
    'TwitterUser',
    'BotRelationship'
]

BOT_STATUS_CHOICES = (
    ('0', 'New'),
    ('1', 'Processed'),
    ('2', 'Reprocess'),
    ('x', 'Failed')
)


class SearchQuery(models.Model):
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class FollowKeyword(models.Model):
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class FavoriteKeyword(models.Model):
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.text


class Bot(models.Model):
    name = models.CharField(max_length=255)
    photo = models.FileField(blank=True, upload_to="bots/photos")
    status = models.CharField(max_length=1, choices=BOT_STATUS_CHOICES, blank=True, default='0')
    retweet_list = models.TextField(blank=True)
    retweet_follow_list = models.TextField(blank=True)

    consumer_key = models.CharField(max_length=255)
    consumer_secret = models.CharField(max_length=255)
    access_token_key = models.CharField(max_length=255)
    access_token_secret = models.CharField(max_length=255)
    retweet_update_time = models.IntegerField(default=1300, help_text="how often to update retweets")
    scan_update_time = models.IntegerField(default=1500, help_text="how often to scan for contest tweets")
    rate_limit_update_time = models.IntegerField(default=10, help_text="how often to scan for contest tweets")

    min_ratelimit = models.IntegerField(default=10, help_text="minimum rate limit")
    min_ratelimit_retweet = models.IntegerField(default=20, help_text="minimum rate limit for retweets")
    min_ratelimit_search = models.IntegerField(default=40, help_text="minimum rate limit for search")

    search_queries = models.ManyToManyField(SearchQuery)
    follow_keywords = models.ManyToManyField(FollowKeyword)
    fav_keywords = models.ManyToManyField(FavoriteKeyword)

    @property
    def ignore_list(self):
        return BotRelationship.objects.filter(bot=self)

    @property
    def retweet_follow_list(self):
        return BotRelationship.objects.filter(bot=self)


    def connect(self):
        # Don't edit these unless you know what you're doing.
        self.api = TwitterAPI(self.consumer_key, self.consumer_secret, self.access_token_key, self.access_token_secret)
        post_list = list()
        ratelimit = [999, 999, 100]
        ratelimit_search = [999, 999, 100]

    def log_and_print(self, text):
        tmp = str(text)
        tmp = text.replace("\n", "")
        print(tmp)
        f_log = open('log', 'a')
        f_log.write(tmp + "\n")
        f_log.close()

    def check_error(self, res):
        res = res.json()
        if 'errors' in res:
            self.log_and_print("We got an error message: "
                               + res['errors'][0]['message'] +
                               " Code: "
                               + str(res['errors'][0]['code']))
            # sys.exit(r['errors'][0]['code'])

    def check_rate_limit(self):
        c = threading.Timer(self.rate_limit_update_time, self.check_rate_limit)
        c.daemon = True
        c.start()

        global ratelimit
        global ratelimit_search

        if ratelimit[2] < self.min_ratelimit:
            print("Ratelimit too low -> Cooldown (" + str(ratelimit[2]) + "%)")
            time.sleep(30)

        r = self.api.request('application/rate_limit_status').json()

        for res_family in r['resources']:
            for res in r['resources'][res_family]:
                limit = r['resources'][res_family][res]['limit']
                remaining = r['resources'][res_family][res]['remaining']
                percent = float(remaining) / float(limit) * 100

                if res == "/search/tweets":
                    ratelimit_search = [limit, remaining, percent]

                if res == "/application/rate_limit_status":
                    ratelimit = [limit, remaining, percent]

                # print(res_family + " -> " + res + ": " + str(percent))
                if percent < 5.0:
                    self.log_and_print(res_family + " -> " + res + ": " + str(percent) + "  !!! <5% Emergency exit !!!")
                    sys.exit(res_family + " -> " + res + ": " + str(percent) + "  !!! <5% Emergency exit !!!")
                elif percent < 30.0:
                    self.log_and_print(res_family + " -> " + res + ": " + str(percent) + "  !!! <30% alert !!!")
                elif percent < 70.0:
                    print(res_family + " -> " + res + ": " + str(percent))

    # TODO: <Miller> Make the stuff below here, look like the stuff up there.

    def update_queue(self):
        u = threading.Timer(self.retweet_update_time, self.update_qQueue)
        u.daemon = True
        u.start()

        print("=== CHECKING RETWEET QUEUE ===")

        print("Queue length: " + str(len(self.post_list)))

        if len(self.post_list) > 0:

            if not ratelimit[2] < self.min_ratelimit_retweet:

                post = post_list[0]
                self.log_and_print("Retweeting: " + str(post['id']) + " " + str(post['text'].encode('utf8')))

                CheckForFollowRequest(post)
                CheckForFavoriteRequest(post)

                r = api.request('statuses/retweet/:' + str(post['id']))
                CheckError(r)
                post_list.pop(0)

            else:

                print("Ratelimit at " + str(ratelimit[2]) + "% -> pausing retweets")




    # Check if a post requires you to follow the user.
    # Be careful with this function! Twitter may write ban your application for following too aggressively
    def CheckForFollowRequest(self, item):
        text = item['text']
        if any(x in text.lower() for x in follow_keywords):
            try:
                r = api.request('friendships/create', {'screen_name': item['retweeted_status']['user']['screen_name']})
                CheckError(r)
                LogAndPrint("Follow: " + item['retweeted_status']['user']['screen_name'])
            except:
                user = item['user']
                screen_name = user['screen_name']
                r = api.request('friendships/create', {'screen_name': screen_name})
                CheckError(r)
                LogAndPrint("Follow: " + screen_name)

    # Check if a post requires you to favorite the tweet.
    # Be careful with this function! Twitter may write ban your application for favoriting too aggressively
    def CheckForFavoriteRequest(self, item):
        text = item['text']

        if any(x in text.lower() for x in fav_keywords):
            try:
                r = api.request('favorites/create', {'id': item['retweeted_status']['id']})
                CheckError(r)
                LogAndPrint("Favorite: " + str(item['retweeted_status']['id']))
            except:
                r = api.request('favorites/create', {'id': item['id']})
                CheckError(r)
                LogAndPrint("Favorite: " + str(item['id']))

    # Scan for new contests, but not too often because of the rate limit.
    def ScanForContests(self):

        t = threading.Timer(scan_update_time, ScanForContests)
        t.daemon = True;
        t.start()

        global ratelimit_search

        if not ratelimit_search[2] < min_ratelimit_search:

            print("=== SCANNING FOR NEW CONTESTS ===")

            for search_query in search_queries:

                print("Getting new results for: " + search_query)

                try:
                    r = api.request('search/tweets', {'q': search_query, 'result_type': "mixed", 'count': 100})
                    CheckError(r)
                    c = 0

                    for item in r:
                        c = c + 1
                        user_item = item['user']
                        screen_name = user_item['screen_name']
                        text = item['text']
                        text = text.replace("\n", "")
                        id = str(item['id'])
                        original_id = id
                        is_retweet = 0

                        if 'retweeted_status' in item:
                            is_retweet = 1
                            original_item = item['retweeted_status']
                            original_id = str(original_item['id'])
                            original_user_item = original_item['user']
                            original_screen_name = original_user_item['screen_name']

                            if not original_id in ignore_list:

                                if not original_screen_name in ignore_list:

                                    if not screen_name in ignore_list:

                                        if item['retweet_count'] > 0:

                                            post_list.append(item)
                                            f_ign = open('ignorelist', 'a')

                                            if is_retweet:
                                                print(
                                                    id + " - " + screen_name + " retweeting " + original_id + " - " + original_screen_name + ": " + text)
                                                ignore_list.append(original_id)
                                                f_ign.write(original_id + "\n")
                                            else:
                                                print(id + " - " + screen_name + ": " + text)
                                                ignore_list.append(id)
                                                f_ign.write(id + "\n")

                                            f_ign.close()

                                else:

                                    if is_retweet:
                                        print(id + " ignored: " + original_screen_name + " on ignore list")
                                    else:
                                        print(original_screen_name + " in ignore list")

                            else:

                                if is_retweet:
                                    print(id + " ignored: " + original_id + " on ignore list")
                                else:
                                    print(id + " in ignore list")

                    print("Got " + str(c) + " results")

                except Exception as e:
                    # print("Could not connect to TwitterAPI - are your credentials correct?")
                    print("Exception: " + str(e))

        else:

            print(
            "Search skipped! Queue: " + str(len(post_list)) + " Ratelimit: " + str(ratelimit_search[1]) + "/" + str(
                ratelimit_search[0]) + " (" + str(ratelimit_search[2]) + "%)")

    def run_bot(self):
        CheckRateLimit()
        ScanForContests()
        UpdateQueue()

        while (True):
            time.sleep(1)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class TwitterUser(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField(max_length=255, blank=True, null=True)
    photo = models.FileField(blank=True, upload_to="twits/photos")

    def __str__(self):
        return self.text

BOT_RELATIONSHIP_STATUS_CHOICES = (
    ('0', 'Ignored'),
    ('1', 'Followed')
)


class BotRelationship(TwitterUser):
    bot = models.ForeignKey(Bot)
    status = models.CharField(max_length=1, choices=BOT_RELATIONSHIP_STATUS_CHOICES, blank=True, default='1')

    def __str__(self):
        return self.text