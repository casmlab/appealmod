from django import forms

from main.models import SignUpData, BanAppealData


class SignUpForm(forms.ModelForm):
    class Meta:
        model = SignUpData
        fields = ['name', 'email', 'reddit_username', 'subreddit_url']
        widgets = {
            'name': forms.TextInput({
                'class': 'w3-input',
                'placeholder': 'Name',
            }),
            'email': forms.EmailInput({
                'class': 'w3-input',
                'placeholder': 'Email',
            }),
            'reddit_username': forms.TextInput({
                'class': 'w3-input',
                'placeholder': 'Reddit Username',
            }),
            'subreddit_url': forms.URLInput({
                'class': 'w3-input',
                'placeholder': 'Subreddit URL',
            })
        }


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

    def clean(self):
        reddit_username = self.cleaned_data['reddit_username']
        subreddit = self.cleaned_data['subreddit']
        if not BanAppealData.objects.auth(reddit_username, subreddit):
            raise forms.ValidationError('Invalid Reddit username or Subreddit')
        return self.cleaned_data


class BanAppealMainForm(forms.ModelForm):
    class Meta:
        model = BanAppealData
        fields = [
            'why_banned', 'why_appealing', 'why_appealing_other',
            'describe_rule', 'describe_actions',
            'wrong_actions', 'will_not_repeat',
            'what_steps', 'allowed_comments',
        ]
        widgets = {
            'why_banned': forms.Textarea({
                'class': 'form-control',
                'rows': 2,
            }),
            'why_appealing': forms.RadioSelect(),
            'why_appealing_other': forms.TextInput({
                'class': 'form-control',
            }),
            'describe_rule': forms.Textarea({
                'class': 'form-control',
                'rows': 2,
            }),
            'describe_actions': forms.Textarea({
                'class': 'form-control',
                'rows': 2,
            }),
            'wrong_actions': forms.RadioSelect(),
            'will_not_repeat': forms.RadioSelect(),
            'what_steps': forms.Textarea({
                'class': 'form-control',
                'rows': 2,
            }),
            'allowed_comments': forms.Textarea({
                'class': 'form-control',
                'rows': 2,
            }),
        }
