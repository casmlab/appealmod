

class Dialogue:

    def run(self, conversation, user_model):
        ...

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

    ...

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
