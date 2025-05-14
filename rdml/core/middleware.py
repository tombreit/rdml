# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.conf import settings
from whitenoise.middleware import WhiteNoiseMiddleware

from django.core.exceptions import PermissionDenied

from .helpers import get_ips_from_ranges, get_client_ip


def more_whitenoise_middleware(get_response):
    """
    Instantiates WhiteNoiseMiddleware, adds extra file directories,
    and returns the callable middleware.
    Inspired by https://github.com/mblayman/homeschool/blob/5f11ca3208b0d422223ca8da2ddf6a3289a71860/homeschool/middleware.py#L8
    """
    whitenoise = WhiteNoiseMiddleware(get_response, settings=settings)

    for more_noise in settings.RDML_MORE_WHITENOISE:
        whitenoise.add_files(more_noise["directory"], prefix=more_noise["prefix"])

    def middleware(request):
        return whitenoise(request)

    return middleware


ips_allowed = get_ips_from_ranges(settings.RDML_EDIT_ALLOWED_IP_RANGES)
ips_allowed_all = settings.RDML_EDIT_ALLOWED_IP_RANGES == ["*"]


def ip_allowed_middleware(get_response):
    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        client_ip = get_client_ip(request)
        request.ip_allowed = any([client_ip in ips_allowed, ips_allowed_all])

        response = get_response(request)

        return response

    return middleware


def admin_ip_restriction_middleware(get_response):
    """
    Deny any request under /admin/ unless request.ip_allowed is True.
    Must come after the middleware that sets request.ip_allowed.
    """

    def middleware(request):
        admin_prefix = getattr(settings, "ADMIN_URL_PREFIX", "/admin/")
        if request.path.startswith(admin_prefix) and not getattr(request, "ip_allowed", False):
            client_ip = get_client_ip(request)
            raise PermissionDenied(f"Admin interface access denied: IP {client_ip} not in allowed range")

        response = get_response(request)

        return response

    return middleware
