import json
import time

import requests
from requests.exceptions import SSLError

from conf import conf


def slack_hook(chat, message):
    if conf.slack_disabled:
        return

    hooks = {
        'main': conf.slack_hook_main,
        'steps': conf.slack_hook_steps,
        'alerts': conf.slack_hook_alerts,
        'errors': conf.slack_hook_errors,
        'logging': conf.slack_hook_logging,
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
        slack_alert(f'⚠️ `slack`  *Error* (1): {e}')
        time.sleep(1)
        try:
            requests.post(url, data=payload, headers=headers)
        except (SSLError, requests.ConnectionError) as e:
            time.sleep(1)
            slack_error(f'⛔ `slack`  *Error* (2): {e}')
            time.sleep(1)
            raise


def slack_main(message, skip_logging=False):
    slack_hook('main', message)

    if not skip_logging:
        slack_hook('logging', message)


def slack_step(message, skip_logging=False):
    slack_hook('steps', message)

    if not skip_logging:
        slack_hook('logging', message)


def slack_alert(message, skip_other=False):
    slack_hook('alerts', message)
    slack_hook('logging', message)

    if not skip_other:
        slack_step(message, skip_logging=True)
        slack_main(message, skip_logging=True)


def slack_error(message, skip_other=True):
    slack_hook('errors', message)
    slack_hook('logging', message)

    if not skip_other:
        slack_step(message, skip_logging=True)
        slack_main(message, skip_logging=True)


def slack_logging(message):
    slack_hook('logging', message)


if __name__ == '__main__':
    slack_step(""":no_entry_sign: I've *disabled* this channel for now because I've received such an error while sending a private message in Slack:
> *Message not sent*
> Your team isn't able to send messages right now. Review any apps or webhooks that may be sending a high-volume of messages. Learn more about message limits.""")
