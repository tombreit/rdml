# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.core.exceptions import PermissionDenied
from functools import wraps


def restrict_to_ip_range(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.ip_allowed:
            raise PermissionDenied(f"Access denied: IP {request} not in allowed range")

        return view_func(request, *args, **kwargs)

    return wrapper
