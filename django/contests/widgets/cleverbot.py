import requests
import urllib

class Cleverbot(object):
    """Handles a conversation with Cleverbot.
    Example usage:
       >>> from cleverbot import Cleverbot
       >>> cb = Cleverbot('my-api-key')
       >>> cb.ask("Hi. How are you?")
       "Hello"

    http://www.cleverbot.com/apis
    """
    def __init__(self, key, q='Hello'):
        self.HOST = "www.cleverbot.com"

        self.PROTOCOL = "https://"
        self.RESOURCE = "/getreply"

        self.key = key
        self.inital_q = urllib.parse.quote_plus(q)

        self.SERVICE_URL = self.PROTOCOL + self.HOST + self.RESOURCE + "?key=" + self.key + "&input=" + self.inital_q
        r = requests.get(self.SERVICE_URL)
        content = r.json()
        self.cs = content['cs']
        self.conversation_id = content['conversation_id']
        self.session = requests.Session()
        self.conversation = []

    def ask(self, q):
        self.conversation.append(q)
        question = urllib.parse.quote_plus(q.encode('utf8'))
        url = self.SERVICE_URL + "&input=" + question + "&cs=" + self.cs

        r = requests.get(url).json()
        self.conversation.append(r['output'])
        print(r['output'])
        return r['output']


