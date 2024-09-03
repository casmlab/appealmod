from datetime import datetime


class DbLogs:
    def __init__(self, collection):
        self.collection = collection

    def log(self, message, subreddit, conv_id):
        self.collection.insert_one({
            "message": message,
            "timestamp": datetime.now(),
            'conversationID': conv_id,
            'subreddit': subreddit,
        })
