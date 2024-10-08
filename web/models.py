from django.db import models


class SignUpData(models.Model):
    name = models.CharField(max_length=254)
    email = models.EmailField()
    reddit_username = models.CharField(max_length=254)
    subreddit_url = models.URLField(max_length=254)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'main_sign_up_data'

    def __str__(self):
        return self.email


class BanAppealDataManager(models.Manager):
    def create(self, reddit_username, subreddit):
        if self.auth(reddit_username, subreddit):
            return None
        return super().create(reddit_username=reddit_username.lower(),
                              subreddit=subreddit.lower(),
                              why_banned=None,
                              why_appealing=None,
                              why_appealing_other=None,
                              describe_rule=None,
                              describe_actions=None,
                              wrong_actions=None,
                              will_not_repeat=None,
                              what_steps=None,
                              allowed_comments=None)

    def auth(self, reddit_username, subreddit):
        if reddit_username:
            reddit_username = reddit_username.lower()
        if subreddit:
            subreddit = subreddit.lower()
        try:
            return self.get(reddit_username=reddit_username,
                            subreddit=subreddit)
        except self.model.DoesNotExist:
            return None


class BanAppealData(models.Model):
    reddit_username = models.CharField(max_length=254)
    subreddit = models.CharField(max_length=254)

    why_banned = models.TextField(
        verbose_name='Find and copy/paste here the note from mods on '
                     'why you were banned',
        blank=True,
        null=True,
    )
    why_appealing = models.CharField(
        verbose_name='Why are you appealing your ban?',
        max_length=254,
        blank=True,
        null=True,
    )
    why_appealing_other = models.TextField(
        blank=True,
        null=True,
    )
    describe_rule = models.TextField(
        verbose_name='Can you describe the rule in your own words?',
        blank=True,
        null=True,
    )
    describe_actions = models.TextField(
        verbose_name='Can you describe your actions that led to the ban '
                     'and the circumstances that made you act that way?',
        blank=True,
        null=True,
    )
    wrong_actions = models.CharField(
        verbose_name='Do you think your actions were wrong?',
        max_length=10,
        blank=True,
        null=True,
    )
    will_not_repeat = models.CharField(
        verbose_name='Are you willing to pledge that you will not repeat '
                     'such actions in the future?',
        max_length=10,
        blank=True,
        null=True,
    )
    what_steps = models.TextField(
        verbose_name="What steps will you take to ensure "
                     "that you don't do this again?",
        blank=True,
        null=True,
    )
    allowed_comments = models.TextField(
        verbose_name='Which of the following comment(s) do you think '
                     'should be allowed in our community?',
        blank=True,
        null=True,
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BanAppealDataManager()

    class Meta:
        db_table = 'main_ban_appeal_data'

    def __str__(self):
        return self.reddit_username

    def filled(self):
        return any({
            self.why_banned, self.why_appealing, self.describe_rule,
            self.describe_actions, self.wrong_actions, self.will_not_repeat,
            self.what_steps, self.allowed_comments,
        })

    def to_json(self):
        return {
            'username': self.reddit_username,
            'subreddit': self.subreddit,
            'why_banned': self.why_banned,
            'why_appealing': self.why_appealing,
            'why_appealing_other': self.why_appealing_other,
            'describe_rule': self.describe_rule,
            'describe_actions': self.describe_actions,
            'wrong_actions': self.wrong_actions,
            'will_not_repeat': self.will_not_repeat,
            'what_steps': self.what_steps,
            'allowed_comments': self.allowed_comments,
        }

    @classmethod
    def get_label(cls, name):
        return cls._meta.get_field(name).verbose_name
