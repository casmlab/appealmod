import json
import logging
import sys
from datetime import datetime
from logging import StreamHandler

import pymongo
import pytz

from core.config import Config as config
from core.scripts.db.db import db
from core.scripts.db.utils.sanitizer import sanitize

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


def update_conv_ids(conv, user):
    """
    Get all conv user has initiated so far -- the main conv id + any other conv ids present
    check if the current conv is part of it.
    if not, then update the user data with a new conv id list which is current list + current conv
    """
    other_conv_ids = user.get('other_conv_ids', [])

    if conv.id == user['conv_id'] or conv.id in other_conv_ids:  # this is an old conv
        return

    other_conv_ids.append(conv.id)
    username = user['username']
    subreddit = str(conv.owner)
    log2(subreddit, conv.id, f'New conv by same user `{username}`, updating model')
    update_user_data(conv, 'other_conv_ids', other_conv_ids)


def update_user_data(conv, key, value, username=None):

    if type(key) is list and type(value) is list:
        pass
    else:
        key = [key]
        value = [value]

    if len(key) == len(value):
        update_dict = dict(zip(key, value))
    else:
        log(f'Key and value list size mismatch while updating the user data')
        log(f'Key is {key} and value is {value}')
        update_dict = {}

    if username is None:
        username = conv.participant.name
    conv_id = conv.id
    subreddit = str(conv.owner)
    log2(subreddit, conv_id, f"User `{username}`: Updating data {update_dict}")
    user_logs_collection.update_one({'username': username, 'subreddit': subreddit}, {'$set': update_dict})


def log_user_data(conv, group):
    username = conv.participant.name
    subreddit = str(conv.owner)

    # Get `appeal_time` value:
    sorted_msgs = sorted(conv.messages, key=lambda x: x.date)
    appeal_time = sorted_msgs[0].date  # default, if no `appeal_time` found
    for message in sorted_msgs:
        if message.author.name == username:
            appeal_time = message.date  # set `appeal_time`
            break

    user = {
        'username': username,
        'conv_id': conv.id,
        'subreddit': subreddit,
        'group': group,
        'appeal_time': appeal_time,
        'form_filled': False,
        'form_shared': False,
        'note_shared': False,
        'mod_involved': False,
        'user_deleted': False,
    }
    user_logs_collection.insert_one(user)
    log2(subreddit, conv.id, f'User `{username}`: Added to DB')
    return user


def log(message, conv_id=None, subreddit=None):
    logger.info(message, extra={'conversationID': conv_id,
                                'subreddit': subreddit})


def log_str(text):
    return f'\n```\n{text}\n```'


def log2(subreddit, conv_id, message):
    log(f'  - `{subreddit}/{conv_id}`: {message}', conv_id, subreddit)
