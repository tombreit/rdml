# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.urls import reverse
from django.http import Http404
from django.template.response import TemplateResponse

from ..research.models.base_models import Resource


def landing_page_list(request):
    resources_public = Resource.public_objects.all()
    resources_all_count = Resource.objects.count()
    context = {
        "resources_all_count": resources_all_count,
        "resources_public": resources_public,
        "resources_suppressed_count": resources_all_count - resources_public.count(),
    }

    return TemplateResponse(request, "doiresolver/landing_page_listing.html", context)


def landing_page(request, identifier=None, pk_uuid=None):
    print(f"landing_page called with {identifier=}, {pk_uuid=}")
    try:
        if identifier:
            resource = Resource.public_objects.get(slug__exact=identifier)
        elif pk_uuid:
            resource = Resource.public_objects.get(id=str(pk_uuid))
    except Resource.DoesNotExist:
        listing_url = reverse("doiresolver:doi-list")
        raise Http404(
            f"Resource with identifier `{identifier}` does not exist. Currently resolvable DOIs: <a href='{listing_url}'>{listing_url}</a>"
        )
        # return HttpResponseNotFound("Here's the text of the web page.")

    context = {"resource": resource}

    return TemplateResponse(request, "doiresolver/landing_page.html", context)
