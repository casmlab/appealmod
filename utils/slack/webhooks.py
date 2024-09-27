import json
import time

import requests
from requests.exceptions import SSLError

from conf import conf


def slack_hook(chat, message, emoji=None):
    if conf.slack_disabled:
        return

    hooks = {
        'logging': conf.slack_hook_logging,
        'status': conf.slack_hook_status,
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


def slack_status(message, emoji=None):
    slack_hook('logging', message, emoji)
    slack_hook('status', message, emoji)


def slack_alert(message, emoji=None):
    slack_hook('logging', message, emoji)
    slack_hook('alerts', message, emoji)


def slack_error(message, emoji=None):
    slack_hook('logging', message, emoji)
    slack_hook('errors', message, emoji)
