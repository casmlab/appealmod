import time
import traceback
from datetime import datetime, timezone

from dateutil import parser
from pymongo.errors import CursorNotFound

from bot.conf import conf
from bot.config import Config as config
from bot.src.dialogue_bot import dialogue_bot
from bot.src.logger import log, log2
from bot.src.reddit_bot import reddit_bot
from mongo_db.db import db
from utils.slack.decorator import slack
from utils.slack.styling import sl
from utils.slack.webhooks import slack_status


def status_updates(user, conv):
    subreddit = str(conv.owner)
    log2(subreddit, user['conv_id'], "Status update")
    # values to update: last_conv_update, user_deleted, appeal_accept
    if conv.participant.name == '[deleted]':
        db.users.update(conv, 'user_deleted', True,
                        force_username=user['username'])
        return False

    else:
        last_update_time = conv.last_updated
        if len(conv.mod_actions) > 0:
            last_action_time = sorted(conv.mod_actions, key=lambda x: x.date)[-1].date
            last_update_time = max(last_update_time, last_action_time)

        appeal_accept = \
            not reddit_bot.is_user_banned_from_subreddit(user['username'],
                                                         subreddit)

        db.users.update(conv, 'last_conv_update', last_update_time)
        db.users.update(conv, 'appeal_accept', appeal_accept)

        return True


@slack('started_convs')
def run_started_convs():
    time.sleep(60)  # wait while [R]ecent conversation processed first  # fixme: increase interval?
    log('Processing already [S]tarted conversations...')
    slack_status(':sparkle: Processing '
                 ':arrows_counterclockwise: already *started* conversations')
    while True:
        users = db.users.all()
        try:
            for j, user in enumerate(users):
                conv_id = user["conv_id"]
                subreddit = user.get("subreddit")
                log(f'*** `{subreddit}/{conv_id}` processing conversation... {"*" * 20}', conv_id)
                slack_status(sl('S', subreddit, conv_id,
                                ':eight_pointed_black_star: *Processing...*'))

                if not subreddit:
                    # fixme: perhaps we don't need it anymore
                    log2(subreddit, conv_id, 'No subreddit field found')
                    continue
                if subreddit not in conf.subreddits_ids:
                    # fixme: perhaps we don't need it anymore
                    log2(subreddit, conv_id, f'Wrong subreddit (not in conf): "{subreddit}"')
                    continue
                try:
                    if 'user_deleted' in user.keys() and user['user_deleted']:
                        log2(subreddit, conv_id, 'User deleted account, IGNORED')
                        slack_status(sl('S', subreddit, conv_id,
                                        ':x: User deleted → IGNORE'))

                        continue
                    if 'last_conv_update' in user.keys() and (datetime.now(timezone.utc) - parser.parse(user['last_conv_update'])).days > config.UPDATE_CUTOFF:
                        log2(subreddit, conv_id, 'Passed time cutoff, IGNORED')  # will no longer be updated
                        slack_status(sl('S', subreddit, conv_id,
                                        ':heavy_multiplication_x: Too old → IGNORE'))
                        continue

                    updated_conversation = reddit_bot.reddit.subreddit(subreddit).modmail(conv_id)
                    update_flag = status_updates(user, updated_conversation)

                    if user['group'] == 1 and update_flag:
                        log2(subreddit, conv_id, "Running dialogue flow...")
                        updated_conversation = reddit_bot.reddit.subreddit(subreddit).modmail(conv_id)
                        slack_status(sl('S', subreddit, conv_id,
                                        ':speech_balloon: Running Dialog...'))
                        dialogue_bot.run(updated_conversation, user)

                except Exception as e:
                    # traceback.print_exc()
                    error_message = traceback.format_exc()
                    log(error_message, conv_id=conv_id)
                time.sleep(5)

        except CursorNotFound as e:
            error_message = traceback.format_exc()
            log(error_message, conv_id=conv_id)
            log(f'It appears that the cursor has expired after {j} records, update will run again after the specified delay',
                conv_id=conv_id)

        time.sleep(config.DIALOGUE_UPDATE_INTERVAL)


if __name__ == "__main__":
    run_started_convs()
