from datetime import datetime

import pytz

from core.scripts.db.utils.sanitizer import sanitize
from core.scripts.logger import log2

EST = pytz.timezone('US/Eastern')


class DbConversations:
    def __init__(self, collection):
        self.collection = collection

    def find(self, conv):
        """
        Has conversation been logged?
        """
        return self.collection.find_one({"id": conv.id})

    def add(self, conv, bot):
        conv_data = sanitize(conv)
        message_data = [sanitize(m) for m in conv.messages]
        subreddit = str(conv.owner)

        data = {
            "id": conv.id,
            "conversationData": conv_data,
            "messageData": message_data,
        }

        user = conv.user.name
        ban_info = None
        try:
            ban_info = bot.get_user_ban_information(user)
        except:
            pass
        if ban_info:
            del ban_info['_reddit']
            data["banInfo"] = ban_info
        data["isBanned"] = "banInfo" in data

        old_entry = self.find(conv)
        if old_entry is not None:  # Need to update instead of adding new entry
            if old_entry.get("isBanned") and not data.get("isBanned"):
                data["unbannedTime"] = datetime.now(EST)
            else:
                data["unbannedTime"] = old_entry.get("unbannedTime")
            self.collection.update_one({"id": conv.id}, {"$set": data})
            log2(subreddit, conv.id, "Conversation LOGGED (updated in DB)")
            return

        # Adding new entry:
        data["unbannedTime"] = None
        self.collection.insert_one(data)
        log2(subreddit, conv.id, "Conversation LOGGED (added to DB)")
