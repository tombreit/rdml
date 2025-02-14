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
# import warnings

from idutils import normalize_doi

from .errors import DataCiteError
from .request import DataCiteRequest


HTTP_OK = requests.codes["ok"]
HTTP_CREATED = requests.codes["created"]


class DataCiteRESTClient(object):
    """DataCite REST API client wrapper."""

    def __init__(self):
        from ..models import DataCiteConfiguration

        datacite_configuration = DataCiteConfiguration.objects.get(is_active=True)
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

    def get_doi(self, doi):
        """Get the URL where the resource pointed by the DOI is located.

        :param doi: DOI name of the resource.
        """
        request = self._create_request()
        resp = request.get("dois/" + doi)
        if resp.status_code == HTTP_OK:
            return resp.json()["data"]["attributes"]["url"]
        else:
            raise DataCiteError.factory(resp.status_code, resp.text)

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

    def post_doi(self, data):
        """Post a new JSON payload to DataCite."""
        headers = {
            "accept": "application/vnd.api+json",
            "content-type": "application/json",
        }

        data["type"] = "dois"
        body = {"data": data}
        body = json.dumps(body)

        request = self._create_request()
        resp = request.post("dois", body=body, headers=headers)
        if resp.status_code == HTTP_CREATED:
            return resp.json()["data"]["id"]
        else:
            raise DataCiteError.factory(resp.status_code, resp.text)

    def put_doi(self, doi, data):
        """Put a JSON payload to DataCite for an existing DOI."""
        headers = {"content-type": "application/vnd.api+json"}
        data["type"] = "dois"
        body = {"data": data}
        request = self._create_request()
        url = "dois/" + doi
        resp = request.put(url, body=json.dumps(body), headers=headers)
        if resp.status_code == HTTP_OK:
            return resp.json()["data"]["attributes"]
        else:
            raise DataCiteError.factory(resp.status_code, resp.text)

    def draft_doi(self, metadata=None, doi=None):
        """Create a draft doi.

        A draft DOI can be deleted

        If doi is not provided, DataCite
        will automatically create a DOI with a random,
        recommended DOI suffix

        :param metadata: metadata for the DOI
        :param doi: DOI (e.g. 10.123/456)
        :return:
        """
        data = {"attributes": {}}
        data["type"] = "dois"
        data["attributes"]["prefix"] = self.prefix

        if metadata:
            data["attributes"] = metadata

        if doi:
            doi = self.check_doi(doi)
            data["attributes"]["doi"] = doi

        return self.post_doi(data)

    def update_url(self, doi, url):
        """Update the url of a doi.

        :param url: URL where the doi will resolve.
        :param doi: DOI (e.g. 10.123/456)
        :return:
        """
        doi = self.check_doi(doi)
        data = {"attributes": {"url": url}}

        result = self.put_doi(doi, data)
        return result["url"]

    def delete_doi(self, doi):
        """Delete a doi.

        This will only work for draft dois

        :param doi: DOI (e.g. 10.123/456)
        :return:
        """
        request = self._create_request()
        resp = request.delete("dois/" + doi)

        if resp.status_code != 204:
            raise DataCiteError.factory(resp.status_code, resp.text)

    def public_doi(self, metadata, url, doi=None):
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
        data = {"attributes": metadata}
        data["type"] = "dois"
        data["attributes"]["prefix"] = self.prefix
        data["attributes"]["event"] = "publish"
        data["attributes"]["url"] = url
        if doi:
            doi = self.check_doi(doi)
            data["attributes"]["doi"] = doi

        return self.post_doi(data)

    def update_doi(self, doi, metadata=None, url=None):
        """Update the metadata or url for a DOI.

        :param url: URL where the doi will resolve.
        :param metadata: JSON format of the metadata.
        :return:
        """
        data = {"attributes": {}}
        data.update({"type": "dois"})

        doi = self.check_doi(doi)
        data["attributes"]["doi"] = doi
        if metadata:
            data["attributes"] = metadata
        if url:
            data["attributes"]["url"] = url

        return self.put_doi(doi, data)

    def private_doi(self, metadata, url, doi=None):
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
        data = {"attributes": metadata}
        data.update({"type": "dois"})

        data["attributes"]["prefix"] = self.prefix
        data["attributes"]["event"] = "register"
        data["attributes"]["url"] = url
        if doi:
            doi = self.check_doi(doi)
            data["attributes"]["doi"] = doi

        return self.post_doi(data)

    def hide_doi(self, doi):
        """Hide a previously registered DOI.

        This DOI will no
        longer be found in DataCite Search

        :param doi: DOI to hide e.g. 10.12345/1.
        :return:
        """
        data = {"attributes": {"event": "hide"}}
        data.update({"type": "dois"})

        if doi:
            doi = self.check_doi(doi)
            data["attributes"]["doi"] = doi

        return self.put_doi(doi, data)

    def show_doi(self, doi):
        """Show a previously registered DOI.

        This DOI will be found in DataCite Search

        :param doi: DOI to hide e.g. 10.12345/1.
        :return:
        """
        data = {"attributes": {"event": "publish"}}
        data.update({"type": "dois"})

        if doi:
            doi = self.check_doi(doi)
            data["attributes"]["doi"] = doi

        return self.put_doi(doi, data)

    def change_doi_state(self, doi, state, metadata):
        doi = self.check_doi(doi)
        data = {"attributes": metadata}
        data["attributes"]["event"] = state
        return self.put_doi(doi, data)

    def get_metadata(self, doi):
        """Get the JSON metadata associated to a DOI name.

        :param doi: DOI name of the resource.
        """
        """Put a JSON payload to DataCite for an existing DOI."""
        headers = {"content-type": "application/vnd.api+json"}
        request = self._create_request()
        resp = request.get("dois/" + doi, headers=headers)

        if resp.status_code == HTTP_OK:
            return resp.json()["data"]["attributes"]
        else:
            raise DataCiteError.factory(resp.status_code, resp.text)

    def get_media(self, doi):
        """Get list of pairs of media type and URLs associated with a DOI.

        :param doi: DOI name of the resource.
        """
        headers = {"content-type": "application/vnd.api+json"}
        request = self._create_request()
        resp = request.get("dois/" + doi, headers=headers)

        if resp.status_code == HTTP_OK:
            return resp.json()["relationships"]["media"]
        else:
            raise DataCiteError.factory(resp.status_code, resp.text)

    # def get_datacite_doi_state(self):
    #     state = "unset"
    #     if self.doi:
    #         print(f"{self.doi=}")
    #         state = DataCiteRESTClient().get_datacite_doi_state(self.doi)
    #     return state

    def get_datacite_doi_state(self, doi=None):
        UNSET_STATE = "unset"
        found = False

        if not doi:
            return (UNSET_STATE, found)

        headers = {"content-type": "application/vnd.api+json"}
        request = self._create_request()
        resp = request.get("dois/" + doi, headers=headers)

        print(f"{resp.status_code=}")

        if resp.status_code == HTTP_OK:
            # try:
            state = resp.json()["data"]["attributes"]["state"]
            found = True
            print(f"get_dataciste_doi_state: {state=}")
            # except KeyError as keyerror:
            #     print(f"{keyerror=}")
            #     # Draf dois do not have a state
            #     return "draft"
        else:
            # No match found for given doi.
            # raise DataCiteError.factory(resp.status_code, resp.text)
            state = UNSET_STATE
            found = False

        return (state, found)
