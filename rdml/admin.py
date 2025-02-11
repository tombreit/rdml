# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.contrib import admin


class RDAdminSite(admin.AdminSite):
    def each_context(self, request):
        from rdml.organization.models import Branding

        branding = Branding.load()

        context = super().each_context(request)
        context.update(
            {
                "site_header": f"{branding.organization_name} Research Data Management",
                "site_title": f"{branding.organization_abbr} Research Data Management Portal",
                "index_title": f"Welcome to the {branding.organization_name} Research Data Management Portal",
            }
        )
        return context
