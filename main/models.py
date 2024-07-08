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
