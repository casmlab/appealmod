from logging import StreamHandler


class MongoDBLogger(StreamHandler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        try:
            conversation_id = record.conv_id
        except Exception as e:
            conversation_id = None

        try:
            subreddit = record.subreddit
        except Exception as e:
            subreddit = None

        from mongo_db.db import db

        message = self.format(record)
        db.logs.add(message, subreddit, conversation_id)
