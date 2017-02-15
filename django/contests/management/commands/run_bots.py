from django.core.management.base import BaseCommand, CommandError
from contests.models import Bot

class Command(BaseCommand):
    """
    Run Box
    """
    help = 'Run Bot'

    @staticmethod
    def handle(*args, **options):
        #import pdb; pdb.set_trace()
        for bot in Bot.objects.all():
            bot.connect()
            bot.run_bot()
