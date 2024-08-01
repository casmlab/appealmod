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
    why_banned = forms.CharField(
        label='Find and copy/paste here the note from mods on '
              'why you were banned',
        widget=forms.Textarea({'class': 'form-control', 'rows': 2}),
        required=True,
    )
    why_appealing = forms.ChoiceField(
        label='Why are you appealing your ban?',
        choices=[
            ('disagree', "I don't agree with the rule"),
            ('not-apply', "I don't think the rule applies to my behavior"),
            ('regret', "I regret my behavior"),
            ('other', "Other (please specify below)"),
        ],
        widget=forms.RadioSelect(),
        required=True,
    )
    why_appealing_other = forms.CharField(
        widget=forms.TextInput({'class': 'form-control'}),
        required=False,
    )
    describe_rule = forms.CharField(
        label='Can you describe the rule in your own words?',
        widget=forms.Textarea({'class': 'form-control', 'rows': 2}),
        required=True,
    )
    describe_actions = forms.CharField(
        label='Can you describe your actions that led to the ban '
              'and the circumstances that made you act that way?',
        widget=forms.Textarea({'class': 'form-control', 'rows': 2}),
        required=True,
    )
    wrong_actions = forms.ChoiceField(
        label='Do you think your actions were wrong?',
        choices=[
            ('no', "No"),
            ('yes', "Yes"),
        ],
        widget=forms.RadioSelect(),
        required=True,
    )
    will_not_repeat = forms.ChoiceField(
        label='Are you willing to pledge that you will not repeat '
                     'such actions in the future?',
        choices=[
            ('no', "No"),
            ('yes', "Yes"),
        ],
        widget=forms.RadioSelect(),
        required=True,
    )
    what_steps = forms.CharField(
        label="What steps will you take to ensure "
              "that you don't do this again?",
        widget=forms.Textarea({'class': 'form-control', 'rows': 2}),
        required=True,
    )
    allowed_comments = forms.TypedMultipleChoiceField(
        label='Which of the following comment(s) do you think '
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
        widget=forms.CheckboxSelectMultiple(),
        coerce=str,
        required=False,
    )

    class Meta:
        model = BanAppealData
        fields = [
            'why_banned', 'why_appealing', 'why_appealing_other',
            'describe_rule', 'describe_actions',
            'wrong_actions', 'will_not_repeat',
            'what_steps', 'allowed_comments',
        ]
