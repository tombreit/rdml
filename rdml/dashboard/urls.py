# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.urls import path

from .views import dashboard

app_name = "dashboard"

urlpatterns = [
    path("", dashboard, name="dashboard"),
]
