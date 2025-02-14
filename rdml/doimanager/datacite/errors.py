# DataCite is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License quoted below.

# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2018 Center for Open Science.
# Copyright (C) 2019-2024 Caltech.
# Copyright (C) 2024 Institute of Biotechnology of the Czech Academy of Sciences.
#
# SPDX-License-Identifier: BSD-3-Clause

# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.

# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.

# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
# OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.


"""Errors for the DataCite API.

MDS error responses will be converted into an exception from this module.
Connection issues raises :py:exc:`datacite.errors.HttpError` while DataCite
MDS error responses raises a subclass of
:py:exc:`datacite.errors.DataCiteError`.
"""


class HttpError(Exception):
    """Exception raised when a connection problem happens."""


class DataCiteError(Exception):
    """Exception raised when the server returns a known HTTP error code.

    Known HTTP error codes include:

    * 204 No Content
    * 400 Bad Request
    * 401 Unauthorized
    * 403 Forbidden
    * 404 Not Found
    * 410 Gone (deleted)
    """

    @staticmethod
    def factory(err_code, *args):
        """Create exceptions through a Factory based on the HTTP error code."""
        if err_code == 204:
            return DataCiteNoContentError(*args)
        elif err_code == 400:
            return DataCiteBadRequestError(*args)
        elif err_code == 401:
            return DataCiteUnauthorizedError(*args)
        elif err_code == 403:
            return DataCiteForbiddenError(*args)
        elif err_code == 404:
            return DataCiteNotFoundError(*args)
        elif err_code == 410:
            return DataCiteGoneError(*args)
        elif err_code == 412:
            return DataCitePreconditionError(*args)
        else:
            return DataCiteServerError(*args)


class DataCiteServerError(DataCiteError):
    """An internal server error happened on the DataCite end. Try later.

    Base class for all 5XX-related HTTP error codes.
    """


class DataCiteRequestError(DataCiteError):
    """A DataCite request error. You made an invalid request.

    Base class for all 4XX-related HTTP error codes as well as 204.
    """


class DataCiteNoContentError(DataCiteRequestError):
    """DOI is known to MDS, but not resolvable.

    This might be due to handle's latency.
    """


class DataCiteBadRequestError(DataCiteRequestError):
    """Bad request error.

    Bad requests can include e.g. invalid XML, wrong domain, wrong prefix.
    Request body must be exactly two lines: DOI and URL
    One or more of the specified mime-types or urls are invalid (e.g. non
    supported mimetype, not allowed url domain, etc.)
    """


class DataCiteUnauthorizedError(DataCiteRequestError):
    """Bad username or password."""


class DataCiteForbiddenError(DataCiteRequestError):
    """Login problem, dataset belongs to another party or quota exceeded."""


class DataCiteNotFoundError(DataCiteRequestError):
    """DOI does not exist in the database."""


class DataCiteGoneError(DataCiteRequestError):
    """Requested dataset was marked inactive (using DELETE method)."""


class DataCitePreconditionError(DataCiteRequestError):
    """Metadata must be uploaded first."""
