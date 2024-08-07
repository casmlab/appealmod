from conf import conf
from scripts.logger import user_logs_collection, log, update_user_data
from config import Config as config
import time
from scripts.bot import Bot
import traceback
from scripts.dialogue import Dialogue
from pymongo.errors import CursorNotFound
from datetime import datetime, timezone
from dateutil import parser

# reddit = praw.Reddit(
#             client_id=config.CLIENT_ID,
#             client_secret=config.CLIENT_SECRET,
#             user_agent=config.USER_AGENT,
#             username=config.REDDIT_USERNAME,
#             password=config.REDDIT_PASSWORD,
# )

bot = Bot(conf.subreddits_ids)
dialogue = Dialogue(bot)


def status_updates(user, conv):
    log("Status update for conversation id: " + user['conv_id'],
        conversation_id=user['conv_id'])
    # values to update: last_conv_update, user_deleted, appeal_accept
    if conv.participant.name == '[deleted]':
        update_user_data(conv, 'user_deleted', True,
                         username=user['username'])
        return False

    else:
        keys = ['last_conv_update', 'appeal_accept']
        last_update_time = conv.last_updated

        if len(conv.mod_actions) > 0:
            last_action_time = sorted(conv.mod_actions, key=lambda x: x.date)[-1].date
            last_update_time = max(last_update_time, last_action_time)

        values = [last_update_time]

        subreddit = str(conv.owner)
        if not bot.is_user_banned_from_subreddit(user['username'], subreddit):
            values.append(True)
        else:
            values.append(False)

        update_user_data(conv, keys, values)
        return True


def dialogue_update_loop():
    log('Starting dialogue loop...')
    while True:
        time.sleep(config.DIALOGUE_UPDATE_INTERVAL)
        cursor = user_logs_collection.find(
            {'subreddit': {'$in': conf.subreddits_ids}},
            batch_size=30,
        )
        try:
            for j, user in enumerate(cursor):
                conversation_id = user["conv_id"]
                subreddit = user.get("subreddit")
                if not subreddit:
                    log(f'No subreddit found for conversation {conversation_id}', conversation_id=conversation_id)
                    continue
                if subreddit not in conf.subreddits_ids:
                    log(f'Wrong subreddit used (not in conf): "{subreddit}"')
                    continue
                try:
                    if 'user_deleted' in user.keys() and user['user_deleted']:
                        log(f'User for conversation {conversation_id} has deleted their account, updates will be skipped',
                            conversation_id=conversation_id)
                        continue
                    if 'last_conv_update' in user.keys() and (datetime.now(timezone.utc) - parser.parse(user['last_conv_update'])).days > config.UPDATE_CUTOFF:
                        # log(f'{conversation_id} has passed the update cutoff, will no longer be updated', conversation_id=conversation_id)
                        continue

                    updated_conversation = bot.reddit.subreddit(subreddit).modmail(conversation_id)
                    update_flag = status_updates(user, updated_conversation)

                    if user['group'] == 1 and update_flag:
                        log("Dialogue updates for conversation id: " + conversation_id,
                            conversation_id=conversation_id)
                        updated_conversation = bot.reddit.subreddit(subreddit).modmail(conversation_id)
                        dialogue.run(updated_conversation, user)

                except Exception as e:
                    # traceback.print_exc()                
                    error_message = traceback.format_exc()
                    log(error_message, conversation_id=conversation_id)
                time.sleep(5)

        except CursorNotFound as e:
            error_message = traceback.format_exc()
            log(error_message, conversation_id=conversation_id)
            log(f'It appears that the cursor has expired after {j} records, update will run again after the specified delay',
                conversation_id=conversation_id)

        # time.sleep(config.DIALOGUE_UPDATE_INTERVAL)
        # cursor.close()


if __name__ == "__main__":
    dialogue_update_loop()
