# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.contrib import messages
from django.urls import reverse
from .models import Branding
from django.utils.html import format_html


def branding(request):
    """Make branding settings available for all requests."""
    try:
        branding = Branding.objects.first()
        branding_dict = {
            "organization_name": branding.organization_name,
            "organization_abbr": branding.organization_abbr,
            "branding_logo": branding.organization_logo,
            "branding_figurative_mark": branding.organization_figurative_mark,
            "branding_affiliation": branding.organization_affiliation,
        }
    except (Branding.DoesNotExist, AttributeError):
        branding_meta = Branding._meta
        messages.warning(
            request,
            format_html(
                'No branding configuration found. Please create one: <a href="{}">{} > {} > {}</a>.',
                reverse("admin:organization_branding_add"),
                "Home",
                branding_meta.app_config.verbose_name,
                branding_meta.verbose_name,
            ),
        )
        branding_dict = {}

    return branding_dict
