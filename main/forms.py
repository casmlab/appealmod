from django import forms

from main.models import SignUpData, BanAppealData


class SignUpForm(forms.ModelForm):
    class Meta:
        model = SignUpData
        fields = ['name', 'email', 'reddit_username', 'subreddit_url']


class BanAppealAuthForm(forms.Form):
    reddit_username = \
        forms.CharField(max_length=254,
                        widget=forms.TextInput(attrs={
                            'class': 'form-control',
                            'placeholder': 'Enter your Reddit username'
                        }))
    subreddit = \
        forms.CharField(max_length=254,
                        widget=forms.TextInput(attrs={
                            'class': 'form-control',
                            'placeholder': 'Enter Subreddit'
                        }))


class BanAppealMainForm(forms.ModelForm):
    class Meta:
        model = BanAppealData
        fields = [
            'why_banned', 'why_appealing',
            'describe_rule', 'describe_actions',
            'wrong_actions', 'will_not_repeat',
            'what_steps', 'allowed_comments',
        ]
