from datetime import datetime

import pytz

from bot.scripts.logger import log2
from mongo_db.utils.sanitizer import sanitize

EST = pytz.timezone('US/Eastern')


class DbConversations:
    def __init__(self, collection):
        self.collection = collection

    def find(self, conv_id):
        """
        Has conversation been logged?
        """
        return self.collection.find_one({"id": conv_id})

    def add(self, conv, bot):
        conv_data = sanitize(conv)
        message_data = [sanitize(m) for m in conv.messages]
        subreddit = str(conv.owner)

        data = {
            "id": conv.id,
            "conversation_data": conv_data,
            "message_data": message_data,
        }

        user = conv.user.name
        ban_info = None
        try:
            ban_info = bot.get_user_ban_information(user)
        except:
            pass
        if ban_info:
            del ban_info['_reddit']
            data["ban_info"] = ban_info
        data["is_banned"] = "ban_info" in data

        old_entry = self.find(conv.id)
        if old_entry is not None:  # Need to update instead of adding new entry
            if old_entry.get("is_banned") and not data.get("is_banned"):
                data["unbanned_time"] = datetime.now(EST)
            else:
                data["unbanned_time"] = old_entry.get("unbanned_time")
            self.collection.update_one({"id": conv.id}, {"$set": data})
            log2(subreddit, conv.id, "Conversation LOGGED (updated in DB)")
            return

        # Adding new entry:
        data["unbanned_time"] = None
        self.collection.insert_one(data)
        log2(subreddit, conv.id, "Conversation LOGGED (added to DB)")
