import time
import traceback

from prawcore.exceptions import ServerError, RequestException

from bot.conf import conf
from bot.src.dialogue_bot import dialogue_bot
from bot.src.logger import log, log_conv, L
from bot.src.reddit_bot import reddit_bot
from bot.src.trigger import should_trigger_reply
from mongo_db.db import db
from utils.slack.decorator import slack
from utils.slack.exceptions import slack_exception
from utils.slack.styling import sl, subreddits, clink
from utils.slack.webhooks import slack_steps


@slack('recent_convs')
def run_recent_convs():
    exception_flag = False
    # NOTE: Any conversation-specific logic should NOT be a part of this driver class
    # NOTE: Peripheral things such as logging the conversation should be a part of the driver class

    log('Processing [R]ecently created conversations...')
    slack_steps(':sparkle: Processing '
                ':arrow_forward: *recently* created conversations for '
                f'[{subreddits()}]')

    if not conf.subreddits_ids:
        log('No subreddits configured, exiting...')
        slack_steps(':no_entry_sign: No subreddits configured, exiting...')
        return

    # consider all msgs, not just appeals...
    while True:
        try:
            for conv in reddit_bot.get_conversations():
                L.conv_id = conv.id
                L.subreddit = str(conv.owner)

                log(f'*** `{L.subreddit}/{L.conv_id}` processing conversation... {"*" * 20}', L.conv_id)
                slack_steps(sl('R', L.subreddit, L.conv_id,
                               f':eight_pointed_black_star: *Start processing {clink(L.conv_id)}:*'))

                if should_trigger_reply(conv):
                    log_conv(L.subreddit, L.conv_id, "It's a ban appeal, OK")

                    user, created = db.users.get_or_create(conv)
                    username = user['username']
                    if created:
                        log_conv(L.subreddit, L.conv_id, f'User `{username}`: Added to DB')
                    else:
                        log_conv(L.subreddit, L.conv_id, f'User `{username}`: Found in DB')
                        log_conv(L.subreddit, L.conv_id, f'New conv by same user `{username}`, updating model')

                    if user['group'] == 1:  # treatment condition
                        log_conv(L.subreddit, L.conv_id, "It's treatment group, OK")
                        # offense = bot.get_user_ban_information(conv.participant.name, L.subreddit)
                        log_conv(L.subreddit, L.conv_id, "Running dialogue flow...")
                        slack_steps(sl('R', L.subreddit, L.conv_id,
                                       ':speech_balloon: Running Dialog...'))
                        dialogue_bot.reply(conv, user)

                    else:  # control condition
                        log_conv(L.subreddit, L.conv_id, "It's control group, IGNORED")
                        slack_steps(sl('R', L.subreddit, L.conv_id,
                                       ':heavy_multiplication_x: Control group → IGNORE'))
                        # log_user_data(conv, group)

                    if not db.conversations.find(conv.id):
                        if db.conversations.add(conv, reddit_bot):
                            log_conv(L.subreddit, L.conv_id, "Conversation LOGGED (added to DB)")
                        else:
                            log_conv(L.subreddit, L.conv_id, "Conversation LOGGED (updated in DB)")
                else:
                    log_conv(L.subreddit, L.conv_id, "It's NOT a ban appeal, IGNORED")
                    slack_steps(sl('R', L.subreddit, L.conv_id,
                                   ':heavy_multiplication_x: Not appeal → IGNORE'))

        except (ServerError, RequestException) as e:
            error_message = traceback.format_exc()
            log(error_message, L.conv_id)
            log(f'Received an exception from praw, retrying in 30 secs', L.conv_id)
            slack_exception('recent_convs', e)
            time.sleep(300)  # try again after 5 mins...


if __name__ == "__main__":
    run_recent_convs()
