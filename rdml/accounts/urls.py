# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.urls import path
from django.contrib.auth import views as auth_views

from rdml.core.decorators import restrict_to_ip_range


app_name = "accounts"

urlpatterns = [
    # Restricted to the allowed IP ranges: this is the only unauthenticated
    # entry point into the LDAP/AD directory and is otherwise unthrottled.
    path(
        "login/",
        restrict_to_ip_range(auth_views.LoginView.as_view(template_name="admin/login.html")),
        name="login",
    ),
]
