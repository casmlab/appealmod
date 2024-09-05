import logging
import sys
from logging import StreamHandler

import pymongo
import pytz

from core.config import Config as config

EST = pytz.timezone('US/Eastern')

# mongoConnectionString = r"mongodb+srv://admin:u8U9VKugQO6EFmrG@cluster0.hxwup.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
mongo_driver = pymongo.MongoClient(config.DB_CONNECTION_STRING)
mongo_database = mongo_driver["main-cluster"]
conversation_logs_collection = mongo_database["conversation-logs"]
application_logs_collection = mongo_database["application-logs"]
user_logs_collection = mongo_database['user-logs']


class MongoDBLogger(StreamHandler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        try:
            conversation_id = record.conversationID
        except Exception as e:
            conversation_id = None

        try:
            subreddit = record.subreddit
        except Exception as e:
            subreddit = None

        from core.scripts.db.db import db

        message = self.format(record)
        db.logs.add(message, subreddit, conversation_id)


def get_logger():
    logger_name = 'main_logger'
    if logger_name in logging.Logger.manager.loggerDict:
        return logging.getLogger(logger_name)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s,%(msecs)03d %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d:%H:%M:%S'
    )

    file_handler = logging.FileHandler("redditLogging.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    mongo_logger = MongoDBLogger()
    mongo_logger.setFormatter(formatter)
    mongo_logger.setLevel(logging.INFO)
    logger.addHandler(mongo_logger)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    return logger


logger = get_logger()


def log(message, conv_id=None, subreddit=None):
    logger.info(message, extra={'conversationID': conv_id,
                                'subreddit': subreddit})


def log_str(text):
    return f'\n```\n{text}\n```'


def log2(subreddit, conv_id, message):
    log(f'  - `{subreddit}/{conv_id}`: {message}', conv_id, subreddit)
