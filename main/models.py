from django.db import models


class SignUpData(models.Model):
    name = models.CharField(max_length=254)
    email = models.EmailField()
    reddit_username = models.CharField(max_length=254)
    subreddit_url = models.CharField(max_length=254)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'main_sign_up_data'

    def __str__(self):
        return self.email


class BanAppealData(models.Model):
    reddit_username = models.CharField(max_length=254)
    subreddit = models.CharField(max_length=254)

    why_banned = models.TextField()
    why_appealing = models.TextField()
    describe_rule = models.TextField()
    describe_actions = models.TextField()
    wrong_actions = models.BooleanField()
    will_not_repeat = models.BooleanField()
    what_steps = models.TextField()
    allowed_comments = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'main_ban_appeal_data'

    def __str__(self):
        return self.reddit_username
