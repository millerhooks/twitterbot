import requests
from lxml import html
import random


def hints():
    """
    Random helpful hints.
    """
    hints = [
        'If you press meta-! or esc-! at the following prompt, you can enter system commands.',
        'Take the elevator instead of the stairs.'
    ]
    return random.choice(hints)


def celebrity_name():
    """
    get a random name from this list
    """
    celebs = ['Albert Einstein', 'Benjamin Franklin', 'Marilyn Monroe',
              'Thomas Jefferson', 'Henry Rollins', 'Eli Whitney',
              'George Washington Carver', 'Marie Curie', 'Sally Ride',
              'David Lynch']
    return random.choice(celebs)


def whatthecommit():
    """
    Get random commit message from whatthecommit.com
    """
    page = requests.get('http://whatthecommit.com')
    tree = html.fromstring(page.content)
    return tree.xpath('//div[@id="content"]/p/text()')[0].replace("\n", "")


def revisionist_commit_history():
    """
    Historical figures make shitty commits
    """
    return "\""+whatthecommit()+"\" --"+celebrity_name()