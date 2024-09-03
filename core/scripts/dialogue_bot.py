from core._old.qualtricsMap import QualtricsMap as qm
from core.scripts.db import Database
from core.scripts.form import add_form_entry, get_form_response
from core.scripts.logger import log, update_user_data, log2
from core.scripts.reddit_bot import reddit_bot


class DialogueBot:
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
            log2(subreddit, conv_id, "Human mod involved, IGNORED")
            update_user_data(conversation, 'mod_involved', True)
        else:
            if not self.bot.have_we_replied(conversation):
                log2(subreddit, conv_id, f"User `{username}`: We haven't replied")
                # we have not replied, so create a new contact and share form link
                log2(subreddit, conv_id, f"User `{username}`: Creating form entry")
                entry = add_form_entry(username, subreddit)
                if not entry:
                    log2(subreddit, conv_id, f"User `{username}`: Error creating form entry")
                # provide the first response, and share the form link
                log2(subreddit, conv_id, f"User `{username}`: Sharing form...")
                self.bot.reply_to_mod_mail_conversation(conversation,
                                                        bot_responses['initial'],
                                                        form_shared=True)
                self.bot.archive_conversation(conversation)
                # update_user_data(conversation, 'form_shared', True)

            else:
                log2(subreddit, conv_id, "Bot already replied, OK")

                if user_model['note_shared']:
                    log2(subreddit, conv_id, "Note already shared with mods, DONE")
                    return

                log2(subreddit, conv_id, f"User `{username}`: Check if form filled")
                form_response = get_form_response(username, subreddit)

                if form_response is None:
                    # some error in collecting responses from qualtrics
                    log(f'Passing on the error via mod note',
                        conversation_id=conv_id)
                    self.create_mod_note(conversation, "I'm having trouble accessing user responses from Qualtrics.",
                                         error=True)
                    form_response = {}

                elif form_response.filled():
                    log2(subreddit, conv_id, f"User `{username}`: Form filled, OK")
                    # user has submitted the form
                    update_user_data(conversation, 'form_filled', True)
                    self.bot.reply_to_mod_mail_conversation(conversation, bot_responses['final'])
                    log2(subreddit, conv_id, "Sending note for mods...")
                    self.create_mod_note(conversation, form_response)
                    self.bot.unarchive_conversation(conversation)

                else:
                    # user has not submitted any response yet
                    if self.bot.is_new_reply_from_user(conversation):
                        log2(subreddit, conv_id, "Form not filled, Reminding user...")
                        self.bot.reply_to_mod_mail_conversation(conversation, bot_responses['reminder'])
                        self.bot.archive_conversation(conversation)
                    else:
                        log2(subreddit, conv_id, "No response from user yet, DONE")

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


dialogue_bot = DialogueBot(reddit_bot)
