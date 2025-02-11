# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.urls import path
from . import views


app_name = "doimanager"


urlpatterns = [
    path("datacite-metadata/<uuid:resource_id>/", views.datacite_manager, name="datacite_manager"),
    path("datacite-metadata/<uuid:resource_id>/<str:transition_to>/", views.datacite_manager, name="datacite_manager"),
    # path('datacite-metadata/update/<uuid:project_id>', views.datacite_metadata_update, name="datacite_metadata_update"),
    # path('datacite-metadata/register/<uuid:project_id>', views.datacite_doi_register, name="datacite_doi_register"),
    # path('doi-transition/<uuid:project_id>/<str:transition_to>', views.doi_transition, name="doi_transition"),
]
