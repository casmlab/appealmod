from pymongo import MongoClient
from core.config import Config as config
from core.models.question import Question
from core.scripts.db import Database
from core.scripts.redditLogging import log, has_conversation_been_logged, \
    update_user_data
from core.scripts.qualtrics import get_survey_response, update_contacts_list
from core.scripts.qualtricsMap import QualtricsMap as qm


class Dialogue:
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    def run(self, conversation, user_model):
        # subreddit_name = 'r/'+str(conversation.owner)
        reddit_username = conversation.participant.name
        subreddit = str(conversation.owner)
        responses = self.db.get_responses(subreddit)

        # this logic has moved to the trigger class. so we only get triggered if no human mod is involved.
        if self.bot.has_mod_been_involved(conversation):
            # mod has been involved so ignore this conversation
            log(f"A human mod has been involved in this conversation {conversation.id}, will be ignored by our bot",
                conversation_id=conversation.id)
            update_user_data(conversation, 'mod_involved', True)
        else:
            if not self.bot.have_we_replied(conversation):
                # we have not replied, so create a new contact and share form link
                update_contacts_list(reddit_username, subreddit)  # todo: create a new entry in our DB
                # provide the first response, and share the form link
                log(f'Sharing the form link with the user',
                    conversation_id=conversation.id)
                self.bot.reply_to_mod_mail_conversation(conversation,
                                                        responses['initial'],
                                                        form_shared=True)
                self.bot.archive_conversation(conversation)
                # update_user_data(conversation, 'form_shared', True)

            else:

                if user_model['note_shared']:
                    log(f'User responses have already been shared with the mods')
                    return

                log(f'Trying to retrieve any exising form responses from the user {reddit_username}',
                    conversation_id=conversation.id)
                user_response = \
                    get_survey_response(reddit_username, subreddit, None)  # todo: check if user filled out our form

                if user_response is None:
                    # some error in collecting responses from qualtrics
                    log(f'Passing on the error via mod note',
                        conversation_id=conversation.id)
                    self.create_mod_note(conversation, "I'm having trouble accessing user responses from Qualtrics.",
                                         error=True)
                    user_response = {}

                elif len(user_response) > 0:
                    # user has submitted the form
                    update_user_data(conversation, 'form_filled', True)
                    self.bot.reply_to_mod_mail_conversation(conversation, responses['final'])
                    log(f'Retrieved user survey response, creating a note for the mods',
                        conversation_id=conversation.id)
                    self.create_mod_note(conversation, user_response)
                    self.bot.unarchive_conversation(conversation)

                else:
                    # user has not submitted any response yet
                    if self.bot.is_new_reply_from_user(conversation):
                        log(f'User survey response not found, reminding user to fill up the form',
                            conversation_id=conversation.id)
                        self.bot.reply_to_mod_mail_conversation(conversation, responses['reminder'])
                        self.bot.archive_conversation(conversation)
                    else:
                        log(f'No response from the user yet',
                            conversation_id=conversation.id)

            # if self.bot.is_new_reply_from_user(conversation):
            # # all our actions are triggered by some response from the user
            # log(f"User has responsed to the conversation {conversation.id}", conversationID=conversation.id)

            # # start_time = self.bot.get_conversation_first_message_time(conversation)
            # log(f'Trying to retrieve any exising form responses from the user {reddit_username}', conversationID=conversation.id)
            # user_response = get_survey_response(reddit_username, None)

            # if user_response is None:
            #     # some error in collecting responses from qualtrics
            #     self.create_mod_note(conversation, "I'm having trouble accessing user responses from Qualtrics.", error=True)
            #     user_response = {}

            # added the extra condition on user response, so if a user has already filled a form, we don't share the link again.
            # this will handle the case where a banned user starts a new modmail conv.
            # if not self.bot.haveWeReplied(conversation) and len(user_response) == 0:
            #     # we have not replied, so create a new contact and share form link
            #     update_contacts_list(reddit_username)
            #     #provide the first response, and share the form link
            #     log(f'Sharing the form link with the user', conversationID=conversation.id)
            #     self.bot.reply_to_mod_mail_conversation(conversation, responses['initial'])
            #     self.bot.archive_conversation(conversation)

            # treatment has been delivered so now we can update the user db with user info.
            # log_user_data(conversation,1)

            # else:

            # we have already replied, so check for whether user has submitted the form
            # start_time = self.bot.get_conversation_first_message_time(conversation)
            # log(f'This is an ongoing conversation, retrieving survey response for user {reddit_username} starting from {start_time}', conversationID=conversation.id)
            # user_response = get_survey_response(reddit_username, start_time)

            # if user_response is None:
            #     # some error in collecting responses from qualtrics
            #     self.create_mod_note(conversation, "I'm having trouble accessing user responses from Qualtrics.", error=True)

            # elif len(user_response) == 0:
            #     # user has not submitted any response yet
            #     log(f'User survey response not found, reminding user to fill up the form', conversationID=conversation.id)
            #     self.bot.reply_to_mod_mail_conversation(conversation, responses['reminder'])
            #     self.bot.archive_conversation(conversation)

        #     else:
        #         # user has submitted the form
        #         update_user_data(conversation)
        #         self.bot.reply_to_mod_mail_conversation(conversation, responses['final'])
        #         log(f'Retrieved user survey response, creating a note for the mods', conversationID=conversation.id)
        #         self.create_mod_note(conversation, user_response)
        #         self.bot.unarchive_conversation(conversation)

        # else:
        #     log(f'No response from the user yet', conversationID=conversation.id)

    def clean_user_text(self, user_response):
        pass

    def create_mod_note(self, conversation, user_response, error=False,
                        print_flag=False):
        # to pass on any kind of expected error to the mods, so they can report it to us.
        if error:
            self.bot.reply_to_mod_mail_conversation(conversation, user_response,
                                                    mod_note=True)
        else:
            notes_list = qm.DICTIONARY

            # so that the responses always go in the fixed order
            notes_list = sorted(notes_list, key=lambda d: d['note_order'])

            # no cleaning takes place as of now
            self.clean_user_text(user_response)

            response_text = ""

            for mydict in notes_list:
                qid = mydict['question_id']
                # this particular question hasn't been answered by the user, so skip
                if qid not in user_response.keys():
                    continue

                if isinstance(user_response[qid], list):
                    response_text += mydict['mod_note'] + ':: '
                    for i, comment in enumerate(user_response[qid]):
                        response_text += str(i + 1) + '. ' + comment + '\n\n'
                    response_text += '\n'
                    # response_text += mydict['mod_note'] + ':: ' + '\n'.join(user_response[qid]) + '\n\n'
                else:
                    response_text += mydict['mod_note'] + ':: ' + str(user_response[qid]) + '\n\n'

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
    #         log(f"This is an existing conversation {conversation.id}")
    #         if self.bot.is_new_reply_from_user(conversation):
    #             log(f"Last response is from the user")
    #             # if not is_message_profane(modmail_conversation.messages[-1].body_markdown):
    #             if not config.DEBUG: 
    #                 self.bot.unarchive_conversation(conversation)
    #                 log(f"Conversation is unarchived {conversation.id}")
    #             # else:
    #             #     log(f"User response is toxic, conversation will remain archived {conversation.id}")
    #     else:
    #         log(f"This is a new conversation, initiating a reply {conversation.id}")
    #         questions = self.d.extract_subreddit_questions(subreddit_name)
    #         reply = ""
    #         for question in questions:
    #             reply += question['question text'] + '\n'
    #         log(f"Received the list of questions {reply}")
    #         if not config.DEBUG:
    #             self.bot.reply_to_mod_mail_conversation(conversation,reply)
    #             self.bot.archive_conversation(conversation)
    #             log(f"The conversation has been replied to and archived {conversation.id}")
