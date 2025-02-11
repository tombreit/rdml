# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.urls import path
from django.contrib.auth import views as auth_views


app_name = "accounts"

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="admin/login.html"), name="login"),
]
