import praw
from core.config import Config as config
from dateutil.parser import parse
from core.scripts.logger import log, update_user_data, log_str, log2


class Bot:
    def __init__(self, subreddits, debug=config.DEBUG):
        """
        Authorize the reddit account with 'script' privileges
        """
        # print(config.REDDIT_EMAIL)
        self.subreddits = subreddits
        self.last_read_conversation_id = None  # ToDo: read from database
        self.reddit = praw.Reddit(
            client_id=config.CLIENT_ID,
            client_secret=config.CLIENT_SECRET,
            user_agent=config.USER_AGENT,
            username=config.REDDIT_USERNAME,
            password=config.REDDIT_PASSWORD,
        )
        self.DEBUG = debug

    def test_connect(self):  # fixme: never used?
        """
        Test authorization by printing top 25 hotest post from r/uofm
        """
        for submission in self.reddit.subreddit(self.subreddits[0]).hot(limit=25):
            print(submission.title)
        # print(self.reddit.user.me())

    def get_all_mod_mail_conversations(self, subreddit, state="mod"):  # fixme: never used?
        """
        Returns a list of all modmail conversations for a subreddit
        """
        # return list(self.reddit.subreddit(subreddit).modmail.conversations(state=state))
        return list(self.reddit.subreddit(subreddit).modmail.conversations(state=state))

    def get_unread_mod_mail_conversations(self, subreddit, state="mod"):  # fixme: never used?
        """
        returns a list of unread modmail conversations for a subreddit
        """
        result = None
        if self.last_read_conversation_id:
            result = list(self.reddit.subreddit(subreddit).modmail.conversations(state=state, after=self.last_read_conversation_id))
        else:
            result = list(self.reddit.subreddit(subreddit).modmail.conversations(state=state))
        if len(result) > 0:
            self.last_read_conversation_id = result[-1].id  # ToDo: write to database
        return result

    def conversation_has_one_message(self, conversation):  # fixme: never used?
        return conversation.num_messages == 1

    def reply_to_mod_mail_conversation(self, conversation, reply, mod_note=False,
                                       form_shared=False, update=True):
        """
        helper function to reply to a modmail conversation
        `mod_note`: should it be visible for user or not
        """
        if not self.DEBUG:
            conversation.reply(reply, internal=mod_note)
            if update and mod_note:
                update_user_data(conversation, 'note_shared', True)
            elif update and form_shared:
                update_user_data(conversation, 'form_shared', True)

        conv_id = conversation.id
        log2(conv_id, "Replied with message: {log_str(reply)}")

    def is_user_banned_from_subreddit(self, username, subreddit):
        """
        returns true if a user is in a subreddit's ban list
        """
        return any(self.reddit.subreddit(subreddit).banned(username))

    def get_user_ban_information(self, username, subreddit):
        """
        returns the ban object for a user
        """
        ban = list(self.reddit.subreddit(subreddit).banned(username))
        if len(ban):
            ban = ban[0]
            return vars(ban)
        else:
            return None # no ban exists for user

    def archive_conversation(self, conversation):
        """
        helper function to archive a modmail conversation
        """
        if not self.DEBUG:
            conversation.archive()
        conv_id = conversation.id
        log2(conv_id, "Conversation ARCHIVED")

    def unarchive_conversation(self, conversation):
        """
        helper function to unarchive a modmail conversation
        """
        if not self.DEBUG:
            conversation.unarchive()
        conv_id = conversation.id
        log2(conv_id, "Conversation UNARCHIVED")

    def is_replied(self, conversation):  # fixme: never used?
        """
        check if a mod has replied to this conversation
        And there is a new reply from user
        """
        # return true if mode has replied
        if conversation.last_mod_update < conversation.last_user_update:
            return True
        return False

    def is_new_reply_from_user(self, conversation):
        """
        check if a user has a new reply on this conversasion
        """
        # return true if user has a new reply
        return conversation.last_user_update == conversation.last_updated

    def have_we_replied(self, conversation):
        """
        check if our account (interactive-workflow) has replied to this modmail conversation
        """
        authors_name_set = set([x.name for x in conversation.authors])
        return config.REDDIT_USERNAME in authors_name_set

    def has_mod_been_involved(self, conversation):
        """
        check if a mod has been involved in this conversation
        """
        authors_excluding_first_message = \
            [x.author for x in sorted(conversation.messages, key=lambda x: x.date)][1:]
        authors_name_set = set([x.name for x in authors_excluding_first_message])
        participant_name = conversation.participant.name
        if participant_name in authors_name_set:
            authors_name_set.remove(participant_name)
        if config.REDDIT_USERNAME in authors_name_set:
            authors_name_set.remove(config.REDDIT_USERNAME)
        return len(authors_name_set) > 0

    def get_conversation_first_message_time(self, conversation):
        """
        returns the timestamp of the first message in a conversation from our bot
        """
        for message in conversation.messages:
            if message.author.name == config.REDDIT_USERNAME:
                return message.date
        return None

    def get_conversations(self):
        return self.reddit.subreddit(self.subreddits[0]).mod.stream.\
            modmail_conversations(sort="recent",
                                  other_subreddits=self.subreddits[1:])
