import json
import time

import requests
from requests.exceptions import SSLError

from bot.src.logger.L import L
from conf import conf
from utils.slack.styling import sl


def slack_hook(chat, message, emoji=None):
    if conf.slack_disabled:
        return

    hooks = {
        'logging': conf.slack_hook_logging,
        'main': conf.slack_hook_main,
        'steps': conf.slack_hook_steps,
        'alerts': conf.slack_hook_alerts,
        'errors': conf.slack_hook_errors,
    }
    url = hooks[chat]
    if not url:
        return

    if emoji:
        message = f':{emoji}: {message}'

    payload = json.dumps({
        "text": message,
        'unfurl_links': False,
        'unfurl_media': False,
    })
    headers = {'content-type': 'application/json'}

    try:
        requests.post(url, data=payload, headers=headers)

    except (SSLError, requests.ConnectionError) as e:
        time.sleep(1)
        slack_alert(f'`slack`  *Error* (1): {e}', 'warning')
        time.sleep(1)
        try:
            requests.post(url, data=payload, headers=headers)
        except (SSLError, requests.ConnectionError) as e:
            time.sleep(1)
            slack_error(f'`slack`  *Error* (2): {e}', 'no_entry')
            time.sleep(1)
            raise


def slack_logging(message, emoji=None):
    slack_hook('logging', message, emoji)


def slack_steps(message, emoji=None):
    slack_hook('logging', message, emoji)
    slack_hook('steps', message, emoji)


def slack_steps_conv(message):
    slack_steps(sl(L.runner, L.subreddit, L.conv_id, message))


def slack_main(message, emoji=None):
    slack_hook('logging', message, emoji)
    slack_hook('main', message, emoji)


def slack_alert(message, emoji=None, send_status=True):
    slack_hook('logging', message, emoji)
    slack_hook('alerts', message, emoji)
    if send_status:
        slack_steps(message, emoji)
        slack_main(message, emoji)


def slack_error(message, emoji=None, send_status=True):
    slack_hook('logging', message, emoji)
    slack_hook('errors', message, emoji)
    if send_status:
        slack_steps(message, emoji)
        slack_main(message, emoji)
