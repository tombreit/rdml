# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from ..research.models import Resource
from .datacite.rest_client import DataCiteRESTClient
from .datacite import errors as datacite_errors
from .models import DataCiteResource
from .metadata import get_rdml_metadata
from .utils import get_citation_snippet


@login_required
@permission_required("doimanager.register_or_update_dois", raise_exception=True)
@require_GET
def datacite_manager(request, resource_id, transition_to=None):
    print(80 * "-")
    print(f"datacite_manager: {transition_to=}")
    errors = []
    sync_citation_snippet = False
    transition_result = None

    project = Resource.objects.get(id=resource_id)
    print(f"{project=}")

    datacite, _created = DataCiteResource.objects.get_or_create(
        resource=project,
        # defaults={'resource': project.id,},
    )

    if datacite.doi:
        doi = datacite.doi
    else:
        # We do not set our DOI suffix manually, we are ok with the randomly
        # assigned DOI suffix from our registrar (here: datacite)
        # Setting DOI to a new proposed DOI
        doi = None

    datacite_doi_state, datacite_found = DataCiteRESTClient().get_datacite_doi_state(
        doi=doi, datacite_resource=datacite
    )
    print(f"{datacite_doi_state=}; {transition_to=}")

    if datacite_found:
        # We found a datacite record for this doi, ensure this is
        # saved in our datacite object:
        datacite.doi = doi
        datacite.save()

    if transition_to and transition_to != datacite_doi_state:
        print(f"Transition DOI for '{project}' from '{datacite_doi_state}' to state '{transition_to}'")
        # https://support.datacite.org/docs/api-create-dois
        # Possible actions:
        # publish - Triggers a state move from draft or registered to findable
        # register - Triggers a state move from draft to registered
        # hide - Triggers a state move from findable to registered

        # We always update metadate on remote datacite endpoint on every
        # DOI state transition.

        try:
            rdml_metadata = get_rdml_metadata(project.id, as_json=False)

            if transition_to == "draft":
                print("Transition to draft now")
                # to_draft is only possible for objects which do not yet have any DOI.
                # Create an identifier in Draft state -> event: None
                transition_result = DataCiteRESTClient().draft_doi(
                    metadata=rdml_metadata,
                    datacite_resource=datacite,
                )
                # draft_doi() returns the validated and draft-saved DOI
                datacite.doi = doi = transition_result

            elif datacite_doi_state == "draft" and transition_to == "registered":
                # Create a Findable DOI -> event: register
                transition_result = DataCiteRESTClient().change_doi_state(
                    doi=doi,
                    state="register",
                    metadata=rdml_metadata,
                    datacite_resource=datacite,
                )
            elif datacite_doi_state == "findable" and transition_to == "registered":
                # Hide a previously findable DOI (state: registered; event: hide):
                transition_result = DataCiteRESTClient().hide_doi(
                    doi=doi,
                    datacite_resource=datacite,
                )
            elif transition_to == "findable":
                # Create a Findable DOI -> event: publish
                transition_result = DataCiteRESTClient().change_doi_state(
                    doi=doi,
                    state="publish",
                    metadata=rdml_metadata,
                    datacite_resource=datacite,
                )

                # Only try to get a citation_snippet for findable DOIs
                sync_citation_snippet = True
            else:
                raise NotImplementedError

        except datacite_errors.DataCiteServerError as e:
            errors.append(e)
        except Exception as e:
            errors.append(e)

        else:
            # If no exceptions are raised, execute this try-else block:
            print(f"{transition_result=}")
            datacite.save()

            # datacite_after_transition = DataCiteResource.objects.get(resource__id=resource_id)
            datacite.refresh_from_db()
            datacite_doi_state, datacite_found = DataCiteRESTClient().get_datacite_doi_state(
                doi=doi, datacite_resource=datacite
            )
            print(f"doi state after transition: {datacite_doi_state}")

            if sync_citation_snippet and datacite.doi:
                datacite.citation_snippet = get_citation_snippet(doi)
                datacite.save(update_fields=["citation_snippet"])

            # Redirect to main view without transition url part
            return redirect("doimanager:datacite_manager", resource_id=project.id)

    print(f"{errors=}")
    print(f"{transition_result=}")

    context = {
        "errors": errors,
        "project": project,
        "datacite": datacite,
        "datacite_doi_state": datacite_doi_state,
        "doi": doi,
        "transition_result": transition_result,
    }

    return TemplateResponse(request, "doimanager/datacite_manager.html", context)
