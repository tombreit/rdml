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


"""Python API client wrapper for the DataCite Rest API.

API documentation is available at
https://support.datacite.org/reference/introduction.
"""

import json
import requests
from datetime import datetime

from ..utils import normalize_doi
from .errors import DataCiteError
from .request import DataCiteRequest


HTTP_OK = requests.codes["ok"]
HTTP_CREATED = requests.codes["created"]


class DataCiteRESTClient(object):
    """DataCite REST API client wrapper."""

    def __init__(self):
        from ..models import DataCiteConfiguration
        from django.core.exceptions import ImproperlyConfigured

        try:
            datacite_configuration = DataCiteConfiguration.objects.get(is_active=True)
        except DataCiteConfiguration.DoesNotExist:
            raise ImproperlyConfigured("No active DataCiteConfiguration found. Create one via the admin interface.")
        except DataCiteConfiguration.MultipleObjectsReturned:
            raise ImproperlyConfigured(
                "Multiple active DataCiteConfiguration instances found; ensure only one is active."
            )

        datacite_env = datacite_configuration.get_datacite_env()

        self.username = datacite_configuration.repo_id
        self.password = datacite_configuration.backend_password
        self.prefix = datacite_configuration.doi_prefix
        self.url = datacite_env.backend_url
        self.api_url = datacite_env.api_url
        self.timeout = 15

    def __repr__(self):
        """Create string representation of object."""
        return "<DataCiteRESTClient: {0}>".format(self.username)

    def _create_request(self):
        """Create a new Request object."""
        datacite_request = DataCiteRequest(
            base_url=self.api_url,
            username=self.username,
            password=self.password,
            timeout=self.timeout,
        )
        return datacite_request

    def _log_history(self, datacite_resource, method, url, request_data=None, response=None, error=None):
        """Log API communication to datacite_history field of DataCiteResource, but skip GET requests."""
        if datacite_resource is None:
            return
        if method.upper() == "GET":
            return  # Skip logging for GET requests
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "method": method,
            "url": url,
        }
        if request_data is not None:
            entry["request_data"] = request_data
        if response is not None:
            try:
                entry["response_status"] = response.status_code
                entry["response_body"] = response.json()
            except Exception:
                entry["response_body"] = getattr(response, "text", str(response))
        if error is not None:
            entry["error"] = str(error)
        # Append to history
        history = datacite_resource.datacite_history or []
        history.append(entry)
        datacite_resource.datacite_history = history
        datacite_resource.save(update_fields=["datacite_history"])

    def get_doi(self, doi, datacite_resource=None):
        """Get the URL where the resource pointed by the DOI is located.

        :param doi: DOI name of the resource.
        """
        request = self._create_request()
        url = "dois/" + doi
        try:
            resp = request.get(url)
            self._log_history(datacite_resource, "GET", url, response=resp)
            if resp.status_code == HTTP_OK:
                return resp.json()["data"]["attributes"]["url"]
            else:
                raise DataCiteError.factory(resp.status_code, resp.text)
        except Exception as e:
            self._log_history(datacite_resource, "GET", url, error=e)
            raise

    def check_doi(self, doi):
        """Check doi structure.

        Check that the doi has a form
        12.12345/123 with the prefix defined
        """
        # If prefix is in doi
        if "/" in doi:
            split = doi.split("/")
            prefix = split[0]
            if prefix != self.prefix:
                # Provided a DOI with the wrong prefix
                raise ValueError(
                    "Wrong DOI {0} prefix provided, it should be {1} as defined in the rest client".format(
                        prefix, self.prefix
                    )
                )
        else:
            doi = "{prefix}/{doi}".format(prefix=self.prefix, doi=doi)
        return normalize_doi(doi)

    def post_doi(self, data, datacite_resource=None):
        """Post a new JSON payload to DataCite."""
        headers = {
            "accept": "application/vnd.api+json",
            "content-type": "application/json",
        }

        data["type"] = "dois"
        body = {"data": data}
        body_json = json.dumps(body)
        url = "dois"
        request = self._create_request()
        try:
            resp = request.post(url, body=body_json, headers=headers)
            self._log_history(datacite_resource, "POST", url, request_data=body, response=resp)
            if resp.status_code == HTTP_CREATED:
                return resp.json()["data"]["id"]
            else:
                raise DataCiteError.factory(resp.status_code, resp.text)
        except Exception as e:
            self._log_history(datacite_resource, "POST", url, request_data=body, error=e)
            raise

    def put_doi(self, doi, data, datacite_resource=None):
        """Put a JSON payload to DataCite for an existing DOI."""
        headers = {"content-type": "application/vnd.api+json"}
        data["type"] = "dois"
        body = {"data": data}
        body_json = json.dumps(body)
        url = "dois/" + doi
        request = self._create_request()
        try:
            resp = request.put(url, body=body_json, headers=headers)
            self._log_history(datacite_resource, "PUT", url, request_data=body, response=resp)
            if resp.status_code == HTTP_OK:
                return resp.json()["data"]["attributes"]
            else:
                raise DataCiteError.factory(resp.status_code, resp.text)
        except Exception as e:
            self._log_history(datacite_resource, "PUT", url, request_data=body, error=e)
            raise

    def draft_doi(self, metadata=None, doi=None, datacite_resource=None):
        """Create a draft doi.

        A draft DOI can be deleted

        If doi is not provided, DataCite
        will automatically create a DOI with a random,
        recommended DOI suffix

        :param metadata: metadata for the DOI
        :param doi: DOI (e.g. 10.123/456)
        :return:
        """
        data = {"type": "dois", "attributes": {}}
        data["attributes"]["prefix"] = self.prefix

        if metadata:
            data["attributes"].update(metadata)

        if doi:
            doi = self.check_doi(doi)
            data["attributes"]["doi"] = doi

        return self.post_doi(data, datacite_resource)

    def update_url(self, doi, url, datacite_resource=None):
        """Update the url of a doi.

        :param url: URL where the doi will resolve.
        :param doi: DOI (e.g. 10.123/456)
        :return:
        """
        doi = self.check_doi(doi)
        data = {"attributes": {"url": url}}

        result = self.put_doi(doi, data, datacite_resource)
        return result["url"]

    def delete_doi(self, doi, datacite_resource=None):
        """Delete a doi.

        This will only work for draft dois

        :param doi: DOI (e.g. 10.123/456)
        :return:
        """
        request = self._create_request()
        url = "dois/" + doi
        try:
            resp = request.delete(url)
            self._log_history(datacite_resource, "DELETE", url, response=resp)
            if resp.status_code != 204:
                raise DataCiteError.factory(resp.status_code, resp.text)
        except Exception as e:
            self._log_history(datacite_resource, "DELETE", url, error=e)
            raise

    def public_doi(self, metadata, url, doi=None, datacite_resource=None):
        """Create a public doi.

        This DOI will be public and cannot be deleted

        If doi is not provided, DataCite
        will automatically create a DOI with a random,
        recommended DOI suffix

        Metadata should follow the DataCite Metadata Schema:
        http://schema.datacite.org/

        :param metadata: JSON format of the metadata.
        :param doi: DOI (e.g. 10.123/456)
        :param url: URL where the doi will resolve.
        :return:
        """
        data = {"type": "dois", "attributes": {}}
        data["attributes"].update(metadata)
        data["attributes"]["prefix"] = self.prefix
        data["attributes"]["event"] = "publish"
        data["attributes"]["url"] = url
        if doi:
            doi = self.check_doi(doi)
            data["attributes"]["doi"] = doi

        return self.post_doi(data, datacite_resource)

    def update_doi(self, doi, metadata=None, url=None, datacite_resource=None):
        """Update the metadata or url for a DOI.

        :param url: URL where the doi will resolve.
        :param metadata: JSON format of the metadata.
        :return:
        """
        data = {"type": "dois", "attributes": {}}

        doi = self.check_doi(doi)
        data["attributes"]["doi"] = doi
        if metadata:
            data["attributes"].update(metadata)
        if url:
            data["attributes"]["url"] = url

        return self.put_doi(doi, data, datacite_resource)

    def private_doi(self, metadata, url, doi=None, datacite_resource=None):
        """Publish a doi in a registered state.

        A DOI generated by this method will
        not be found in DataCite Search

        This DOI cannot be deleted

        If doi is not provided, DataCite
        will automatically create a DOI with a random,
        recommended DOI suffix

        Metadata should follow the DataCite Metadata Schema:
        http://schema.datacite.org/

        :param metadata: JSON format of the metadata.
        :return:
        """
        data = {"type": "dois", "attributes": {}}
        data["attributes"].update(metadata)
        data["attributes"]["prefix"] = self.prefix
        data["attributes"]["event"] = "register"
        data["attributes"]["url"] = url
        if doi:
            doi = self.check_doi(doi)
            data["attributes"]["doi"] = doi

        return self.post_doi(data, datacite_resource)

    def hide_doi(self, doi, datacite_resource=None):
        """Hide a previously registered DOI.

        This DOI will no
        longer be found in DataCite Search

        :param doi: DOI to hide e.g. 10.12345/1.
        :return:
        """
        data = {"type": "dois", "attributes": {"event": "hide"}}

        if doi:
            doi = self.check_doi(doi)
            data["attributes"]["doi"] = doi

        return self.put_doi(doi, data, datacite_resource)

    def show_doi(self, doi, datacite_resource=None):
        """Show a previously registered DOI.

        This DOI will be found in DataCite Search

        :param doi: DOI to hide e.g. 10.12345/1.
        :return:
        """
        data = {"type": "dois", "attributes": {"event": "publish"}}

        if doi:
            doi = self.check_doi(doi)
            data["attributes"]["doi"] = doi

        return self.put_doi(doi, data, datacite_resource)

    def change_doi_state(self, doi, state, metadata, datacite_resource=None):
        doi = self.check_doi(doi)
        data = {"type": "dois", "attributes": {}}
        data["attributes"].update(metadata)
        data["attributes"]["event"] = state
        return self.put_doi(doi, data, datacite_resource)

    def get_metadata(self, doi, datacite_resource=None):
        """Get the JSON metadata associated to a DOI name.

        :param doi: DOI name of the resource.
        """
        """Put a JSON payload to DataCite for an existing DOI."""
        headers = {"content-type": "application/vnd.api+json"}
        request = self._create_request()
        url = "dois/" + doi
        try:
            resp = request.get(url, headers=headers)
            self._log_history(datacite_resource, "GET", url, response=resp)
            if resp.status_code == HTTP_OK:
                return resp.json()["data"]["attributes"]
            else:
                raise DataCiteError.factory(resp.status_code, resp.text)
        except Exception as e:
            self._log_history(datacite_resource, "GET", url, error=e)
            raise

    def get_media(self, doi, datacite_resource=None):
        """Get list of pairs of media type and URLs associated with a DOI.

        :param doi: DOI name of the resource.
        """
        headers = {"content-type": "application/vnd.api+json"}
        request = self._create_request()
        url = "dois/" + doi
        try:
            resp = request.get(url, headers=headers)
            self._log_history(datacite_resource, "GET", url, response=resp)
            if resp.status_code == HTTP_OK:
                return resp.json()["relationships"]["media"]
            else:
                raise DataCiteError.factory(resp.status_code, resp.text)
        except Exception as e:
            self._log_history(datacite_resource, "GET", url, error=e)
            raise

    def get_datacite_doi_state(self, doi=None, datacite_resource=None):
        UNSET_STATE = "unset"
        found = False

        if not doi:
            return (UNSET_STATE, found)

        headers = {"content-type": "application/vnd.api+json"}
        request = self._create_request()
        url = "dois/" + doi
        try:
            resp = request.get(url, headers=headers)
            self._log_history(datacite_resource, "GET", url, response=resp)
            if resp.status_code == HTTP_OK:
                state = resp.json()["data"]["attributes"]["state"]
                found = True
            else:
                state = UNSET_STATE
                found = False
        except Exception as e:
            self._log_history(datacite_resource, "GET", url, error=e)
            state = UNSET_STATE
            found = False

        return (state, found)
