import time
import traceback

from prawcore.exceptions import ServerError, RequestException

from bot.conf import conf
from bot.src.dialogue_bot import dialogue_bot
from bot.src.logger.L import L
from bot.src.reddit_bot import reddit_bot
from bot.src.trigger import should_trigger_reply
from mongo_db.db import db
from utils.slack.decorator import slack
from utils.slack.exceptions import slack_exception


@slack('recent_convs')
def run_recent_convs():
    # NOTE: Any conversation-specific logic should NOT be a part of this driver class
    # NOTE: Peripheral things such as logging the conversation should be a part of the driver class

    L.runner = 'R'
    L.run()

    if not conf.subreddits_ids:
        L.step('🚫 No subreddits configured, exiting...', conv_prefix=False)
        return

    # consider all msgs, not just appeals...
    while True:
        try:
            for conv in reddit_bot.get_conversations():
                L.conv_id = conv.id
                L.subreddit = str(conv.owner)
                L.conv()

                if should_trigger_reply(conv):
                    L.logging("It's a ban appeal, OK")

                    user, created = db.users.get_or_create(conv)
                    username = user['username']
                    if created:
                        L.logging(f'User `{username}`: Added to DB')
                    else:
                        L.logging(f'User `{username}`: Found in DB')
                        L.logging(f'New conv by same user `{username}`, updating model')

                    if user['group'] == 1:  # treatment condition
                        # It's treatment group, OK"
                        # offense = bot.get_user_ban_information(conv.participant.name, L.subreddit)
                        L.step('💬 Running Dialog...')
                        dialogue_bot.reply(conv, user)

                    else:  # control condition
                        L.step('✖️ Control group → IGNORE')
                        # log_user_data(conv, group)

                    if not db.conversations.find(conv.id):
                        if db.conversations.add(conv, reddit_bot):
                            L.logging("Conversation LOGGED (added to DB)")
                        else:
                            L.logging("Conversation LOGGED (updated in DB)")
                else:
                    L.step('✖️ Not appeal → IGNORE')

        except (ServerError, RequestException) as e:
            error_message = traceback.format_exc()
            L.logger(error_message)  # fixme: join with exception in L
            L.logger(f'Received an exception from praw, retrying in 30 secs')
            slack_exception('recent_convs', e)  # fixme
            time.sleep(300)  # try again after 5 mins...


if __name__ == "__main__":
    run_recent_convs()
