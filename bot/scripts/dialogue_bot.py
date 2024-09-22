from bot.scripts.form import add_form_entry, get_form_response
from bot.scripts.logger import log, log2
from bot.scripts.reddit_bot import reddit_bot
from mongo_db.db import db


class DialogueBot:
    def run(self, conv, user_model):
        username = conv.participant.name
        subreddit = str(conv.owner)

        bot_responses = db.bot_responses.get(subreddit)

        # this logic has moved to the trigger class. so we only get triggered if no human mod is involved.
        if reddit_bot.has_mod_been_involved(conv):
            # mod has been involved so ignore this conversation
            log2(subreddit, conv.id, "Human mod involved, IGNORED")
            db.users.update(conv, 'mod_involved', True)
        else:
            if not reddit_bot.have_we_replied(conv):
                log2(subreddit, conv.id, f"User `{username}`: We haven't replied")
                # we have not replied, so create a new contact and share form link
                log2(subreddit, conv.id, f"User `{username}`: Creating form entry")
                entry = add_form_entry(username, subreddit)
                if not entry:
                    log2(subreddit, conv.id, f"User `{username}`: Error creating form entry")
                # provide the first response, and share the form link
                log2(subreddit, conv.id, f"User `{username}`: Sharing form...")
                reddit_bot.reply_to_mod_mail_conversation(conv,
                                                          bot_responses['initial'],
                                                          form_shared=True)
                reddit_bot.archive_conversation(conv)
                # db.users.update(conv, 'form_shared', True)

            else:
                log2(subreddit, conv.id, "Bot already replied, OK")

                if user_model['note_shared']:
                    log2(subreddit, conv.id, "Note already shared with mods, DONE")
                    return

                log2(subreddit, conv.id, f"User `{username}`: Check if form filled")
                form_response = get_form_response(username, subreddit)

                if form_response is None:
                    # some error in collecting responses from qualtrics
                    log(f'Passing on the error via mod note', conv_id=conv.id)
                    self.create_mod_note(conv, "I'm having trouble accessing user responses from Qualtrics.",
                                         error=True)
                    form_response = {}

                elif form_response.filled():
                    log2(subreddit, conv.id, f"User `{username}`: Form filled, OK")
                    # user has submitted the form
                    db.users.update(conv, 'form_filled', True)
                    reddit_bot.reply_to_mod_mail_conversation(conv, bot_responses['final'])
                    log2(subreddit, conv.id, "Sending note for mods...")
                    self.create_mod_note(conv, form_response)
                    reddit_bot.unarchive_conversation(conv)

                else:
                    # user has not submitted any response yet
                    if reddit_bot.is_new_reply_from_user(conv):
                        log2(subreddit, conv.id, "Form not filled, Reminding user...")
                        reddit_bot.reply_to_mod_mail_conversation(conv, bot_responses['reminder'])
                        reddit_bot.archive_conversation(conv)
                    else:
                        log2(subreddit, conv.id, "No response from user yet, DONE")

    def clean_user_text(self, user_response):
        pass

    def create_mod_note(self, conv, form_response, error=False,
                        print_flag=False):
        # to pass on any kind of expected error to the mods, so they can report it to us.
        if error:
            reddit_bot.reply_to_mod_mail_conversation(conv, form_response,
                                                      mod_note=True)
        else:
            # no cleaning takes place as of now
            self.clean_user_text(form_response)

            # todo: bold
            response_text = "**User's reflection on their behavior**" + "\n\n" + \
                form_response.describe_actions + '\n\n' + \
                "**User's explanation of the rule led to their ban**" + "\n\n" + \
                form_response.describe_rule + '\n\n' + \
                "**Changes in the future**" + "\n\n" + \
                form_response.what_steps

            if not print_flag:
                reddit_bot.reply_to_mod_mail_conversation(conv, response_text,
                                                          mod_note=True)
            else:
                with open('examples/mod-notes.txt', 'a') as outputfile:
                    output = conv.id + '\n' + response_text + '\n'
                    outputfile.write(output)


dialogue_bot = DialogueBot()
