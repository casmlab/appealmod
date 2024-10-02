import traceback

from bot.conf import conf
from bot.src.logger.logger import logger
from utils.slack.exceptions import simplify_traceback
from utils.slack.styling import make_conv_prefix, subreddits, clink
from utils.slack.webhooks import slack_main, slack_step, slack_alert, \
    slack_error, slack_logging


class L:  # current logging "headers"
    runner = '?'  # either [R]ecent or [S]tarted: ('R' or 'S')
    subreddit = '?'
    conv_id = '?'

    @classmethod
    def job_icon(cls):
        return {'R': '▶️', 'S': '👤'}[cls.runner]

    @classmethod
    def _log(cls, slack_channel, message, conv_prefix=True, skip_logger=False,
             skip_logging=False):
        if not skip_logger:
            cls.logger(message, conv_prefix)

        if conv_prefix:
            prefix = make_conv_prefix(cls.runner, cls.subreddit, cls.conv_id)
            message = f'{cls.job_icon()} {prefix} {message}'

        match slack_channel:
            case 'main':
                slack_main(message, skip_logging)
            case 'step':
                slack_step(message, skip_logging)
            case 'alert':
                slack_alert(message, skip_logging)
            case 'error':
                slack_error(message, skip_logging)
            case 'logging':
                slack_logging(message)
            case _:
                raise ValueError(f'Invalid Slack channel: "{slack_channel}"')

    @classmethod
    def logger(cls, message, conv_prefix=True):
        extra = {}

        if conv_prefix:
            message = f'{cls.job_icon()} `{L.subreddit}/{L.conv_id}`: {message}'
            extra = {'conv_id': cls.conv_id,
                     'subreddit': cls.subreddit}

        logger.info(message, extra=extra)

    @classmethod
    def main(cls, message, conv_prefix=True, skip_logger=False):
        cls._log('main', message, conv_prefix, skip_logger)

    @classmethod
    def step(cls, message, conv_prefix=True, skip_logger=False, main=False):
        cls._log('step', message, conv_prefix, skip_logger)

        if main:
            cls._log('main', message, conv_prefix,
                     skip_logger=True, skip_logging=True)

    @classmethod
    def alert(cls, message, conv_prefix=True, skip_logger=False):
        cls._log('alert', message, conv_prefix, skip_logger)

    @classmethod
    def error(cls, message, conv_prefix=True, skip_logger=False):
        cls._log('error', message, conv_prefix, skip_logger)

    @classmethod
    def logging(cls, message, conv_prefix=True, skip_logger=False):
        cls._log('logging', message, conv_prefix, skip_logger)

    @classmethod
    def exception(cls, e, message_suffix='', only_alert=True):
        header = f'⚠️ {cls.job_icon()}  *{type(e).__name__}*: {e}  {message_suffix}'

        traceback_text = simplify_traceback(traceback.format_exc().strip())
        full_message = f'{header}\n{traceback_text}'
        if only_alert:
            slack_alert(full_message, skip_other=True)
        else:
            slack_error(full_message, skip_other=True)

        slack_step(header, skip_logging=True)
        slack_main(header, skip_logging=True)

    @classmethod
    def run(cls):
        job_name = {
            'R':  '*[R]ecently* created',
            'S': 'already *[S]tarted*'
        }[cls.runner]
        msg = f'❇️ Run processing {cls.job_icon()} {job_name} conversations for '

        logger_subreddits = \
            ", ".join(subreddit for subreddit in conf.subreddits_ids)
        cls.logger(f'{msg} [{logger_subreddits}]', conv_prefix=False)

        slack_subreddits = subreddits()
        cls.step(f'{msg} [{slack_subreddits}]', conv_prefix=False, skip_logger=True)
        cls.main(f'{msg} [{slack_subreddits}]', conv_prefix=False, skip_logger=True)

    @classmethod
    def conv(cls):
        cls.logger(f'✴️ Start processing {L.conv_id}: {"*" * 20}')
        cls.step(f'✴️ *Start processing {clink(L.conv_id)}:*', skip_logger=True)
