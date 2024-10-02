import time
import traceback

from prawcore.exceptions import ServerError, RequestException

from bot.conf import conf
from bot.src.dialogue_bot import dialogue_bot
from bot.src.logger.utils import log, log_conv
from bot.src.logger.L import L
from bot.src.reddit_bot import reddit_bot
from bot.src.trigger import should_trigger_reply
from mongo_db.db import db
from utils.slack.decorator import slack
from utils.slack.exceptions import slack_exception
from utils.slack.styling import sl, subreddits, clink
from utils.slack.webhooks import slack_step, slack_steps_conv, slack_main


@slack('recent_convs')
def run_recent_convs():
    # NOTE: Any conversation-specific logic should NOT be a part of this driver class
    # NOTE: Peripheral things such as logging the conversation should be a part of the driver class

    L.runner = 'R'
    L.run()

    if not conf.subreddits_ids:
        log('No subreddits configured, exiting...')
        slack_step('🚫 No subreddits configured, exiting...')
        return

    # consider all msgs, not just appeals...
    while True:
        try:
            for conv in reddit_bot.get_conversations():
                L.conv_id = conv.id
                L.subreddit = str(conv.owner)

                log(f'*** `{L.subreddit}/{L.conv_id}` processing conversation... {"*" * 20}', L.conv_id)
                slack_steps_conv(f'✴️ *Start processing {clink(L.conv_id)}:*')

                if should_trigger_reply(conv):
                    log_conv("It's a ban appeal, OK")

                    user, created = db.users.get_or_create(conv)
                    username = user['username']
                    if created:
                        log_conv(f'User `{username}`: Added to DB')
                    else:
                        log_conv(f'User `{username}`: Found in DB')
                        log_conv(f'New conv by same user `{username}`, updating model')

                    if user['group'] == 1:  # treatment condition
                        log_conv("It's treatment group, OK")
                        # offense = bot.get_user_ban_information(conv.participant.name, L.subreddit)
                        log_conv("Running dialogue flow...")
                        slack_steps_conv('💬 Running Dialog...')
                        dialogue_bot.reply(conv, user)

                    else:  # control condition
                        log_conv("It's control group, IGNORED")
                        slack_steps_conv('✖️ Control group → IGNORE')
                        # slack_main_conv('✖️ Control group → IGNORE')  # todo: remove?
                        # log_user_data(conv, group)

                    if not db.conversations.find(conv.id):
                        if db.conversations.add(conv, reddit_bot):
                            log_conv("Conversation LOGGED (added to DB)")
                        else:
                            log_conv("Conversation LOGGED (updated in DB)")
                else:
                    log_conv("It's NOT a ban appeal, IGNORED")
                    slack_steps_conv('✖️ Not appeal → IGNORE')
                    # slack_main_conv('✖️ Not appeal → IGNORE')  # todo: remove?

        except (ServerError, RequestException) as e:
            error_message = traceback.format_exc()
            log(error_message, L.conv_id)
            log(f'Received an exception from praw, retrying in 30 secs', L.conv_id)
            slack_exception('recent_convs', e)
            time.sleep(300)  # try again after 5 mins...


if __name__ == "__main__":
    run_recent_convs()
