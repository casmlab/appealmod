from bs4 import BeautifulSoup
from prawcore.exceptions import Forbidden

from bot.src.logger.utils import md_code, log_conv
from bot.src.logger.L import L
from bot.src.reddit_bot import reddit_bot
from utils.slack.webhooks import slack_steps_conv, slack_alert_conv


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
        log_conv(f'Pre-emptive ban by an anti-brigade bot, IGNORED')
        slack_steps_conv('✖️ Pre-emptive ban by an anti-brigade bot')
        return False

    elif conv.authors[-1].name.lower() == 'saferbot':  # another bot used in reddit
        log_conv(f'Used saferbot already, IGNORED')
        slack_steps_conv('✖️ Used saferbot already')
        return False

    for author in conv.authors:
        try:
            if reddit_bot.is_user_banned_from_subreddit(author, L.subreddit):

                if 'temporarily banned' in conv.subject:
                    # ignore temp bans...
                    log_conv(f'Is a temp ban, IGNORED')
                    slack_steps_conv('✖️ Temp ban')
                    return False

                elif reddit_bot.has_mod_been_involved(conv):
                    # mod has been involved so ignore this conversation
                    log_conv(f"A human mod has been involved in this conversation {L.conv_id}, IGNORED")
                    slack_steps_conv('✖️ Human involved')
                    return False

                elif not contains_reason(conv):
                    log_conv(f"Ban with no reason, IGNORED")
                    if not reddit_bot.have_we_replied(conv):
                        log_conv(f"Writing a mod note: ban reason is missing")
                        reply = 'Hi mods, it seems that the reason for ban is not available for this user so I will not engage with them.'
                        reddit_bot.reply_to_mod_mail_conversation(
                            conv, reply, mod_note=True, update=False
                        )
                        log_conv(f"Replied with message: {md_code(reply)}")
                    slack_steps_conv('✖️ Ban with no reason')
                    return False

                elif autoban_involved(author):
                    log_conv(f'Ban note is "Autoban", IGNORED')
                    if not reddit_bot.have_we_replied(conv):
                        log_conv(f'Writing a mod note: ban note is "Autoban"')
                        reply = 'Hi mods, it seems that the ban note contains "Autoban", so I will not participate further.'
                        reddit_bot.reply_to_mod_mail_conversation(
                            conv, reply, mod_note=True, update=False
                        )
                        log_conv(f"Replied with message: {md_code(reply)}")
                    slack_steps_conv('✖️ Ban note is "Autoban"')
                    return False

                else:

                    return True

        except Forbidden:
            log_conv(f'Unable to get user ban status {author}')
            slack_alert_conv(f'✖️ Unable to get user ban status {author}')

    return False
