import core.scripts.bin  # to enable django support
from main.models import BanAppealData


def add_form_entry(reddit_username, subreddit):
    return BanAppealData.objects.create(reddit_username, subreddit)


def get_form_response(reddit_username, subreddit):
    return BanAppealData.objects.auth(reddit_username, subreddit)
