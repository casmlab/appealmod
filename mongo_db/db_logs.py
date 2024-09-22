from datetime import datetime


class DbLogs:
    def __init__(self, collection):
        self.collection = collection

    def add(self, message, subreddit, conv_id):
        self.collection.insert_one({
            "message": message,
            "timestamp": datetime.now(),
            'conv_id': conv_id,
            'subreddit': subreddit,
        })
