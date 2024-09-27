import logging
import sys
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


class L:  # current logging "headers"
    subreddit = '?'
    conv_id = '?'


def log(message, conv_id=None, subreddit=None):
    logger.info(message, extra={'conv_id': conv_id,
                                'subreddit': subreddit})


def md_code(text):  # Markdown code block
    return f'\n```\n{text}\n```'

# todo: in `log_conv`: which job: [R]ecent_convs, [S]tarted_convs, [C]ommon_code

def log_conv(message):  # Logging conversation related info
    log(f'  - `{L.subreddit}/{L.conv_id}`: {message}',
        L.conv_id, L.subreddit)
