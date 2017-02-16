from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from TwitterAPI import TwitterAPI
import sys, json, time, threading, random
from .widgets.wtc import revisionist_commit_history, whatthecommit
from .widgets.cleverbot import Cleverbot
from .widgets.pandora_bot import PandoraBot
from .widgets.programo import ProgramO


__admin__ = [
    'Log',
    'SearchQuery',
    'FollowKeyword',
    'FavoriteKeyword',
    'TweetGenerator',
    'Bot',
    'TwitterUser',
    'Tweet',
    'Gibberish'
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
    ('4', 'Tweet'),
    ('x', 'Error'),

)

TWEET_GENERATORS_CHOICES = (
    ('non', 'Do not generate tweets'),
    ('wtc', 'What The Communicator'),
    ('clv', 'Cleverbot'),
    ('dnd', 'Dungeons & Dragons'),
    ('all', 'Use all of them')
)

class Gibberish(models.Model):
    name = models.CharField(max_length=255)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.name

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

class TweetGenerator(models.Model):
    slug = models.CharField(max_length=255)
    display = models.CharField(max_length=255)

    def __str__(self):
        return self.display


class Bot(models.Model):
    name = models.CharField(max_length=255)
    screen_name = models.CharField(max_length=255, blank=True, null=True)
    photo = models.FileField(blank=True, upload_to="bots/photos")
    status = models.CharField(max_length=1, choices=BOT_STATUS_CHOICES, blank=True, default='0')
    tweet_generator = models.ManyToManyField(TweetGenerator, blank=True)

    consumer_key = models.CharField(max_length=255)
    consumer_secret = models.CharField(max_length=255)
    access_token_key = models.CharField(max_length=255)
    access_token_secret = models.CharField(max_length=255)

    retweet_update_time = models.IntegerField(default=1300, help_text="how often to update retweets")
    scan_update_time = models.IntegerField(default=1500, help_text="how often to scan for contest tweets")
    rate_limit_update_time = models.IntegerField(default=10, help_text="how often to scan for contest tweets")
    talk_update_time = models.IntegerField(default=1000, help_text="how often to puke up text")

    min_ratelimit = models.IntegerField(default=10, help_text="minimum rate limit")
    min_ratelimit_retweet = models.IntegerField(default=20, help_text="minimum rate limit for retweets")
    min_ratelimit_search = models.IntegerField(default=40, help_text="minimum rate limit for search")
    min_ratelimit_talk = models.IntegerField(default=40, help_text="minimum rate limit for random talking")

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
        self.cb = None # Cleverbot
        self.pnd = None # Pandorabot
        self.pgm = None  # ProgramO

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
                               + str(res['errors'][0]['code']), 'x')

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
                    sys.exit(res_family + " -> " + res + ": " + str(percent) + "  !!! <5% Emergency exit !!!")
                elif percent < 30.0:
                    self.log_and_print(res_family + " -> " + res + ": " + str(percent) + "  !!! <30% alert !!!", 'x')
                elif percent < 70.0:
                    print(res_family + " -> " + res + ": " + str(percent))

    def tweet(self, users='', ask='', queue=False):
        gens = self.tweet_generator.all()
        tweet = ''
        if not ask:
            ask = whatthecommit()

        if gens:
            gen_choice = random.choice(gens)
            if gen_choice.slug == 'wtc':
                tweet = revisionist_commit_history()
            elif gen_choice.slug == 'clv':
                if not self.cb:
                    self.cb = Cleverbot('f2aaac5921e75233e1be67ee6332f7a0')
                    tweet = self.cb.ask(ask)
                    if not tweet:
                        self.log_and_print("CLEVERBOT RETURNED NOTHING"+str(self.cb.conversation), 'x')
            elif gen_choice.slug == 'pgm':
                if not self.pgm:
                    self.pgm = ProgramO()
                    tweet = self.pgm.talk(ask)
            elif gen_choice.slug == 'pnd':
                if not self.pnd:
                    self.pnd = PandoraBot()
                    tweet = self.pnd.talk(ask)
            elif gen_choice.slug == 'non':
                pass

            if users:
                tweet = users+tweet

            if not queue:
                self.log_and_print("Tweeting: " + tweet + " ", '4')
                r = self.api.request('statuses/update', {'status': tweet})
                self.check_error(r)

            return tweet

    def get_mentions(self):
        res = self.api.request('statuses/mentions_timeline')
        self.check_error(res)
        mentions = json.loads(res.response.content)
        for item in mentions:
            users = ""
            for ent in item['entities']['user_mentions']:
                if ent['screen_name'] != self.screen_name:
                    users += "@"+ent['screen_name'] + " "

            throttle = settings.THROTTLE_REPLY_TWEETS
            reply = self.tweet(users, item['text'], throttle)
            post = self.parse_status_item(item, reply, throttle)
            post.save()

    def parse_status_item(self, item, reply='', throttle=False):
        user = item['user']
        post = item

        twit_dict = TwitterUser().__dict__
        del twit_dict['_state']

        user_set = set(user)
        model_set = set(twit_dict)
        user_dict = {}
        for key in model_set.intersection(user_set):
            if key == 'id':
                user_dict['twitter_id'] = user[key]
            else:
                user_dict[key] = user[key]

        tweet_dict = Tweet().__dict__
        del tweet_dict['_state']

        post_set = set(post)
        model_set = set(tweet_dict)
        post_dict = {}
        for key in model_set.intersection(post_set):
            if key == 'id':
                post_dict['twitter_id'] = post[key]
            else:
                post_dict[key] = post[key]

        post_obj = Tweet.objects.get_or_create(**post_dict)[0]
        post_obj.user = TwitterUser.objects.get_or_create(**user_dict)[0]
        post_obj.bot = self
        if reply:
            post_obj.reply = reply

        if post and not throttle:
            self.post_list.add(post_obj)
            self.save()

        return post_obj



    def update_queue(self):
        u = threading.Timer(self.retweet_update_time, self.update_queue)
        u.daemon = True
        u.start()

        print("=== CHECKING RETWEET QUEUE ===")
        print("Queue length: " + str(len(self.post_list.all())))

        if self.min_ratelimit_retweet < self.ratelimit[2]:
            self.tweet()
            self.get_mentions()
            for post in self.post_list.all():
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

    def check_for_follow_request(self, post):
        if self.follow_keywords.filter(text=post.text.lower()):
            r = self.api.request('friendships/create', {'screen_name': post.user.screen_name})
            self.check_error(r)
            self.log_and_print("Follow: " + post.user.screen_name, '2')
            self.retweet_follow_list.add(post)
            self.save()

    def check_for_favorite_request(self, post):
        if self.fav_keywords.filter(text=post.text.lower()):
            res = self.api.request('favorites/create', {'id': post.id})
            self.check_error(res)
            self.log_and_print("Favorite: " + str(post.id), '1')
            self.favorited_list.add(post)
            self.save()


    def scan_for_contests(self):
        t = threading.Timer(self.scan_update_time, self.scan_for_contests)
        t.daemon = True
        t.start()

        if self.min_ratelimit_search < self.ratelimit_search[2]:
            print("=== SCANNING FOR NEW CONTESTS ===")
            for search_query in self.search_queries.all():
                print("Getting new results for: " + search_query.text)
                try:
                    r = self.api.request('search/tweets', {'q': search_query, 'result_type': "mixed", 'count': 100})
                    self.check_error(r)
                    statuses = json.loads(r.response.content)['statuses']

                    for item in statuses:
                        # Have we tweeted this tweet before?
                        if item not in self.retweet_list.all():
                            # has this user been ignored before?
                            if len(self.ignore_list.filter(screen_name=item['user']['screen_name'])) == 0:
                                self.parse_status_item(item)
                except Exception as e:
                    print("Exception: " + str(e))
        else:
            print(
            "Search skipped! Queue: " + str(len(self.post_list.all())) + " Ratelimit: " + str(self.ratelimit_search[1]) + "/" + str(
                self.ratelimit_search[0]) + " (" + str(self.ratelimit_search[2]) + "%)")

    def run_bot(self):
        self.check_rate_limit()
        self.scan_for_contests()
        self.update_queue()

        while True:
            time.sleep(1)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class TwitterUser(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    twitter_id = models.IntegerField(blank=True, null=True)
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
    created_at = models.CharField(max_length=255, blank=True, null=True)
    is_translator = models.BooleanField(default=False)


    photo = models.FileField(blank=True, null=True, upload_to="twits/photos")

    def __str__(self):
        return str(self.name)


class Tweet(models.Model):
    text = models.TextField()

    twitter_id = models.IntegerField(blank=True, null=True)
    in_reply_to_screen_name = models.CharField(max_length=255, blank=True, null=True)
    in_reply_to_status_id = models.IntegerField(blank=True, null=True)
    contributors = models.CharField(max_length=255, blank=True, null=True)
    is_quote_status = models.BooleanField(default=False)
    in_reply_to_status_id_str = models.CharField(max_length=255, blank=True, null=True)
    place = models.CharField(max_length=255, blank=True, null=True)
    favorited = models.BooleanField(default=False)
    created_at = models.CharField(max_length=255, blank=True, null=True)
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

    reply = models.TextField(max_length=255, blank=True, null=True)

    user = models.ForeignKey(TwitterUser, blank=True, null=True)

    bot = models.ForeignKey(Bot, blank=True, null=True)

    def __str__(self):
        return "%s - %s" % (self.user, self.text)