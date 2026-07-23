# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import logging

from django.core.exceptions import PermissionDenied
from functools import wraps

from .helpers import get_client_ip


logger = logging.getLogger(__name__)


def restrict_to_ip_range(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.ip_allowed:
            # Never interpolate the client IP (or the request repr) into the
            # exception message: it is client-controlled and ends up in the 403
            # template, the logs and the admin mails.
            logger.warning("Access denied for IP %s on path %s", get_client_ip(request), request.path)
            raise PermissionDenied("Access denied: your IP address is not in the allowed range.")

        return view_func(request, *args, **kwargs)

    return wrapper
