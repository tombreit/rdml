# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import re
import requests


def normalize_doi(doi):
    """
    See http://en.wikipedia.org/wiki/Digital_object_identifier.
    """
    if not doi:
        raise ValueError("DOI must be given")
    doi_regexp = re.compile(r"(doi:\s*|(?:https?://)?(?:dx\.)?doi\.org/)?(10\.\d+(\.\d+)*/.+)$", flags=re.I)
    m = doi_regexp.match(doi)
    if not m:
        raise ValueError(f"Invalid DOI format: {doi}")
    return m.group(2)


def get_citation_snippet(doi):
    """
    !Citation Snippet only available for DataCite production endpoint!
    DataCite services that contain citation data rely on an external service, Crossref Event Data. Because of this dependency, citation data is not available in DataCite test environments, doi.test.datacite.org (Fabrica test), api.test.datacite.org (API test).
    Source: https://support.datacite.org/docs/eventdata-guide

    Further info:
    * 3rd party service: https://citation.crosscite.org/docs.html
    * https://blog.datacite.org/citation-formatting-service-upgrade/
    """

    from .models import DataCiteConfiguration
    from .datacite.rest_client import DataCiteRESTClient

    try:
        print(f"get_citation_snippet {doi=}")
        datacite_configuration = DataCiteConfiguration.objects.get(is_active=True)

        # Possible values:"findable", "registered", and "draft"
        # TODO: find out for which values a citation snippet is available
        doi_state = DataCiteRESTClient().get_metadata(doi)
        print(f"{doi_state['state']=}")

        url = f"{datacite_configuration.get_datacite_env.doi_base_url}{doi}"
        print(f"{url=}")

        headers = {"Accept": "text/x-bibliography", "style": "apa"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        http_status_code = response.status_code
        print(f"{http_status_code=}")
        response_as_utf8 = response.content.decode("utf-8")
        return response_as_utf8
    except requests.exceptions.HTTPError as httperror:
        print(f"get_citation_snippet error for {url}: {httperror}")
        return ""
    except BaseException as base_exception:
        print(f"get_citation_snippet error for {url}: {base_exception}")
        return ""
