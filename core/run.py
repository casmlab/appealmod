from conf import conf
from scripts.bot import Bot
from scripts.trigger import should_trigger_reply
from scripts.redditLogging import has_conversation_been_logged, log_conversation, \
    log, sanitize_object_for_mongo, log_user_data, check_user_model, \
    update_conv_ids
from config import Config as config
from scripts.db import Database
from scripts.dialogue import Dialogue
from numpy.random import binomial
from prawcore.exceptions import ServerError, RequestException
import traceback
import time


def get_user_model(modmail_conversation, treatment_fraction=config.TREATMENT_FRACTION):
    user_model = check_user_model(modmail_conversation.participant.name)  # to check if this is a repeat user.

    if user_model is not None:  # this is repeat user
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

    log('***********Starting bot*****************')
    log(f'Beginning driver loop')
    # consider all msgs not just appeals...
    while True:
        try:
            for modmail_conversation in bot.get_conversations():
                current_subreddit = str(modmail_conversation.owner)
                log(f'Received new modmail conversation: {modmail_conversation.id}',
                    conversation_id=modmail_conversation.id)

                if should_trigger_reply(bot, modmail_conversation, current_subreddit):
                    log(f'conversation {modmail_conversation.id} classified as a ban appeal',
                        conversation_id=modmail_conversation.id)

                    user_model = get_user_model(modmail_conversation)

                    if user_model['group'] == 1:  # treatment condition
                        log(f'Conversation {modmail_conversation.id} is assigned to the treatment group',
                            conversation_id=modmail_conversation.id)
                        # offense = bot.get_user_ban_information(modmail_conversation.participant.name, current_subreddit)
                        log(f'Initiating the dialogue flow',
                            conversation_id=modmail_conversation.id)
                        dialogue.run(modmail_conversation, user_model)

                    else:  # control condition
                        log(f'Conversation {modmail_conversation.id} is assigned to the control group',
                            conversation_id=modmail_conversation.id)
                        # log_user_data(modmail_conversation, group)

                    if not has_conversation_been_logged(modmail_conversation):
                        log_conversation(modmail_conversation, bot)
                else:
                    log(f'Conversation {modmail_conversation.id} is not a ban appeal, will be ignored',
                        conversation_id=modmail_conversation.id)

        except (ServerError, RequestException) as e:
            error_message = traceback.format_exc()
            log(error_message, conversation_id=modmail_conversation.id)
            log(f'Received an exception from praw, retrying in 30 secs',
                conversation_id=modmail_conversation.id)
            time.sleep(300)  # try again after 5 mins...


if __name__ == "__main__":
    main()
