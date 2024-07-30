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
                              subreddit=subreddit.lower())

    def auth(self, reddit_username, subreddit):
        if reddit_username:
            reddit_username = reddit_username.lower()
        if subreddit:
            subreddit = subreddit.lower()
        return self.filter(reddit_username=reddit_username,
                           subreddit=subreddit).exists()


class BanAppealData(models.Model):
    reddit_username = models.CharField(max_length=254)
    subreddit = models.CharField(max_length=254)

    why_banned = models.TextField(
        verbose_name='Find and copy/paste here the note from mods on '
                     'why you were banned',
        null=True,
    )
    why_appealing = models.CharField(
        verbose_name='Why are you appealing your ban?',
        max_length=254,
        choices=[
            ('disagree', "I don't agree with the rule"),
            ('not-apply', "I don't think the rule applies to my behavior"),
            ('regret', "I regret my behavior"),
            ('other', "Other (please specify below)"),
        ],
        blank=False,
        default=None,
        null=True,
    )
    why_appealing_other = models.TextField(
        blank=True,
        null=True,
    )
    describe_rule = models.TextField(
        verbose_name='Can you describe the rule in your own words?',
        null=True,
    )
    describe_actions = models.TextField(
        verbose_name='Can you describe your actions that led to the ban '
                     'and the circumstances that made you act that way?',
        null=True,
    )
    wrong_actions = models.CharField(
        verbose_name='Do you think your actions were wrong?',
        max_length=10,
        choices=[
            ('no', "No"),
            ('yes', "Yes"),
        ],
        blank=False,
        default=None,
        null=True,
    )
    will_not_repeat = models.CharField(
        verbose_name='Are you willing to pledge that you will not repeat '
                     'such actions in the future?',
        max_length=10,
        choices=[
            ('no', "No"),
            ('yes', "Yes"),
        ],
        blank=False,
        default=None,
        null=True,
    )
    what_steps = models.TextField(
        verbose_name="What steps will you take to ensure "
                     "that you don't do this again?",
        null=True,
    )
    allowed_comments = models.TextField(
        verbose_name='Which of the following comment(s) do you think '
                     'should be allowed in our community?',
        choices=[
            ("c1", "Hahaha, not at all, I love a good discussion, "
                   "especially with a retard on the internet, but you're too dumb"),
            ("c2", "You’re still a fat fuck, k..ill yourself"),
            ("c3", "I’ll hire my hacker friend to doxx you then send a hitman "
                   "to give you ebola then shoot you in the head and revive you to give you AIDS"),
            ("c4", "Even if your mom is a fucking asshole, I believe you that she is, "
                   "drugging her will NOT do anyone any good"),
            ("c5", "Fuck him. You dont want or need those assholes in your life. "
                   "Make a new friend"),
        ],
        blank=False,
        default=None,
        null=True,
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BanAppealDataManager()

    class Meta:
        db_table = 'main_ban_appeal_data'

    def __str__(self):
        return self.reddit_username
