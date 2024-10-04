import praw
import time

from bot.config import Config as config
from mongo_db.db import db


def get_admin_reddit():
    return praw.Reddit(
        client_id=config.TEST_ADMIN_CLIENT_ID,
        client_secret=config.TEST_ADMIN_CLIENT_SECRET,
        user_agent=config.TEST_ADMIN_USER_AGENT,
        username=config.TEST_ADMIN_USERNAME,
        password=config.TEST_ADMIN_PASSWORD,
    )


username = config.TEST_USER_USERNAME
# subreddit = "umsiexperiments"
subreddit = "appealmodtest"


def unban_user(username, subreddit):
    # initially unban the user to activate the other scripts.
    reddit.subreddit(subreddit).banned.remove(username)


def get_users_cursor(username, subreddit):
    cursor = db.users.collection.find({'username': username,
                                       'subreddit': subreddit})
    # print(len(list(cursor)))
    return cursor


def ban_user(username, subreddit):
    reddit.subreddit(subreddit).banned.add(username, ban_message="banned",
                                           ban_reason="banned",
                                           note="Banned with note")


def get_user_reddit():
    # User details to send reply
    return praw.Reddit(
        username=config.TEST_USER_USERNAME,
        password=config.TEST_USER_PASSWORD,
        client_id=config.TEST_USER_CLIENT_ID,
        client_secret=config.TEST_USER_CLIENT_SECRET,
        user_agent=config.TEST_USER_USER_AGENT
    )


def get_user_messages():
    # Get your messages
    messages = user_reddit.inbox.messages()
    # print(messages)
    return messages


def reply_on_ban_message(subreddit, messages):
    # Loop through messages
    for message in messages:
        # Check if the message is from a moderator and the message content matches what you're looking for
        # print('#' * 80)
        # print('-', message)
        # print(message.body)
        # print(dir(message))
        # print(message.subreddit)
        # print('*' * 80)
        if message.subreddit == subreddit and f"permanently banned from participating in r/{subreddit}" in message.body:
            print(message, 'ok')
            # Reply to the message
            reply_text = "Why i am Ban?."
            message.reply(reply_text)
            print("Replied to the moderator's message.")
            break  # Stop after replying to the first matching message


def wait_user_db_creation(cursor, username, subreddit):
    # Loop which keeps running until new user have been added to the DB via recent_convs.py script.
    while len(list(cursor)) == 0:
        # break
        cursor = db.users.collection.find({'username': username,
                                           'subreddit': subreddit})
        print("sleep...")
        time.sleep(5)
    print("Found the user in user logs.")


# run.py will get triggered if the user is getting banned for the first time

# dialogue_update.py will get triggered to send a reply to the user's reply("why banned") 
# on behalf of moderator

# dialogue_update.py line 14 -> modify the subreddits to take only ['umsiexperiments']
# {username:"TryOwn7908"}

# how to get to know if test is successful in automated way. Currently we check manually in the logs
# and define if the test is successful or not


if __name__ == "__main__":
    reddit = get_admin_reddit()
    unban_user(username, subreddit)
    ban_user(username, subreddit)
    user_reddit = get_user_reddit()

    messages = get_user_messages()
    reply_on_ban_message(subreddit, messages)

    # print((any(reddit.subreddit(subreddit).banned(username))))  # fixme: old code
    cursor = get_users_cursor(username, subreddit)
    wait_user_db_creation(cursor, username, subreddit)

    # todo: 4st step - responses['initial']...

    unban_user(username, subreddit)
    # todo: remove the user from DB
