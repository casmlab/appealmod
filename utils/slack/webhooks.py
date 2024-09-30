import json
import time

import requests
from requests.exceptions import SSLError

from bot.src.logger.L import L
from conf import conf
from utils.slack.styling import sl


def slack_hook(chat, message):
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
        slack_alert(f':warning: `slack`  *Error* (1): {e}')
        time.sleep(1)
        try:
            requests.post(url, data=payload, headers=headers)
        except (SSLError, requests.ConnectionError) as e:
            time.sleep(1)
            slack_error(f':no_entry: `slack`  *Error* (2): {e}')
            time.sleep(1)
            raise


def slack_logging(message):
    slack_hook('logging', message)


def slack_steps(message):
    slack_hook('logging', message)
    slack_hook('steps', message)


def slack_steps_conv(message):
    slack_steps(sl(L.runner, L.subreddit, L.conv_id, message))


def slack_main(message):
    slack_hook('logging', message)
    slack_hook('main', message)


def slack_alert(message, send_status=True):
    slack_hook('logging', message)
    slack_hook('alerts', message)
    if send_status:
        slack_steps(message)
        slack_main(message)


def slack_error(message, send_status=True):
    slack_hook('logging', message)
    slack_hook('errors', message)
    if send_status:
        slack_steps(message)
        slack_main(message)
