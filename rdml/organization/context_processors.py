# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from .models import Branding


def branding(request):
    """Make branding settings available for all requests."""
    branding = Branding.load()

    return {
        "organization_name": branding.organization_name,
        "organization_abbr": branding.organization_abbr,
        "branding_logo": branding.organization_logo,
        "branding_figurative_mark": branding.organization_figurative_mark,
        "branding_affiliation": branding.organization_affiliation,
    }
