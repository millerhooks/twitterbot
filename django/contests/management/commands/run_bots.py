from django.core.management.base import BaseCommand, CommandError
from contest.models import Bot

class Command(BaseCommand):
    """
    Run Box
    """
    help = 'Run Bot'

    @staticmethod
    def handle(*args, **options):
        #import pdb; pdb.set_trace()
        for bot in Bot.objects.all():
            bot.run_bot()
