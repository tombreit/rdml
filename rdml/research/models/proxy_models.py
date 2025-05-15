# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.db import models

from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField

from .base_models import Resource


# class ProjectManager(models.Manager):
#     def get_queryset(self):
#         return super().get_queryset().filter(resource_type=Resource.ResourceType.PROJECT)

#     def create(self, **kwargs):
#         kwargs.update({'resource_type': Resource.ResourceType.PROJECT})
#         return super().create(**kwargs)

# class Project(Resource):
#     objects = ProjectManager()

#     # def save(self, *args, **kwargs):
#     #     self.resource_type = Resource.ResourceType.PROJECT
#     #     super().save(*args, **kwargs)

#     class Meta:
#         proxy = True


class ResearchResourceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()  # .exclude(resource_type=Resource.ResourceType.PROJECT)


class ResearchResource(Resource):
    objects = ResearchResourceManager()
    history = AuditlogHistoryField()

    class Meta:
        proxy = True


auditlog.register(
    ResearchResource,
    m2m_fields=[
        "child_resources",
        "curators",
        "creators",
        "contributors",
        "keywords",
        "cv_subject_areas",
        "research_funding_agency",
        "cv_time_dimension",
        "cv_sampling_procedure",
        "cv_mode_of_collection",
        "cv_geographic_areas",
    ],
)
