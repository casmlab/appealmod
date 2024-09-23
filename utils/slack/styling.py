

def sl(job, subreddit, conv_id, text):
    job_icon = {
        'R': ':arrow_forward:',
        'S': ':arrows_counterclockwise:',
        'D': ':speech_balloon:',
    }[job]

    subreddit_link = f'https://reddit.com/r/{subreddit}'
    conv_link = f'https://mod.reddit.com/mail/all/{conv_id}'

    return f'{job_icon} [<{subreddit_link}|{subreddit}> :: ' \
           f'<{conv_link}|{conv_id}>]: {text}'
