from bot.src.logger.logger import logger


def log(message, conv_id=None, subreddit=None):
    logger.info(message, extra={'conv_id': conv_id,
                                'subreddit': subreddit})
