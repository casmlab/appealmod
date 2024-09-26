import re
import traceback

from utils.slack.webhooks import slack_error, slack_status


def simplify_traceback(traceback_text):
    # todo: replace paths

    traceback_text = traceback_text.replace(
        'Traceback (most recent call last):',
        '_Traceback (most recent call last):_\n'
    )
    traceback_text = traceback_text.replace(
        'During handling of the above exception, another exception occurred:',
        '_During handling of the above exception, another exception occurred:_'
    )

    traceback_text = re.sub(
        r'File "([^"]+/)([^/"]+\.py)", line (\d+), in (\w+)\n'
        r' {4}(.*)\n',
        r'*File* "\1*\2*", line *\3*, in *`\4`*\n'
        r'    `\5`\n\n',
        traceback_text
    )

    traceback_text = f'\n{traceback_text.strip()}'.replace('\n', '\n> ')

    return traceback_text


def slack_exception(slug, e, message_suffix='', send_traceback=True):
    header = f'`{slug}`  *{type(e).__name__}*: {e}  {message_suffix}'
    traceback_text = simplify_traceback(traceback.format_exc().strip())

    message = f'{header}\n{traceback_text}' if send_traceback else header
    slack_error(message, 'warning')
    slack_status(header, 'warning')
