# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.apps import AppConfig


class ClassificationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rdml.classification"
