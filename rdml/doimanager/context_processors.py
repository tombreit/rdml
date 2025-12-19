# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.contrib import messages
from django.urls import reverse
from .models import DataCiteConfiguration
from django.utils.html import format_html
from django.core.exceptions import MultipleObjectsReturned


def doimanager(request):
    datacite_configuration_meta = DataCiteConfiguration._meta

    try:
        datacite_configuration = DataCiteConfiguration.objects.get(is_active=True)

        if datacite_configuration.datacite_instance == DataCiteConfiguration.DataCiteInstance.TEST:
            messages.warning(
                request,
                format_html(
                    'The DataCite configuration is set to the TEST instance. DOIs will not be registered with the production DataCite service. Setup and/or activate a PRODUCTION instance: <a href="{}">{} > {} > {}</a>.',
                    reverse("admin:doimanager_dataciteconfiguration_changelist"),
                    "Home",
                    datacite_configuration_meta.app_config.verbose_name,
                    datacite_configuration_meta.verbose_name,
                ),
            )

    except MultipleObjectsReturned:
        messages.error(
            request,
            format_html(
                'Multiple active DataCiteConfiguration instances found. Please ensure only one is active: <a href="{}">{} > {} > {}</a>.',
                reverse("admin:doimanager_dataciteconfiguration_changelist"),
                "Home",
                datacite_configuration_meta.app_config.verbose_name,
                datacite_configuration_meta.verbose_name,
            ),
        )
    except DataCiteConfiguration.DoesNotExist:
        messages.warning(
            request,
            format_html(
                'No active DataCiteConfiguration configuration found. To assign or update DOIs, create one: <a href="{}">{} > {} > {}</a>.',
                reverse("admin:doimanager_dataciteconfiguration_add"),
                "Home",
                datacite_configuration_meta.app_config.verbose_name,
                datacite_configuration_meta.verbose_name,
            ),
        )

    return {}
