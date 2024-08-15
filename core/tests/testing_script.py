import praw
from core.config import Config as config
from core.scripts.logger import user_logs_collection
import time


def get_admin_reddit():
    return praw.Reddit(
        client_id=config.CLIENT_ID,
        client_secret=config.CLIENT_SECRET,
        user_agent=config.USER_AGENT,
        username=config.REDDIT_USERNAME,
        password=config.REDDIT_PASSWORD,
    )

# update username and subreddit accordingly.
# TODO: create some config or console input to enter these values.
username = 'TryOwn7908'
subreddit = "umsiexperiments"


def unban_user(username, subreddit):
    # initially unban the user to activate the other scripts.
    reddit.subreddit(subreddit).banned.remove(username)


def get_users_cursor(username, subreddit):
    # print((any(reddit.subreddit(subreddit).banned(username))))
    cursor = user_logs_collection.find({'username': username,
                                        'subreddit': subreddit})
    # print(len(list(cursor)))
    return cursor


def ban_user(username, subreddit):
    reddit.subreddit(subreddit).banned.add(username, ban_reason="banned",
                                           note="Banned with note")


def get_user_reddit():
    # User details to send reply
    # TODO: remove hardcoding
    return praw.Reddit(
        username=username,
        password='Sargam123',
        client_id="dgvEH0n-lHFHvckN8d9JyQ",
        client_secret="sLDy3I-F-ZaDDjtXpCzDwTUcKSYiVw",
        user_agent=username,
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
        # print(message)
        # print(dir(message))
        # print(message.subreddit)
        if message.subreddit == subreddit and f"permanently banned from participating in r/{subreddit}" in message.body:
            print(message)
            # Reply to the message
            reply_text = "Why i am Ban?."
            message.reply(reply_text)
            print("Replied to the moderator's message.")
            break  # Stop after replying to the first matching message


def wait_user_db_creation(cursor, username):
    # Loop which keeps running until new user have been added to the DB via run.py script.
    while len(list(cursor)) == 0:
        # break
        cursor = user_logs_collection.find({'username': username})
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

    cursor = get_users_cursor(username, subreddit)
    wait_user_db_creation(cursor, username)

    # todo: 4st step - responses['initial']...

    unban_user(username, subreddit)
    # todo: remove the user from DB
