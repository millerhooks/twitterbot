from pb_py import main as API
from django.conf import settings


class PandoraBot(object):
    def __init__(self):
        HOST = 'aiaas.pandorabots.com'
        APP_ID = settings.PANDORA_BOT_APP_ID
        USER_KEY = settings.PANDORA_BOT_USER_KEY
        BOT_NAME = settings.PANDORA_BOT_NAME

        self.bot = API.create_bot(USER_KEY, APP_ID, HOST, BOT_NAME)

    def talk(self, input_text):
        return self.bot.talk(input_text=input_text)
