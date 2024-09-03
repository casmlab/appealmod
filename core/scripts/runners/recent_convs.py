import time
import traceback

from numpy.random import binomial
from prawcore.exceptions import ServerError, RequestException

from core.config import Config as config
from core.scripts.dialogue_bot import dialogue_bot
from core.scripts.logger import has_conversation_been_logged, log_conversation, \
    log, log_user_data, update_conv_ids, log2, user_logs_collection
from core.scripts.reddit_bot import reddit_bot
from core.scripts.trigger import should_trigger_reply


def get_user_model(modmail_conversation,
                   treatment_fraction=config.TREATMENT_FRACTION):

    username = modmail_conversation.participant.name
    subreddit = str(modmail_conversation.owner)
    user_model = user_logs_collection.find_one({"username": username,
                                                "subreddit": subreddit})

    if user_model:  # this is repeat user
        conv_id = modmail_conversation.id
        log2(subreddit, conv_id, f'User `{username}`: Found in DB')
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
    exception_flag = False
    # NOTE: Any conversation-specific logic should NOT be a part of this driver class
    # NOTE: Peripheral things such as logging the conversation should be a part of the driver class

    log('Starting bot...')
    # consider all msgs not just appeals...
    while True:
        try:
            for conv in reddit_bot.get_conversations():
                conv_id = conv.id
                subreddit = str(conv.owner)
                log(f'*** `{subreddit}/{conv_id}` processing conversation... {"*" * 20}', conv_id)

                if should_trigger_reply(reddit_bot, conv, subreddit):
                    log2(subreddit, conv_id, "It's a ban appeal, OK")

                    user_model = get_user_model(conv)

                    if user_model['group'] == 1:  # treatment condition
                        log2(subreddit, conv_id, "It's treatment group, OK")
                        # offense = bot.get_user_ban_information(conv.participant.name, subreddit)
                        log2(subreddit, conv_id, "Running dialogue flow...")
                        dialogue_bot.run(conv, user_model)

                    else:  # control condition
                        log2(subreddit, conv_id, "It's control group, IGNORED")
                        # log_user_data(conv, group)

                    if not has_conversation_been_logged(conv):
                        log_conversation(conv, reddit_bot)
                else:
                    log2(subreddit, conv_id, "It's NOT a ban appeal, IGNORED")

        except (ServerError, RequestException) as e:
            error_message = traceback.format_exc()
            log(error_message, conv_id)
            log(f'Received an exception from praw, retrying in 30 secs', conv_id)
            time.sleep(300)  # try again after 5 mins...


if __name__ == "__main__":
    main()
