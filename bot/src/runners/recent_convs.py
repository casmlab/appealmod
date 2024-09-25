import time
import traceback

from prawcore.exceptions import ServerError, RequestException

from bot.src.dialogue_bot import dialogue_bot
from bot.src.logger import log, log2
from bot.src.reddit_bot import reddit_bot
from bot.src.trigger import should_trigger_reply
from mongo_db.db import db
from utils.slack.decorator import slack
from utils.slack.exceptions import slack_exception
from utils.slack.styling import sl
from utils.slack.webhooks import slack_status


@slack('recent_convs')
def run_recent_convs():
    exception_flag = False
    # NOTE: Any conversation-specific logic should NOT be a part of this driver class
    # NOTE: Peripheral things such as logging the conversation should be a part of the driver class

    log('Processing [R]ecently created conversations...')
    slack_status(':sparkle: Processing '
                 ':arrow_forward: *recently* created conversations')

    # consider all msgs, not just appeals...
    while True:
        try:
            for conv in reddit_bot.get_conversations():
                conv_id = conv.id
                subreddit = str(conv.owner)
                log(f'*** `{subreddit}/{conv_id}` processing conversation... {"*" * 20}', conv_id)
                slack_status(sl('R', subreddit, conv_id,
                                ':eight_pointed_black_star: *Processing...*'))

                if should_trigger_reply(reddit_bot, conv, subreddit):
                    log2(subreddit, conv_id, "It's a ban appeal, OK")

                    user = db.users.get_or_create(conv)

                    if user['group'] == 1:  # treatment condition
                        log2(subreddit, conv_id, "It's treatment group, OK")
                        # offense = bot.get_user_ban_information(conv.participant.name, subreddit)
                        log2(subreddit, conv_id, "Running dialogue flow...")
                        slack_status(sl('R', subreddit, conv_id,
                                        ':speech_balloon: Running Dialog...'))
                        dialogue_bot.run(conv, user)

                    else:  # control condition
                        log2(subreddit, conv_id, "It's control group, IGNORED")
                        slack_status(sl('R', subreddit, conv_id,
                                        ':heavy_multiplication_x: Control group → IGNORE'))
                        # log_user_data(conv, group)

                    if not db.conversations.find(conv.id):
                        db.conversations.add(conv, reddit_bot)
                else:
                    log2(subreddit, conv_id, "It's NOT a ban appeal, IGNORED")
                    slack_status(sl('R', subreddit, conv_id,
                                    ':heavy_multiplication_x: Not appeal → IGNORE'))

        except (ServerError, RequestException) as e:
            error_message = traceback.format_exc()
            log(error_message, conv_id)
            log(f'Received an exception from praw, retrying in 30 secs', conv_id)
            slack_exception('recent_convs', e)
            time.sleep(300)  # try again after 5 mins...


if __name__ == "__main__":
    run_recent_convs()
