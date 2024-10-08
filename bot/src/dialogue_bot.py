from bot.src.form import add_form_entry, get_form_response
from bot.src.logger.L import L
from bot.src.reddit_bot import reddit_bot
from mongo_db.db import db


class DialogueBot:
    def reply(self, conv, user):
        username = conv.participant.name
        L.conv_id = conv.id
        L.subreddit = str(conv.owner)

        bot_responses = db.bot_responses.get(L.subreddit)

        # this logic has moved to the trigger class. so we only get triggered if no human mod is involved.
        if reddit_bot.has_mod_been_involved(conv):
            # mod has been involved so ignore this conversation
            L.step('✖️ Human involved → IGNORE')
            db.users.update(conv, 'mod_involved', True)
            db.users.update(conv, 'ignored', True)

        else:
            if not reddit_bot.have_we_replied(conv):
                L.logging(f"User `{username}`: We haven't replied")
                L.logging(f"User `{username}`: Creating form entry")
                entry = add_form_entry(username, L.subreddit)
                if not entry:
                    L.error(f'📛 Creating Form (user `{username}`) → ERROR')
                    return
                L.step('☑️ Form created')

                # provide the first response, and share the form link
                L.logging(f"User `{username}`: Sharing form...")
                reddit_bot.reply_to_mod_mail_conversation(
                    conv, bot_responses['initial'], form_shared=True)
                L.step('☑️ Form shared')

                reddit_bot.archive_conversation(conv)
                L.step('✅ Archived')
                L.main('✅ Form shared, Archived')
                # db.users.update(conv, 'form_shared', True)

            else:
                L.logging("Bot already replied, OK")

                if user['note_shared']:
                    L.step('✖️ Note already shared → IGNORE')
                    db.users.update(conv, 'ignored', True)
                    return

                L.logging(f"User `{username}`: Check if form filled")
                form_response = get_form_response(username, L.subreddit)

                if form_response is None:
                    L.error(f'📛 Form not found (user `{username}`) → ERROR')
                    self.create_mod_note(
                        conv, "I'm having trouble accessing user form responses",
                        error=True)

                elif form_response.filled():
                    L.step('☑️ Form was filled')  # user has submitted the form
                    db.users.update(conv, 'form_filled', True)

                    reddit_bot.reply_to_mod_mail_conversation(conv, bot_responses['final'])

                    L.logging("Sending note for mods...")
                    self.create_mod_note(conv, form_response)
                    L.step('☑️ Note shared')

                    reddit_bot.unarchive_conversation(conv)
                    L.step('✅ Unarchived')
                    L.main('✅ Form filled, Note shared, Unarchived')

                else:
                    L.step('🔘 Form not filled yet')  # user has not submitted any response yet

                    if reddit_bot.is_new_reply_from_user(conv):
                        L.logging("New reply from user, Reminding them...")
                        reddit_bot.reply_to_mod_mail_conversation(conv, bot_responses['reminder'])
                        L.step('☑️ User reminded')

                        reddit_bot.archive_conversation(conv)
                        L.step('✅ Archived')
                        L.main('✅ Form not filled, User reminded, Archived')

                    else:
                        L.step('☑️ Do nothing')  # No response from user yet

    def clean_user_text(self, user_response):
        pass

    def create_mod_note(self, conv, form_response, error=False,
                        print_flag=False):
        # to pass on any kind of expected error to the mods, so they can report it to us.
        if error:
            # todo: send "form_response.prettified" or ".json" instead?
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
