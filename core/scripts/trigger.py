from prawcore.exceptions import Forbidden
from core.scripts.redditLogging import log
from bs4 import BeautifulSoup


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
    # return conversation.num_messages < 2 and bot.isUserBannedFromSubreddit(conversation.author)
    if conversation.authors[-1].name == 'ArchangelleN8theGr8':  # another bot used in reddit
        log(f'This is a pre-emptive ban by an anti-brigade bot, will be ignored',
            conversation_id=conversation.id)
        return False

    for author in conversation.authors:
        # print(author)
        try: 
            if bot.is_user_banned_from_subreddit(author, subreddit):

                if 'temporarily banned' in conversation.subject:
                    # ignore temp bans... 
                    log(f'The conv {conversation.id} is a temp ban, will be ignored',
                        conversation_id=conversation.id)
                    return False

                elif bot.has_mod_been_involved(conversation):
                    # mod has been involved so ignore this conversation
                    log(f"A human mod has been involved in this conversation {conversation.id}, will be ignored by our bot",
                        conversation_id=conversation.id)
                    return False
                
                elif not contains_reason(conversation):
                    log(f"For conversation {conversation.id}, the ban contains no reason, will be ignored.",
                        conversation_id=conversation.id)
                    if not bot.have_we_replied(conversation):
                        log(f"Writing a mod note to inform mods that the reason for ban is missing",
                            conversation_id=conversation.id)
                        response = 'Hi mods, it seems that the reason for ban is not available for this user so I will not engage with them.'
                        bot.reply_to_mod_mail_conversation(conversation, response,
                                                           mod_note=True, update=False)
                    return False 

                else:
                    return True

        except Forbidden:
            log(f'Unable to get user ban status {author}',
                conversation_id=conversation.id)

    return False
