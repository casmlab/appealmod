from bs4 import BeautifulSoup
from prawcore.exceptions import Forbidden

from core.scripts.logger import log2


def contains_reason(conversation):
    first_msg = sorted(conversation.messages, key=lambda x: x.date)[0]

    if first_msg.author.name == conversation.participant.name:
        # this is a fresh conv from the user, so we can't check for reason.
        return True

    html_text = first_msg.body
    soup = BeautifulSoup(html_text, 'html.parser')
    a = soup.find('blockquote')
    if a is None:
        return False
    else:
        return True


def should_trigger_reply(bot, conversation, subreddit):
    """
    returns true if a conversation should trigger a reply
    is it assumed that the conversation was unread before this function is called
    """
    conv_id = conversation.id

    # return conversation.num_messages < 2 and bot.isUserBannedFromSubreddit(conversation.author)
    if conversation.authors[-1].name == 'ArchangelleN8theGr8':  # another bot used in reddit
        log2(subreddit, conv_id, f'Pre-emptive ban by an anti-brigade bot, IGNORED')
        return False

    for author in conversation.authors:
        try:
            if bot.is_user_banned_from_subreddit(author, subreddit):

                if 'temporarily banned' in conversation.subject:
                    # ignore temp bans...
                    log2(subreddit, conv_id, f'Is a temp ban, IGNORED')
                    return False

                elif bot.has_mod_been_involved(conversation):
                    # mod has been involved so ignore this conversation
                    log2(subreddit, conv_id, f"A human mod has been involved in this conversation {conv_id}, IGNORED")
                    return False

                elif not contains_reason(conversation):
                    log2(subreddit, conv_id, f"Ban with no reason, IGNORED")
                    if not bot.have_we_replied(conversation):
                        log2(subreddit, conv_id, f"Writing a mod note: ban reason is missing")
                        response = 'Hi mods, it seems that the reason for ban is not available for this user so I will not engage with them.'
                        bot.reply_to_mod_mail_conversation(conversation, response,
                                                           mod_note=True, update=False)
                    return False

                else:

                    return True

        except Forbidden:
            log2(subreddit, conv_id, f'Unable to get user ban status {author}')

    return False
