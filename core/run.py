from conf import conf
from scripts.bot import Bot
from scripts.trigger import should_trigger_reply
from scripts.logger import has_conversation_been_logged, log_conversation, \
    log, sanitize_object_for_mongo, log_user_data, \
    update_conv_ids, log2, user_logs_collection
from config import Config as config
from scripts.db import Database
from scripts.dialogue import Dialogue
from numpy.random import binomial
from prawcore.exceptions import ServerError, RequestException
import traceback
import time


def get_user_model(modmail_conversation,
                   treatment_fraction=config.TREATMENT_FRACTION):

    username = modmail_conversation.participant.name
    subreddit = str(modmail_conversation.owner)
    user_model = user_logs_collection.find_one({"username": username,
                                                "subreddit": subreddit})

    if user_model:  # this is repeat user
        conv_id = modmail_conversation.id
        log2(conv_id, f'  - User `{username}`: Found in DB')
        # update conv ids if this is a new conversation
        update_conv_ids(modmail_conversation, user_model)
        return user_model

    else:
        group = binomial(1, treatment_fraction)  # assign a new random group. 1 denotes treatment. 0 denotes control
        # we log user data here.
        user_model = log_user_data(modmail_conversation, group)
        return user_model


def main():
    """
    Driver function
    Add testing functions
    """
    bot = Bot(conf.subreddits_ids)
    dialogue = Dialogue(bot)
    exception_flag = False
    # NOTE: Any conversation-specific logic should NOT be a part of this driver class
    # NOTE: Peripheral things such as logging the conversation should be a part of the driver class

    log('Starting bot...')
    # consider all msgs not just appeals...
    while True:
        try:
            for modmail_conversation in bot.get_conversations():
                conv_id = modmail_conversation.id
                subreddit = str(modmail_conversation.owner)
                log(f'*** `{conv_id}` conversation in `r/{subreddit}` {"*" * 20}', conv_id)

                if should_trigger_reply(bot, modmail_conversation, subreddit):
                    log2(conv_id, f"It's a ban appeal, OK")

                    user_model = get_user_model(modmail_conversation)

                    if user_model['group'] == 1:  # treatment condition
                        log2(conv_id, "It's treatment group, OK")
                        # offense = bot.get_user_ban_information(modmail_conversation.participant.name, subreddit)
                        log2(conv_id, "Running dialogue flow...")
                        dialogue.run(modmail_conversation, user_model)

                    else:  # control condition
                        log2(conv_id, "It's control group, IGNORED")
                        # log_user_data(modmail_conversation, group)

                    if not has_conversation_been_logged(modmail_conversation):
                        log_conversation(modmail_conversation, bot)
                else:
                    log2(conv_id, "It's NOT a ban appeal, IGNORED")

        except (ServerError, RequestException) as e:
            error_message = traceback.format_exc()
            log(error_message, conv_id)
            log(f'Received an exception from praw, retrying in 30 secs', conv_id)
            time.sleep(300)  # try again after 5 mins...


if __name__ == "__main__":
    main()
