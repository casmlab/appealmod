import time
import traceback
from datetime import datetime, timezone

from dateutil import parser
from pymongo.errors import CursorNotFound

from bot.conf import conf
from bot.config import Config as config
from bot.src.dialogue_bot import dialogue_bot
from bot.src.logger.utils import log, log_conv
from bot.src.logger.L import L
from bot.src.reddit_bot import reddit_bot
from mongo_db.db import db
from utils.slack.decorator import slack
from utils.slack.exceptions import slack_exception
from utils.slack.styling import subreddits, clink
from utils.slack.webhooks import slack_step, slack_steps_conv, slack_main_conv, \
    slack_main


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

    L.runner = 'S'
    L.run()

    if not conf.subreddits_ids:
        log('No subreddits configured, exiting...')
        slack_step('🚫 No subreddits configured, exiting...')
        return

    while True:
        users = db.users.all()
        try:
            for j, user in enumerate(users):
                L.conv_id = user["conv_id"]
                L.subreddit = user.get("subreddit")
                L.conv()

                if not L.subreddit:
                    raise Exception("Never should happen: subreddit field is required")
                if L.subreddit not in conf.subreddits_ids:
                    raise Exception("Never should happen: we already filter by subreddit")
                if 'user_deleted' in user.keys() and user['user_deleted']:
                    raise Exception("Never should happen: we already excluded deleted")

                try:
                    conv = reddit_bot.reddit.subreddit(L.subreddit).modmail(L.conv_id)

                    if 'last_conv_update' in user.keys() and (datetime.now(timezone.utc) - parser.parse(user['last_conv_update'])).days > config.UPDATE_CUTOFF:
                        log_conv('Passed time cutoff, IGNORED')  # will no longer be updated
                        slack_steps_conv('✖️ Too old → IGNORE')
                        slack_main_conv('✖️ Too old → IGNORE')
                        continue

                    log_conv("Status update")
                    update_flag = status_updates(user, conv)

                    if user['group'] != 1:
                        log_conv("It's control group, IGNORED")
                        slack_steps_conv('✖️ Control group → IGNORE')
                        slack_main_conv('✖️ Control group → IGNORE')
                    elif not update_flag:  # fixme: Implement check in another way?
                        slack_steps_conv('❌ User was deleted → IGNORE')
                        slack_main_conv('❌ User was deleted → IGNORE')
                    else:
                        log_conv("Running dialogue flow...")
                        conv = reddit_bot.reddit.subreddit(L.subreddit).modmail(L.conv_id)
                        slack_steps_conv('💬 Running Dialog...')
                        dialogue_bot.reply(conv, user)

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
