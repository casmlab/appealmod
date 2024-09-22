from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from web.forms import SignUpForm


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
