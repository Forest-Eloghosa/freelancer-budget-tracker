"""
URL configuration for freelancer_budget_tracker project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import path, include
from budget.forms import (
    BootstrapAuthForm,
    BootstrapPasswordResetForm,
    BootstrapSetPasswordForm,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(form_class=BootstrapAuthForm),
        name='login',
    ),
    path(
        'accounts/password_reset/',
        auth_views.PasswordResetView.as_view(form_class=BootstrapPasswordResetForm),
        name='password_reset',
    ),
    path(
        'accounts/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            form_class=BootstrapSetPasswordForm
        ),
        name='password_reset_confirm',
    ),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('budget.urls')),
]