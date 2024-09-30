from bot.src.logger.L import L
from bot.src.logger.logger import logger


def log(message, conv_id=None, subreddit=None):
    logger.info(message, extra={'conv_id': conv_id,
                                'subreddit': subreddit})


def md_code(text):  # Markdown code block
    return f'\n```\n{text}\n```'


def log_conv(message):  # Logging conversation related info
    log(f'  - `{L.subreddit}/{L.conv_id}`: {message}',
        L.conv_id, L.subreddit)


# todo: func for log_conv(f"Replied with message: {md_code(reply)}")
# todo: in `log_conv`: which job: [R]ecent_convs, [S]tarted_convs, [C]ommon_code
