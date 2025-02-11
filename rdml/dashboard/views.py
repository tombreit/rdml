from django.urls import reverse
from django.template.response import TemplateResponse
from django.contrib.auth.decorators import login_required

from ..research.models import ResearchResource


@login_required
def dashboard(request):

    navitems = [
        # {
        #     'url': reverse('admin:index'),
        #     'title': 'Backend',
        # },
        {
            'url': reverse('admin:research_researchresource_changelist'),
            'title': 'Administration',
        },
        {
            'url': reverse('doiresolver:doi-list'),
            'title': 'Landing pages',
        },
    ]

    research_resources = ResearchResource.objects.all()
    context = {
        "research_resources": research_resources,
        "research_resources_with_doi": research_resources.filter(dataciteresource__doi__isnull=False).count(),
        "research_resources_without_doi": research_resources.filter(dataciteresource__doi__isnull=True).count(),
        "navitems": navitems,
    }

    return TemplateResponse(request, "dashboard/dashboard.html", context)
