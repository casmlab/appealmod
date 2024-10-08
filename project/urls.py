"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from web.views.api.api_form import FormApiView
from web.views.debug import DebugView
from web.views.form import FormAuthView, FormAuthErrorView, MainFormView, \
    FormErrorView, FormThanksView
from web.views.home import IndexView, SignUpView, SignUpSuccessView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),

    path('sign-up/', SignUpView.as_view(), name='sign-up'),
    path('sign-up-success/', SignUpSuccessView.as_view(), name='sign-up-success'),

    path('form/auth/', FormAuthView.as_view(), name='form-auth'),
    path('form/auth/error/', FormAuthErrorView.as_view(), name='form-auth-error'),
    path('form/', MainFormView.as_view(), name='form'),
    path('form/error/', FormErrorView.as_view(), name='form-error'),
    path('form/thanks/', FormThanksView.as_view(), name='form-thanks'),

    path('api/form/', FormApiView.as_view(), name='api-form'),

    path('debug/', DebugView.as_view(), name='debug'),
]
# todo: + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
