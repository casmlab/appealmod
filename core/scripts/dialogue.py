from pymongo import MongoClient
from core.config import Config as config
from core.models.question import Question
from core.scripts.db import Database
from core.scripts.form import add_form_entry, get_form_response
from core.scripts.logger import log, has_conversation_been_logged, \
    update_user_data, log2
from core.scripts.qualtricsMap import QualtricsMap as qm


class Dialogue:
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    def run(self, conversation, user_model):
        # subreddit_name = 'r/'+str(conversation.owner)
        username = conversation.participant.name
        conv_id = conversation.id
        subreddit = str(conversation.owner)
        bot_responses = self.db.get_responses(subreddit)

        # this logic has moved to the trigger class. so we only get triggered if no human mod is involved.
        if self.bot.has_mod_been_involved(conversation):
            # mod has been involved so ignore this conversation
            log2(conv_id, "Human mod involved, IGNORED")
            update_user_data(conversation, 'mod_involved', True)
        else:
            if not self.bot.have_we_replied(conversation):
                log2(conv_id, f"User `{username}`: We haven't replied")
                # we have not replied, so create a new contact and share form link
                log2(conv_id, f"User `{username}`: Creating form entry")
                add_form_entry(username, subreddit)
                # provide the first response, and share the form link
                log2(conv_id, f"User `{username}`: Sharing form...")
                self.bot.reply_to_mod_mail_conversation(conversation,
                                                        bot_responses['initial'],
                                                        form_shared=True)
                self.bot.archive_conversation(conversation)
                # update_user_data(conversation, 'form_shared', True)

            else:
                log2(conv_id, "Bot already replied, OK")

                if user_model['note_shared']:
                    log2(conv_id, "Note already shared with mods, DONE")
                    return

                log2(conv_id, f"User `{username}`: Check if form filled")
                form_response = get_form_response(username, subreddit)

                if form_response is None:
                    # some error in collecting responses from qualtrics
                    log(f'Passing on the error via mod note',
                        conversation_id=conv_id)
                    self.create_mod_note(conversation, "I'm having trouble accessing user responses from Qualtrics.",
                                         error=True)
                    form_response = {}

                elif form_response.filled():
                    log2(conv_id, f"User `{username}`: Form filled, OK")
                    # user has submitted the form
                    update_user_data(conversation, 'form_filled', True)
                    self.bot.reply_to_mod_mail_conversation(conversation, bot_responses['final'])
                    log2(conv_id, "Sending note for mods...")
                    self.create_mod_note(conversation, form_response)
                    self.bot.unarchive_conversation(conversation)

                else:
                    # user has not submitted any response yet
                    if self.bot.is_new_reply_from_user(conversation):
                        log2(conv_id, "Form not filled, Reminding user...")
                        self.bot.reply_to_mod_mail_conversation(conversation, bot_responses['reminder'])
                        self.bot.archive_conversation(conversation)
                    else:
                        log2(conv_id, "No response from user yet, DONE")

            # if self.bot.is_new_reply_from_user(conversation):
            # # all our actions are triggered by some response from the user
            # log(f"User has responsed to the conversation {conv_id}", conversationID=conv_id)

            # # start_time = self.bot.get_conversation_first_message_time(conversation)
            # log(f'Trying to retrieve any exising form responses from the user {username}', conversationID=conv_id)
            # form_response = get_survey_response(username, None)

            # if form_response is None:
            #     # some error in collecting responses from qualtrics
            #     self.create_mod_note(conversation, "I'm having trouble accessing user responses from Qualtrics.", error=True)
            #     form_response = {}

            # added the extra condition on user response, so if a user has already filled a form, we don't share the link again.
            # this will handle the case where a banned user starts a new modmail conv.
            # if not self.bot.haveWeReplied(conversation) and len(form_response) == 0:
            #     # we have not replied, so create a new contact and share form link
            #     update_contacts_list(username)
            #     #provide the first response, and share the form link
            #     log(f'Sharing the form link with the user', conversationID=conv_id)
            #     self.bot.reply_to_mod_mail_conversation(conversation, bot_responses['initial'])
            #     self.bot.archive_conversation(conversation)

            # treatment has been delivered so now we can update the user db with user info.
            # log_user_data(conversation,1)

            # else:

            # we have already replied, so check for whether user has submitted the form
            # start_time = self.bot.get_conversation_first_message_time(conversation)
            # log(f'This is an ongoing conversation, retrieving survey response for user {username} starting from {start_time}', conversationID=conv_id)
            # form_response = get_survey_response(username, start_time)

            # if form_response is None:
            #     # some error in collecting responses from qualtrics
            #     self.create_mod_note(conversation, "I'm having trouble accessing user responses from Qualtrics.", error=True)

            # elif len(form_response) == 0:
            #     # user has not submitted any response yet
            #     log(f'User survey response not found, reminding user to fill up the form', conversationID=conv_id)
            #     self.bot.reply_to_mod_mail_conversation(conversation, bot_responses['reminder'])
            #     self.bot.archive_conversation(conversation)

        #     else:
        #         # user has submitted the form
        #         update_user_data(conversation)
        #         self.bot.reply_to_mod_mail_conversation(conversation, bot_responses['final'])
        #         log(f'Retrieved user survey response, creating a note for the mods', conversationID=conv_id)
        #         self.create_mod_note(conversation, form_response)
        #         self.bot.unarchive_conversation(conversation)

        # else:
        #     log(f'No response from the user yet', conversationID=conv_id)

    def clean_user_text(self, user_response):
        pass

    def create_mod_note(self, conversation, form_response, error=False,
                        print_flag=False):
        # to pass on any kind of expected error to the mods, so they can report it to us.
        if error:
            self.bot.reply_to_mod_mail_conversation(conversation, form_response,
                                                    mod_note=True)
        else:
            notes_list = qm.DICTIONARY

            # so that the responses always go in the fixed order
            notes_list = sorted(notes_list, key=lambda d: d['note_order'])

            # no cleaning takes place as of now
            self.clean_user_text(form_response)

            # todo: bold
            response_text = "User's reflection on their behavior:" + "\n" + \
                form_response.describe_actions + '\n\n' + \
                "User's explanation of the rule led to their ban:" + "\n" + \
                form_response.describe_rule + '\n\n' + \
                "Changes in the future" + "\n" + \
                form_response.what_steps

            if not print_flag:
                self.bot.reply_to_mod_mail_conversation(conversation, response_text,
                                                        mod_note=True)
            else:
                with open('examples/mod-notes.txt', 'a') as outputfile:
                    output = conversation.id + '\n' + response_text + '\n'
                    outputfile.write(output)

    # def run(self,conversation):
    #     subreddit_name = 'r/'+str(conversation.owner)
    #     # If debug is true, we don't do any archive, any reply.

    #     if has_conversation_been_logged(conversation):
    #         log(f"This is an existing conversation {conv_id}")
    #         if self.bot.is_new_reply_from_user(conversation):
    #             log(f"Last response is from the user")
    #             # if not is_message_profane(modmail_conversation.messages[-1].body_markdown):
    #             if not config.DEBUG: 
    #                 self.bot.unarchive_conversation(conversation)
    #                 log(f"Conversation is unarchived {conv_id}")
    #             # else:
    #             #     log(f"User response is toxic, conversation will remain archived {conv_id}")
    #     else:
    #         log(f"This is a new conversation, initiating a reply {conv_id}")
    #         questions = self.d.extract_subreddit_questions(subreddit_name)
    #         reply = ""
    #         for question in questions:
    #             reply += question['question text'] + '\n'
    #         log(f"Received the list of questions {reply}")
    #         if not config.DEBUG:
    #             self.bot.reply_to_mod_mail_conversation(conversation,reply)
    #             self.bot.archive_conversation(conversation)
    #             log(f"The conversation has been replied to and archived {conv_id}")
