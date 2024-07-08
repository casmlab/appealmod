from django.shortcuts import render, redirect
from django.views.generic import TemplateView, CreateView, FormView

from main.forms import SignUpForm, BanAppealMainForm, BanAppealAuthForm

from django.urls import reverse_lazy


class IndexView(TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class SignUpView(CreateView):
    template_name = "sign-up/sign-up-page.html"
    form_class = SignUpForm
    success_url = reverse_lazy('sign-up-success')


class SignUpSuccessView(TemplateView):
    template_name = "sign-up/sign-up-success.html"


class BanAppealAuthFormView(FormView):
    template_name = "ban-appeal/auth.html"
    form_class = BanAppealAuthForm

    def form_valid(self, form):
        url = reverse_lazy('ban-appeal-form') + \
            '?reddit_username=' + form.cleaned_data['reddit_username'] + \
            '&subreddit=' + form.cleaned_data['subreddit']
        return redirect(url)


class BanAppealMainFormView(CreateView):
    template_name = "ban-appeal/form.html"
    form_class = BanAppealMainForm
    success_url = reverse_lazy('ban-appeal-thanks')


class BanAppealThanksView(TemplateView):
    template_name = "ban-appeal/thanks.html"
