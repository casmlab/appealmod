from bot.src.form import add_form_entry, get_form_response
from bot.src.logger import log, log2
from bot.src.reddit_bot import reddit_bot
from mongo_db.db import db
from utils.slack.styling import sl
from utils.slack.webhooks import slack_status, slack_error


class DialogueBot:
    def run(self, conv, user_model):
        username = conv.participant.name
        subreddit = str(conv.owner)

        bot_responses = db.bot_responses.get(subreddit)

        # this logic has moved to the trigger class. so we only get triggered if no human mod is involved.
        if reddit_bot.has_mod_been_involved(conv):
            # mod has been involved so ignore this conversation
            log2(subreddit, conv.id, "Human mod involved, IGNORED")
            slack_status(sl('D', subreddit, conv.id,
                            ':heavy_multiplication_x: Human involved → IGNORE'))
            db.users.update(conv, 'mod_involved', True)
        else:
            if not reddit_bot.have_we_replied(conv):
                log2(subreddit, conv.id, f"User `{username}`: We haven't replied")
                # we have not replied, so create a new contact and share form link
                log2(subreddit, conv.id, f"User `{username}`: Creating form entry")
                entry = add_form_entry(username, subreddit)
                if not entry:
                    log2(subreddit, conv.id, f"User `{username}`: Error creating form entry")
                    slack_error(sl('D', subreddit, conv.id,
                                   ':name_badge: Creating Form → ERROR'))
                    return
                slack_status(sl('D', subreddit, conv.id,
                                ':ballot_box_with_check: Form created'))
                # provide the first response, and share the form link
                log2(subreddit, conv.id, f"User `{username}`: Sharing form...")
                reddit_bot.reply_to_mod_mail_conversation(conv,
                                                          bot_responses['initial'],
                                                          form_shared=True)
                slack_status(sl('D', subreddit, conv.id,
                                ':ballot_box_with_check: Form shared'))
                reddit_bot.archive_conversation(conv)
                slack_status(sl('D', subreddit, conv.id,
                                ':white_check_mark: Archived'))
                # db.users.update(conv, 'form_shared', True)

            else:
                log2(subreddit, conv.id, "Bot already replied, OK")

                if user_model['note_shared']:
                    log2(subreddit, conv.id, "Note already shared with mods, IGNORE")
                    slack_status(sl('D', subreddit, conv.id,
                                    ':heavy_multiplication_x: Note already shared → IGNORE'))
                    return

                log2(subreddit, conv.id, f"User `{username}`: Check if form filled")
                form_response = get_form_response(username, subreddit)

                if form_response is None:
                    # some error in collecting responses from qualtrics
                    log(f'Passing on the error via mod note', conv_id=conv.id)
                    slack_error(sl('D', subreddit, conv.id,
                                   ':name_badge: Form not found → ERROR'))
                    self.create_mod_note(conv, "I'm having trouble accessing user form responses",
                                         error=True)
                    form_response = {}

                elif form_response.filled():
                    log2(subreddit, conv.id, f"User `{username}`: Form filled, OK")
                    slack_status(sl('D', subreddit, conv.id,
                                    ':ballot_box_with_check: Form was filled'))
                    # user has submitted the form
                    db.users.update(conv, 'form_filled', True)
                    reddit_bot.reply_to_mod_mail_conversation(conv, bot_responses['final'])
                    log2(subreddit, conv.id, "Sending note for mods...")
                    self.create_mod_note(conv, form_response)
                    slack_status(sl('D', subreddit, conv.id,
                                    ':ballot_box_with_check: Note shared'))
                    reddit_bot.unarchive_conversation(conv)
                    slack_status(sl('D', subreddit, conv.id,
                                    ':white_check_mark: Unarchived'))

                else:
                    slack_status(sl('D', subreddit, conv.id,
                                    ':radio_button: Form not filled yet'))
                    # user has not submitted any response yet
                    if reddit_bot.is_new_reply_from_user(conv):
                        log2(subreddit, conv.id, "Form not filled, Reminding user...")
                        reddit_bot.reply_to_mod_mail_conversation(conv, bot_responses['reminder'])
                        slack_status(sl('D', subreddit, conv.id,
                                        ':ballot_box_with_check: User reminded'))
                        reddit_bot.archive_conversation(conv)
                        slack_status(sl('D', subreddit, conv.id,
                                        ':white_check_mark: Archived'))
                    else:
                        log2(subreddit, conv.id, "No response from user yet, DONE")
                        slack_status(sl('D', subreddit, conv.id,
                                        ':ballot_box_with_check: Do nothing'))

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
