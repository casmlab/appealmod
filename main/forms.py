from django import forms

from main.models import SignUpData


class SignUpForm(forms.ModelForm):
    class Meta:
        model = SignUpData
        fields = ['name', 'email', 'reddit_username', 'subreddit_url']
