import requests
import urllib
import hashlib, random

BOTS = [
    ('6', 'The original chatbot'),
    ('10', 'ShakespeareBot'),
    ('12', 'Chatmundo'),
    ('15', 'Elizaibeth'),
    ('00', 'Random Bot'),
]

class ProgramO(object):
    """Multipurpose Chat Bot Wrapper
    http://www.program-o.com/chatbotapi
    """
    def __init__(self, q='Hello', bot='00'):
        self.HOST = "api.program-o.com/v2/chatbot/?"
        self.USAGE = 'tweetin_'+hashlib.sha1(str(random.random()).encode('utf8')).hexdigest()

        self.PROTOCOL = "http://"

        self.bot = bot
        if self.bot == '00':
            self.bot = random.choice(BOTS[random.randrange(len(BOTS)-1)])
        self.inital_q = urllib.parse.quote_plus(q)

        self.SERVICE_URL = self.PROTOCOL + self.HOST \
                           + "?bot_id=" + self.bot \
                           + "&convo_id=" + self.USAGE \
                           + "&say=%s&format=json"

        r = requests.get(self.SERVICE_URL % self.inital_q)

        content = r.json()
        self.session = requests.Session()
        self.conversation = []
        self.conversation.append(self.inital_q)
        self.conversation.append(content['botsay'])

    def talk(self, q):
        self.conversation.append(q)
        question = urllib.parse.quote_plus(q.encode('utf8'))
        r = requests.get(self.SERVICE_URL % question).json()
        botsay = r['botsay']
        self.conversation.append(botsay)
        print(botsay)
        return botsay
