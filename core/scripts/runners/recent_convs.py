import time
import traceback

from prawcore.exceptions import ServerError, RequestException

from core.scripts.db.db import db
from core.scripts.dialogue_bot import dialogue_bot
from core.scripts.logger import log, log2, get_user_model
from core.scripts.reddit_bot import reddit_bot
from core.scripts.trigger import should_trigger_reply


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

                    if not db.conversations.find(conv):
                        db.conversations.add(conv, reddit_bot)
                else:
                    log2(subreddit, conv_id, "It's NOT a ban appeal, IGNORED")

        except (ServerError, RequestException) as e:
            error_message = traceback.format_exc()
            log(error_message, conv_id)
            log(f'Received an exception from praw, retrying in 30 secs', conv_id)
            time.sleep(300)  # try again after 5 mins...


if __name__ == "__main__":
    main()
