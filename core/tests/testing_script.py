import praw
from core.config import Config as config
from core.scripts.logger import user_logs_collection
import time

reddit = praw.Reddit(
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

# initially unban the user to activate the other scripts.
reddit.subreddit(subreddit).banned.remove(username)

# print((any(reddit.subreddit(subreddit).banned(username))))
cursor = user_logs_collection.find({'username': username})
# print(len(list(cursor)))
reddit.subreddit(subreddit).banned.add(username, ban_reason="banned",
                                       note="Banned with note")


# User details to send reply
# TODO: remove hardcoding
user_reddit = praw.Reddit(
    username=username,
    password='Sargam123',
    client_id="dgvEH0n-lHFHvckN8d9JyQ",
    client_secret="sLDy3I-F-ZaDDjtXpCzDwTUcKSYiVw",
    user_agent=username, 
)

# Get your messages
messages = user_reddit.inbox.messages()
# print(messages)

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


# Loop which keeps running until new user have been added to the DB via run.py script.
while len(list(cursor)) == 0:
    # break
    cursor = user_logs_collection.find({'username': username})
    print("sleep...")
    time.sleep(5)
print("Found the user in user logs.")

# todo: 4st step - responses['initial']...

reddit.subreddit(subreddit).banned.remove(username)
# todo: remove the user

# run.py will get triggered if the user is getting banned for the first time

# dialogue_update.py will get triggered to send a reply to the user's reply("why banned") 
# on behalf of moderator

# dialogue_update.py line 14 -> modify the subreddits to take only ['umsiexperiments']
# {username:"TryOwn7908"}

# how to get to know if test is successful in automated way. Currently we check manually in the logs
# and define if the test is successful or not
