import time
import traceback
from datetime import datetime, timezone

from dateutil import parser
from pymongo.errors import CursorNotFound

from bot.conf import conf
from bot.config import Config as config
from bot.src.dialogue_bot import dialogue_bot
from bot.src.logger import log, log_conv, L
from bot.src.reddit_bot import reddit_bot
from mongo_db.db import db
from utils.slack.decorator import slack
from utils.slack.exceptions import slack_exception
from utils.slack.styling import sl, subreddits, clink
from utils.slack.webhooks import slack_steps


def status_updates(user, conv):
    subreddit = str(conv.owner)

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
    time.sleep(120)  # wait while [R]ecent conversation processed first
    log('Processing already [S]tarted conversations...')
    slack_steps(':sparkle: Processing '
                ':arrows_counterclockwise: already *started* conversations for '
                f'[{subreddits()}]')

    if not conf.subreddits_ids:
        log('No subreddits configured, exiting...')
        slack_steps(':no_entry_sign: No subreddits configured, exiting...')
        return

    while True:
        users = db.users.all()
        try:
            for j, user in enumerate(users):
                L.conv_id = user["conv_id"]
                L.subreddit = user.get("subreddit")

                log(f'*** `{L.subreddit}/{L.conv_id}` processing conversation... {"*" * 20}', L.conv_id)
                slack_steps(sl('S', L.subreddit, L.conv_id,
                               f':eight_pointed_black_star: *Start processing {clink(L.conv_id)}:*'))

                if not L.subreddit:
                    # fixme: perhaps we don't need it anymore
                    log_conv(L.subreddit, L.conv_id, 'No subreddit field found')
                    continue
                if L.subreddit not in conf.subreddits_ids:
                    # fixme: perhaps we don't need it anymore
                    log_conv(L.subreddit, L.conv_id, f'Wrong subreddit (not in conf): "{L.subreddit}"')
                    continue
                try:
                    if 'user_deleted' in user.keys() and user['user_deleted']:
                        log_conv(L.subreddit, L.conv_id, 'User deleted account, IGNORED')
                        slack_steps(sl('S', L.subreddit, L.conv_id,
                                       ':x: User deleted → IGNORE'))
                        continue

                    if 'last_conv_update' in user.keys() and (datetime.now(timezone.utc) - parser.parse(user['last_conv_update'])).days > config.UPDATE_CUTOFF:
                        log_conv(L.subreddit, L.conv_id, 'Passed time cutoff, IGNORED')  # will no longer be updated
                        slack_steps(sl('S', L.subreddit, L.conv_id,
                                       ':heavy_multiplication_x: Too old → IGNORE'))
                        continue

                    updated_conversation = reddit_bot.reddit.subreddit(L.subreddit).modmail(L.conv_id)
                    log_conv(L.subreddit, L.conv_id, "Status update")
                    update_flag = status_updates(user, updated_conversation)

                    if user['group'] != 1:
                        log_conv(L.subreddit, L.conv_id, "It's control group, IGNORED")
                        slack_steps(sl('S', L.subreddit, L.conv_id,
                                       ':heavy_multiplication_x: Control group → IGNORE'))
                    elif not update_flag:  # fixme: Implement check in another way?
                        slack_steps(sl('S', L.subreddit, L.conv_id,
                                       ':x: User was deleted → IGNORE'))
                    else:
                        log_conv(L.subreddit, L.conv_id, "Running dialogue flow...")
                        updated_conversation = reddit_bot.reddit.subreddit(L.subreddit).modmail(L.conv_id)
                        slack_steps(sl('S', L.subreddit, L.conv_id,
                                       ':speech_balloon: Running Dialog...'))
                        dialogue_bot.reply(updated_conversation, user)

                except Exception as e:
                    # traceback.print_exc()
                    error_message = traceback.format_exc()
                    log(error_message, conv_id=L.conv_id)
                    slack_exception('started_convs', e)

        except CursorNotFound as e:
            error_message = traceback.format_exc()
            log(error_message, conv_id=L.conv_id)
            log(f'It appears that the cursor has expired after {j} records, update will run again after the specified delay',
                conv_id=L.conv_id)
            slack_exception('started_convs', e)

        time.sleep(config.DIALOGUE_UPDATE_INTERVAL)


if __name__ == "__main__":
    run_started_convs()
