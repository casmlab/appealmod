from bot.conf import conf


def rlink(subreddit):
    subreddit_link = f'https://reddit.com/r/{subreddit}'
    return f'<{subreddit_link}|{subreddit}>'


def clink(conv_id):
    conv_link = f'https://mod.reddit.com/mail/all/{conv_id}'
    return f'<{conv_link}|{conv_id}>'


def sl(job, subreddit, conv_id, text):
    job_icon = {
        'R': ':arrow_forward:',
        'S': ':bust_in_silhouette:',
    }[job]

    return f'{job_icon} [{rlink(subreddit)} :: {clink(conv_id)}]: {text}'


def subreddits():
    return ", ".join(rlink(subreddit) for subreddit in conf.subreddits_ids)
