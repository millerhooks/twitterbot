from __future__ import unicode_literals

from django.db import models
from TwitterAPI import TwitterAPI
import sys, json, time, threading
from dateutil.parser import parse
from django.apps import apps

__admin__ = [
    'Log',
    'SearchQuery',
    'FollowKeyword',
    'FavoriteKeyword',
    'Bot',
    'TwitterUser',
    'Tweet'
]

BOT_STATUS_CHOICES = (
    ('0', 'New'),
    ('1', 'Processed'),
    ('2', 'Reprocess'),
    ('x', 'Failed')
)

LOG_EVENT_TYPE_CHOICES = (
    ('0', 'Retweet'),
    ('1', 'Favorite'),
    ('2', 'Follow'),
    ('3', 'Scan'),
    ('x', 'Error'),
)

class Log(models.Model):
    event = models.TextField()
    type = models.CharField(max_length=1, choices=LOG_EVENT_TYPE_CHOICES, blank=True, null=True, default='0')
    timestamp = models.DateTimeField(auto_now=True, blank=True, null=True)


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

    search_queries = models.ManyToManyField(SearchQuery, blank=True)
    follow_keywords = models.ManyToManyField(FollowKeyword, blank=True)
    fav_keywords = models.ManyToManyField(FavoriteKeyword, blank=True)

    retweet_list = models.ManyToManyField('Tweet', related_name='retweet_list', blank=True)
    favorited_list = models.ManyToManyField('Tweet', related_name='favorited_list', blank=True)
    ignore_list = models.ManyToManyField('TwitterUser', related_name='ignore_list', blank=True)
    retweet_follow_list = models.ManyToManyField('Tweet', related_name='retweet_follow_list', blank=True)

    post_list = models.ManyToManyField('Tweet', related_name='post_queue', blank=True)

    def connect(self):
        self.api = TwitterAPI(self.consumer_key, self.consumer_secret, self.access_token_key, self.access_token_secret)
        self.ratelimit = [999, 999, 100]
        self.ratelimit_search = [999, 999, 100]

    @staticmethod
    def log_and_print(text, _type='0'):
        log = Log(event=str(text), type=_type)
        log.save()
        return log

    def check_error(self, res):
        res = res.json()
        if 'errors' in res:
            self.log_and_print("We got an error message: "
                               + res['errors'][0]['message'] +
                               " Code: "
                               + str(res['errors'][0]['code']))

    def check_rate_limit(self):
        c = threading.Timer(self.rate_limit_update_time, self.check_rate_limit)
        c.daemon = True
        c.start()

        if self.ratelimit[2] < self.min_ratelimit:
            self.log_and_print("Ratelimit too low -> Cooldown (" + str(self.ratelimit[2]) + "%)")
            time.sleep(30)

        r = self.api.request('application/rate_limit_status').json()

        for res_family in r['resources']:
            for res in r['resources'][res_family]:
                limit = r['resources'][res_family][res]['limit']
                remaining = r['resources'][res_family][res]['remaining']
                percent = float(remaining) / float(limit) * 100

                if res == "/search/tweets":
                    self.ratelimit_search = [limit, remaining, percent]

                if res == "/application/rate_limit_status":
                    self.ratelimit = [limit, remaining, percent]

                if percent < 5.0:
                    self.log_and_print(res_family + " -> " + res + ": " + str(percent) + "  !!! <5% Emergency exit !!!",
                                       'x')
                    sys.exit(res_family + " -> " + res + ": " + str(percent) + "  !!! <5% Emergency exit !!!", 'x')
                elif percent < 30.0:
                    self.log_and_print(res_family + " -> " + res + ": " + str(percent) + "  !!! <30% alert !!!", 'x')
                elif percent < 70.0:
                    print(res_family + " -> " + res + ": " + str(percent))

    def update_queue(self):
        u = threading.Timer(self.retweet_update_time, self.update_queue)
        u.daemon = True
        u.start()

        print("=== CHECKING RETWEET QUEUE ===")

        print("Queue length: " + str(len(self.post_list.all())))

        for post in self.post_list.all():
            if not self.ratelimit[2] < self.min_ratelimit_retweet:
                self.log_and_print("Retweeting: " + str(post.id) + " " + str(post.text), '0')

                self.check_for_follow_request(post)
                self.check_for_favorite_request(post)

                r = self.api.request('statuses/retweet/:' + str(post.id))
                self.check_error(r)
                self.retweet_list.add(post)
                self.post_list.remove(post)
                self.save()
            else:
                print("Ratelimit at " + str(self.ratelimit[2]) + "% -> pausing retweets")

    # Check if a post requires you to follow the user.
    # Be careful with this function! Twitter may write ban your application for following too aggressively
    def check_for_follow_request(self, post):
        if self.follow_keywords.filter(text=post.text.lower()):
            r = self.api.request('friendships/create', {'screen_name': post.user.screen_name})
            self.check_error(r)
            self.log_and_print("Follow: " + post.user.screen_name, '2')
            self.retweet_follow_list.add(post)
            self.save()


    # Check if a post requires you to favorite the tweet.
    # Be careful with this function! Twitter may write ban your application for favoriting too aggressively
    def check_for_favorite_request(self, post):
        if self.fav_keywords.filter(text=post.text.lower()):
            res = self.api.request('favorites/create', {'id': post.id})
            self.check_error(res)
            self.log_and_print("Favorite: " + str(post.id), '1')
            self.favorited_list.add(post)
            self.save()

    @staticmethod
    def object_from_dict(mod, dic):

        # Go through the object, load in the objects we want
        obj = {}
        _app = apps.get_app_config('contests')
        _model = _app.get_model(mod)

        import pdb;
        pdb.set_trace()
        new_obj = _model.objects.get_or_create(obj)
        return new_obj

    # Scan for new contests, but not too often because of the rate limit.
    def scan_for_contests(self):
        t = threading.Timer(self.scan_update_time, self.scan_for_contests)
        t.daemon = True
        t.start()

        if not self.ratelimit_search[2] < self.min_ratelimit_search:
            print("=== SCANNING FOR NEW CONTESTS ===")
            for search_query in self.search_queries.all():
                print("Getting new results for: " + search_query.text)
                try:
                    r = self.api.request('search/tweets', {'q': search_query, 'result_type': "mixed", 'count': 100})
                    self.check_error(r)
                    statuses = json.loads(r.response.content)['statuses']

                    #
                    for item in statuses:
                        # Have we tweeted this tweet before?
                        if item not in self.retweet_list.all():
                            # has this user been ignored before?
                            if len(self.ignore_list.filter(screen_name=item['user']['screen_name'])) == 0:
                                item['user']['created_at'] = parse(item['user']['created_at'])

                                user_obj = {}
                                for field in TwitterUser._meta.get_fields():
                                    if field.name in item['user'].keys():
                                        user_obj[field.name] = item['user'][field.name]

                                user_obj, new_user = TwitterUser.objects.get_or_create(**user_obj)

                                if item['retweet_count'] > 0:
                                    item['created_at'] = parse(item['created_at'])
                                    item['user'] = user_obj
                                    item['bot'] = self
                                    field_obj = {}
                                    for field in Tweet._meta.get_fields():
                                        if field.name in item.keys():
                                            field_obj[field.name] = item[field.name]
                                    post, new_post = Tweet.objects.get_or_create(**field_obj)
                                    if new_post:
                                        self.post_list.add(post)
                                        self.save()
                except Exception as e:
                    # print("Could not connect to TwitterAPI - are your credentials correct?")
                    print("Exception: " + str(e))
        else:
            print(
            "Search skipped! Queue: " + str(len(self.post_list.all())) + " Ratelimit: " + str(self.ratelimit_search[1]) + "/" + str(
                self.ratelimit_search[0]) + " (" + str(self.ratelimit_search[2]) + "%)")

    def run_bot(self):
        self.check_rate_limit()
        self.scan_for_contests()
        self.update_queue()

        while (True):
            time.sleep(1)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class TwitterUser(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    verified = models.BooleanField(default=False)
    geo_enabled = models.BooleanField(default=False)
    location = models.CharField(max_length=255, blank=True, null=True)
    default_profile_image = models.BooleanField(default=False)
    profile_image_url = models.CharField(max_length=255, blank=True, null=True)
    follow_request_sent = models.BooleanField(default=False)
    following = models.BooleanField(default=False)
    id_str = models.CharField(max_length=255, blank=True, null=True)
    screen_name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    friends_count = models.IntegerField(blank=True, null=True)
    profile_banner_url = models.CharField(max_length=255, blank=True, null=True)
    followers_count = models.IntegerField(blank=True, null=True)
    statuses_count = models.IntegerField(blank=True, null=True)
    protected = models.BooleanField(default=False)
    contributors_enabled = models.BooleanField(default=False)
    url = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    is_translator = models.BooleanField(default=False)


    photo = models.FileField(blank=True, null=True, upload_to="twits/photos")

    def __str__(self):
        return self.name


class Tweet(models.Model):
    text = models.TextField()

    in_reply_to_screen_name = models.CharField(max_length=255, blank=True, null=True)
    in_reply_to_status_id = models.IntegerField(blank=True, null=True)
    contributors = models.CharField(max_length=255, blank=True, null=True)
    is_quote_status = models.BooleanField(default=False)
    in_reply_to_status_id_str = models.CharField(max_length=255, blank=True, null=True)
    place = models.CharField(max_length=255, blank=True, null=True)
    favorited = models.BooleanField(default=False)
    created_at = models.DateTimeField(blank=True, null=True)
    retweet_count = models.IntegerField(blank=True, null=True)
    retweeted = models.BooleanField(default=False)
    coordinates = models.CharField(max_length=255, blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)
    lang = models.CharField(max_length=255, blank=True, null=True)
    favorite_count = models.IntegerField(blank=True, null=True)
    geo = models.CharField(max_length=255, blank=True, null=True)
    in_reply_to_user_id = models.IntegerField(blank=True, null=True)
    possibly_sensitive = models.BooleanField(default=False)
    truncated = models.BooleanField(default=False)
    in_reply_to_user_id_str = models.CharField(max_length=255, blank=True, null=True)
    id_str = models.CharField(max_length=255, blank=True, null=True)

    user = models.ForeignKey(TwitterUser, blank=True, null=True)

    bot = models.ForeignKey(Bot, blank=True, null=True)

    def __str__(self):
        return "%s - %s" % (self.user.name, self.text)