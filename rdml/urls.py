# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.views.defaults import server_error


urlpatterns = [
    path("_500/", server_error),  # Forcefully raise 500 Internal Server Error
    path("", RedirectView.as_view(url="resource/", permanent=False)),
    path("admin/", admin.site.urls),
    path("accounts/", include("rdml.accounts.urls")),
    path("resource/", include("rdml.doiresolver.urls")),
    path("doimanager/", include("rdml.doimanager.urls")),
    path("dashboard/", include("rdml.dashboard.urls")),
]

if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += debug_toolbar_urls()
