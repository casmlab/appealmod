from bs4 import BeautifulSoup
from prawcore.exceptions import Forbidden

from bot.src.logger.L import L
from bot.src.reddit_bot import reddit_bot


def contains_reason(conv):
    first_msg = sorted(conv.messages, key=lambda x: x.date)[0]

    if first_msg.author.name == conv.participant.name:
        # this is a fresh conv from the user, so we can't check for reason.
        return True

    html_text = first_msg.body
    soup = BeautifulSoup(html_text, 'html.parser')
    a = soup.find('blockquote')
    if a is None:
        return False
    else:
        return True


def autoban_involved(author):
    ban = reddit_bot.get_user_ban_information(author, L.subreddit)
    if ban['note'].startswith('Autoba'):
        return True
    return False


def should_trigger_reply(conv):
    """
    returns true if a conversation should trigger a reply
    is it assumed that the conversation was unread before this function is called
    """

    # return conversation.num_messages < 2 and bot.isUserBannedFromSubreddit(conversation.author)
    if conv.authors[-1].name == 'ArchangelleN8theGr8':  # another bot used in reddit
        L.step('🚫 Pre-emptive ban by an anti-brigade bot', main=True)
        return False

    elif conv.authors[-1].name.lower() == 'saferbot':  # another bot used in reddit
        L.step('🚫 Used saferbot already', main=True)
        return False

    for author in conv.authors:
        try:
            if reddit_bot.is_user_banned_from_subreddit(author, L.subreddit):

                if 'temporarily banned' in conv.subject:
                    L.step('🚫 Temp ban', main=True)
                    return False

                elif reddit_bot.has_mod_been_involved(conv):
                    L.step('🚫 Human mod involved', main=True)
                    return False

                elif not contains_reason(conv):
                    L.step('🚫 Ban with no reason', main=True)

                    if not reddit_bot.have_we_replied(conv):
                        L.logging(f"Writing a mod note: ban reason is missing")
                        reply = 'Hi mods, it seems that the reason for ban is not available for this user so I will not engage with them.'
                        reddit_bot.reply_to_mod_mail_conversation(
                            conv, reply, mod_note=True, update=False
                        )

                    return False

                elif autoban_involved(author):
                    L.step('🚫 Ban note is "Autoban"', main=True)

                    if not reddit_bot.have_we_replied(conv):
                        L.logging(f'Writing a mod note: ban note is "Autoban"')
                        reply = 'Hi mods, it seems that the ban note contains "Autoban", ' \
                                'so I will not participate further.'
                        reddit_bot.reply_to_mod_mail_conversation(
                            conv, reply, mod_note=True, update=False
                        )

                    return False

                else:

                    return True

        except Forbidden:
            L.alert(f'📛 Unable to get user ban status {author}')

    return False
