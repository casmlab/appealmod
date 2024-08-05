from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.views.generic import TemplateView, CreateView, FormView, UpdateView

from main.forms import SignUpForm, BanAppealMainForm, BanAppealAuthForm

from django.urls import reverse_lazy

from main.models import BanAppealData


class IndexView(CreateView):
    template_name = "index.html"
    form_class = SignUpForm
    success_url = reverse_lazy('sign-up-success')


class SignUpView(CreateView):
    template_name = "sign-up/sign-up-page.html"
    form_class = SignUpForm
    success_url = reverse_lazy('sign-up-success')


class SignUpSuccessView(TemplateView):
    template_name = "sign-up/sign-up-success.html"


class FormAuthView(FormView):
    template_name = "form/auth.html"
    form_class = BanAppealAuthForm

    def form_valid(self, form):
        reddit_username = form.cleaned_data['reddit_username']
        subreddit = form.cleaned_data['subreddit']
        url = reverse_lazy('form') + \
            f'?reddit_username={reddit_username}&subreddit={subreddit}'
        return redirect(url)


class FormAuthErrorView(TemplateView):
    template_name = "form/auth-error.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reddit_username = self.request.GET.get('reddit_username')
        subreddit = self.request.GET.get('subreddit')
        context.update({
            'reddit_username': reddit_username,
            'subreddit': subreddit,
        })
        return context


class MainFormView(UpdateView):
    template_name = "form/form.html"
    form_class = BanAppealMainForm
    success_url = reverse_lazy('form-thanks')

    def get(self, request, *args, **kwargs):
        reddit_username = request.GET.get('reddit_username')
        subreddit = request.GET.get('subreddit')
        if not reddit_username or not subreddit:
            url = reverse_lazy('form-auth')
            return redirect(url)
        auth = BanAppealData.objects.auth(reddit_username, subreddit)
        if not auth:
            url = reverse_lazy('form-auth-error') + \
                  f'?reddit_username={reddit_username}&subreddit={subreddit}'
            return redirect(url)
        if auth.filled():
            url = reverse_lazy('form-error')
            return redirect(url)
        return super().get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        reddit_username = self.request.GET.get('reddit_username')
        subreddit = self.request.GET.get('subreddit')
        return BanAppealData.objects.auth(reddit_username, subreddit)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reddit_username = self.request.GET.get('reddit_username')
        subreddit = self.request.GET.get('subreddit')
        context.update({
            'reddit_username': reddit_username,
            'subreddit': subreddit,
        })
        return context


class FormErrorView(TemplateView):
    template_name = "form/form-error.html"


class FormThanksView(TemplateView):
    template_name = "form/thanks.html"


class DebugView(TemplateView):
    template_name = "debug.html"

    def dispatch(self, request, *args, **kwargs):
        BanAppealData.objects.create('some_username', 'some_subreddit')
        return super().dispatch(request, *args, **kwargs)
