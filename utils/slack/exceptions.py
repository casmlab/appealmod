import re


def simplify_traceback(traceback_text):
    traceback_text = traceback_text.replace(
        '  File "/usr/local/lib/python3.10/site-packages',
        '  File "/🧩/<site-packages>/'
    )

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
