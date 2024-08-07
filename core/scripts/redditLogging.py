import sys

import pymongo
import logging
from logging import StreamHandler
from datetime import datetime
import json
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

        msg = self.format(record)
        # write the log message to the mongo database
        application_logs_collection.insert_one({
            "message": msg,
            "timestamp": datetime.now(),
            'conversationID': conversation_id
        })


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


class SafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        return str(obj)


def sanitize_object_for_mongo(obj):
    return json.loads(json.dumps(vars(obj), cls=SafeJSONEncoder))


def has_conversation_been_logged(praw_conversation):
    return conversation_logs_collection.find_one({"id": praw_conversation.id})


def log_conversation(praw_conversation, bot):
    conversation_data = sanitize_object_for_mongo(praw_conversation)
    message_data = [sanitize_object_for_mongo(m) for m in praw_conversation.messages]
    conv_id = praw_conversation.id
    to_log = {
        "id": conv_id,
        "conversationData": conversation_data,
        "messageData": message_data,
    }
    user = praw_conversation.user.name
    ban_info = None
    try:
        ban_info = bot.get_user_ban_information(user)
    except:
        pass
    if ban_info:
        del ban_info['_reddit']
        to_log["banInfo"] = ban_info
    to_log["isBanned"] = "banInfo" in to_log
    existing_conversation = has_conversation_been_logged(praw_conversation)
    if existing_conversation is None:
        to_log["unbannedTime"] = None
        conversation_logs_collection.insert_one(to_log)
        log2(conv_id, "Conversation LOGGED (added to DB)")
    else:
        if existing_conversation.get("isBanned") and not to_log.get("isBanned"):
            to_log["unbannedTime"] = datetime.now(EST)
        else:
            to_log["unbannedTime"] = existing_conversation.get("unbannedTime")
        conversation_logs_collection.update_one({"id": conv_id},
                                                {"$set": to_log})
        log2(conv_id, "Conversation LOGGED (updated in DB)")


def update_conv_ids(modmail_conversation, user_model):
    # get all conv user has initiated so far -- the main conv id + any other conv ids present
    # check if the current conv is part of it.
    # if not, then update the user data with a new conv id list which is current list + current conv
    if 'other_conv_ids' in user_model.keys():
        other_conv_ids = user_model['other_conv_ids']
    else:
        other_conv_ids = []

    if modmail_conversation.id == user_model['conv_id'] or modmail_conversation.id in other_conv_ids:  # this is an old conv
        return
    else:
        other_conv_ids.append(modmail_conversation.id)
        username = user_model['username']
        log(f'This is a new conversation by the same user {username}, updating the model with the new conv id',
            conversation_id=modmail_conversation.id)
        update_user_data(modmail_conversation, 'other_conv_ids', other_conv_ids)


def update_user_data(modmail_conversation, key, value, username=None):

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
        username = modmail_conversation.participant.name
    conv_id = modmail_conversation.id
    log2(conv_id, "User `{username}`: Updating data {update_dict}")
    subreddit = str(modmail_conversation.owner)
    user_logs_collection.update_one({'username': username, 'subreddit': subreddit}, {'$set': update_dict})


def log_user_data(modmail_conversation, group):  # todo: rename: add_user...
    subreddit = str(modmail_conversation.owner)

    username = modmail_conversation.participant.name
    sorted_msgs = sorted(modmail_conversation.messages, key=lambda x: x.date)

    appeal_time = sorted_msgs[0].date  ## default time, if no appeal time is found.
    for message in sorted_msgs:
        if message.author.name == username:
            appeal_time = message.date  ## setting the appeal time
            break

    conv_id = modmail_conversation.id
    # if getUserGroup(username) is None: # to ensure that we don't create duplicate entries...
    mydict = {
        'username': username,
        'conv_id': conv_id,
        'subreddit': subreddit,
        'group': group,
        'appeal_time': appeal_time,
        'form_filled': False,
        'form_shared': False,
        'note_shared': False,
        'mod_involved': False,
        'user_deleted': False,
    }
    user_logs_collection.insert_one(mydict)
    log2(conv_id, f'User `{username}`: Added to DB')
    return mydict


def check_user_model(username, subreddit):
    mydict = user_logs_collection.find_one({"username": username, "subreddit": subreddit})
    if mydict:  # user exists already
        log(f'  - User `{username}`: Found in DB')  # todo: move this to `get_user_model` to log with `conv_id`
        return mydict
    else:
        return None


def log(message, conversation_id=None):
    logger.info(message, extra={'conversationID': conversation_id})


def log_str(text):
    return f'\n```\n{text}\n```'


def log2(conv_id, message):
    log(f'  - `{conv_id}`: {message}', conv_id)
