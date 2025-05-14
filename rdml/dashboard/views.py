# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.urls import reverse
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required

from rdml.core.decorators import restrict_to_ip_range
from ..research.models import ResearchResource


@login_required
@restrict_to_ip_range
def dashboard(request):
    research_resources = ResearchResource.objects.all()

    navitems = [
        # {
        #     'url': reverse('admin:index'),
        #     'title': 'Backend',
        # },
        {
            "url": reverse("admin:research_researchresource_changelist"),
            "pretitle": "Backend",
            "title": "Research resources",
            "count": research_resources.count(),
        },
        {
            "url": reverse("doiresolver:doi-list"),
            "pretitle": "Frontend",
            "title": "Landing pages",
            "count": research_resources.filter(is_public=True).count(),
        },
    ]

    context = {
        "research_resources_with_doi": research_resources.filter(dataciteresource__doi__isnull=False).count(),
        "research_resources_without_doi": research_resources.filter(dataciteresource__doi__isnull=True).count(),
        "research_resources_yours": research_resources.filter(curators=request.user).count(),
        "public_landing_pages_count": research_resources.filter(is_public=True).count(),
        "not_public_landing_pages_count": research_resources.filter(is_public=False).count(),
        "navitems": navitems,
    }

    return TemplateResponse(request, "dashboard/dashboard.html", context)
