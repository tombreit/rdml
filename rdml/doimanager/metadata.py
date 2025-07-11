# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import json
from django.urls import reverse
from django.contrib.sites.models import Site

from rdml.research.models import Resource


def get_creators(resource_id):
    creators = []
    # TODO: merge with get_contributors

    resource = Resource.objects.get(id=resource_id)

    for creator in resource.creatorperson_set.all():
        creator_dict = {
            "name": creator.person.get_full_name,
            "givenName": creator.person.first_name,
            "familyName": creator.person.last_name,
            # contributorType is not an attribute of creator, but only for
            # contributor.
            # "contributorType": creator.datacite_contributor_type,
        }

        name_identifiers = []
        if creator.person.orcid_id:
            name_identifiers.append(
                {
                    "schemeUri": "https://orcid.org",
                    "nameIdentifier": creator.person.orcid_id,
                    "nameIdentifierScheme": "ORCID",
                }
            )

        if creator.person.cone_id:
            name_identifiers.append(
                {
                    "schemeUri": "https://pure.mpdl.mpg.de",
                    "nameIdentifier": f"https://pure.mpg.de/cone/persons/resource/{creator.person.cone_id}",
                    "nameIdentifierScheme": "PuRe CoNE ID",
                }
            )

        if name_identifiers:
            creator_dict.update({"nameIdentifiers": name_identifiers})

        creators.append(creator_dict)
    return creators


# def get_contributors(self):
#     contributors = []
#     for contributor in resource_obj.contributorperson_set.all():
#         contributor_dict = {
#             "name": contributor.person.get_full_name,
#             "givenName": contributor.person.first_name,
#             "familyName": contributor.person.last_name,
#             # "affiliation": [
#             #     {
#             #     "name": "Delft University of Technology",
#             #     "affiliationIdentifier": "https://ror.org/02e2c7k09",
#             #     "affiliationIdentifierScheme": "ROR"
#             #     }
#             # ],
#             "contributorType": contributor.datacite_contributor_type,
#         }
#         name_identifiers = []
#         if contributor.person.orcid_id:
#             name_identifiers.append({
#                 "schemeUri": "https://orcid.org",
#                 "nameIdentifier": contributor.person.orcid_id,
#                 "nameIdentifierScheme": "ORCID"
#             })
#         if contributor.person.cone_id:
#             name_identifiers.append({
#                 "schemeUri": "https://pure.mpdl.mpg.de",
#                 "nameIdentifier": f"https://pure.mpg.de/cone/persons/resource/{contributor.person.cone_id}",
#                 "nameIdentifierScheme": "PuRe CoNE ID"
#             })
#         if name_identifiers:
#             contributor_dict.update({"nameIdentifiers": name_identifiers})
#         contributors.append(contributor_dict)
#     return contributors


def get_rdml_metadata(resource_id, as_json=True):
    resource = Resource.objects.get(id=resource_id)

    errors = []

    try:
        # --- Basic checks for required attributes ---
        missing_required_fields = []

        if not resource.datacite_resource_type:
            missing_required_fields.append("Datacite ResourceType")
        if not resource.datacite_resource_type_general:
            missing_required_fields.append("Datacite ResourceTypeGeneral")

        # Check for creators
        creators_list = get_creators(resource_id)
        if not creators_list:
            missing_required_fields.append("Creators")

        if not resource.date_start:
            missing_required_fields.append("Start Date (for publicationYear)")
        if not resource.title_en:
            missing_required_fields.append("Title (English)")
        if not resource.publisher:
            missing_required_fields.append("Publisher")
        if not resource.language:
            missing_required_fields.append("Language")

        if missing_required_fields:
            raise ValueError(f"Missing required metadata attributes: {', '.join(missing_required_fields)}.")

        # Construct metadata
        current_site = Site.objects.get_current()
        redirect_url = f"https://{current_site.domain}{reverse('doiresolver:landing-page', args=[resource.pk])}"

        if hasattr(resource, "doi"):
            prefix = resource.doi.split("/")[0]
        else:
            from .models import DataCiteConfiguration

            datacite_configuration = DataCiteConfiguration.objects.get(is_active=True)
            prefix = datacite_configuration.doi_prefix

        metadata = {
            "url": redirect_url,
            "prefix": prefix,
            "publisher": resource.publisher.name,  # Already checked for existence
            "language": resource.language,  # Already checked for existence
            "publicationYear": resource.date_start.year,  # Already checked for existence
            "creators": creators_list,  # Use the fetched list, already checked for non-emptiness
            # "contributors": self.get_contributors(),
            "types": {
                "resourceType": resource.datacite_resource_type,
                "resourceTypeGeneral": resource.datacite_resource_type_general,
            },
            "titles": [
                {"lang": "en", "title": resource.title_en},
            ],
        }

        if resource.abstract_en:
            metadata["descriptions"].append(
                {
                    "lang": "en",
                    "description": resource.abstract_en,
                    "descriptionType": "Abstract",
                }
            )

        # Multilanguage metadata
        if resource.title_de:
            metadata["titles"].append(
                {
                    "lang": "de",
                    "title": resource.title_de,
                }
            )

        if resource.abstract_de:
            metadata["descriptions"].append(
                {
                    "lang": "de",
                    "description": resource.abstract_de,
                    "descriptionType": "Abstract",
                }
            )

        if as_json:
            metadata = json.dumps(metadata, sort_keys=True, indent=2)
        else:
            metadata = metadata

    except ValueError as e:
        errors.append(e)
        raise e
    except AttributeError as e:
        errors.append(e)
        raise e

    return metadata
