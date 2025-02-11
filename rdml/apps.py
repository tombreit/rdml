# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.contrib.admin.apps import AdminConfig


class RDAdminConfig(AdminConfig):
    default_site = "rdml.admin.RDAdminSite"
