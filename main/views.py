from django.shortcuts import render
from django.views.generic import TemplateView, CreateView

from main.forms import SignUpForm


class IndexView(TemplateView):
    template_name = "index.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)


class SignUpView(CreateView):
    template_name = "sign-up/sign-up-page.html"
    form_class = SignUpForm
    success_url = '/'
