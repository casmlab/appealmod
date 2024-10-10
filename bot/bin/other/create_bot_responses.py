from bot.conf import conf
from mongo_db.db import db

if __name__ == '__main__':
    for subreddit in conf.subreddits_ids:
        print(subreddit)
        if db.bot_responses.get(subreddit):
            print('-', 'Already exists')
        else:
            db.bot_responses.add_default(subreddit)
            print('-', db.bot_responses.get(subreddit))
