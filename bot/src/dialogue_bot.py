from bot.src.form import add_form_entry, get_form_response
from bot.src.logger.utils import log, md_code, log_conv
from bot.src.logger.L import L
from bot.src.reddit_bot import reddit_bot
from mongo_db.db import db
from utils.slack.styling import sl
from utils.slack.webhooks import slack_steps_conv, slack_error, slack_main_conv


class DialogueBot:
    def reply(self, conv, user):
        username = conv.participant.name
        L.conv_id = conv.id
        L.subreddit = str(conv.owner)

        bot_responses = db.bot_responses.get(L.subreddit)

        # this logic has moved to the trigger class. so we only get triggered if no human mod is involved.
        if reddit_bot.has_mod_been_involved(conv):
            # mod has been involved so ignore this conversation
            log_conv("Human mod involved, IGNORED")
            slack_steps_conv('✖️ Human involved → IGNORE')
            slack_main_conv('✖️ Human involved → IGNORE')
            db.users.update(conv, 'mod_involved', True)
            db.users.update(conv, 'ignored', True)
        else:
            if not reddit_bot.have_we_replied(conv):
                log_conv(f"User `{username}`: We haven't replied")
                # we have not replied, so create a new contact and share form link
                log_conv(f"User `{username}`: Creating form entry")
                entry = add_form_entry(username, L.subreddit)
                if not entry:
                    log_conv(f"User `{username}`: Error creating form entry")
                    slack_error(sl('D', L.subreddit, L.conv_id,
                                   '📛 Creating Form → ERROR'))
                    return
                slack_steps_conv(':ballot_box_with_check: Form created')
                # provide the first response, and share the form link
                log_conv(f"User `{username}`: Sharing form...")
                reddit_bot.reply_to_mod_mail_conversation(conv,
                                                          bot_responses['initial'],
                                                          form_shared=True)
                log_conv(f"Replied with message: {md_code(bot_responses['initial'])}")

                slack_steps_conv('☑️ Form shared')
                reddit_bot.archive_conversation(conv)
                log_conv("Conversation ARCHIVED")
                slack_steps_conv('✅ Archived')
                slack_main_conv('✅ Form shared, Archived')
                # db.users.update(conv, 'form_shared', True)

            else:
                log_conv("Bot already replied, OK")

                if user['note_shared']:
                    log_conv("Note already shared with mods, IGNORE")
                    slack_steps_conv('✖️ Note already shared → IGNORE')
                    slack_main_conv('✖️ Note already shared → IGNORE')
                    db.users.update(conv, 'ignored', True)
                    return

                log_conv(f"User `{username}`: Check if form filled")
                form_response = get_form_response(username, L.subreddit)

                if form_response is None:
                    # some error in collecting responses from qualtrics
                    log(f'Passing on the error via mod note', conv_id=L.conv_id)
                    slack_error(sl('D', L.subreddit, L.conv_id,
                                   '📛 Form not found → ERROR'))
                    self.create_mod_note(conv, "I'm having trouble accessing user form responses",
                                         error=True)

                elif form_response.filled():
                    log_conv(f"User `{username}`: Form filled, OK")
                    slack_steps_conv('☑️ Form was filled')
                    # user has submitted the form
                    db.users.update(conv, 'form_filled', True)
                    reddit_bot.reply_to_mod_mail_conversation(conv, bot_responses['final'])
                    log_conv(f"Replied with message: {md_code(bot_responses['final'])}")

                    log_conv("Sending note for mods...")
                    self.create_mod_note(conv, form_response)
                    slack_steps_conv('☑️ Note shared')
                    reddit_bot.unarchive_conversation(conv)
                    log_conv("Conversation UNARCHIVED")
                    slack_steps_conv('✅ Unarchived')
                    slack_main_conv('✅ Form filled, Note shared, Unarchived')

                else:
                    slack_steps_conv('🔘 Form not filled yet')
                    # user has not submitted any response yet
                    if reddit_bot.is_new_reply_from_user(conv):
                        log_conv("Form not filled, Reminding user...")
                        reddit_bot.reply_to_mod_mail_conversation(conv, bot_responses['reminder'])
                        log_conv(f"Replied with message: {md_code(bot_responses['reminder'])}")

                        slack_steps_conv('☑️ User reminded')
                        reddit_bot.archive_conversation(conv)
                        log_conv("Conversation ARCHIVED")
                        slack_steps_conv('✅ Archived')
                        slack_main_conv('✅ Form not filled, User reminded, Archived')
                    else:
                        log_conv("No response from user yet, DONE")
                        slack_steps_conv('☑️ Do nothing')

    def clean_user_text(self, user_response):
        pass

    def create_mod_note(self, conv, form_response, error=False,
                        print_flag=False):
        # to pass on any kind of expected error to the mods, so they can report it to us.
        if error:
            reddit_bot.reply_to_mod_mail_conversation(conv, form_response,
                                                      mod_note=True)
            log_conv(f"Replied with message: {md_code(form_response)}")
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
                log_conv(f"Replied with message: {md_code(response_text)}")
            else:
                with open('examples/mod-notes.txt', 'a') as outputfile:
                    output = conv.id + '\n' + response_text + '\n'
                    outputfile.write(output)


dialogue_bot = DialogueBot()
