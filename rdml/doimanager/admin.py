# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import json
from django.contrib import admin

from .models import DataCiteResource, DataCiteConfiguration
from ..core.helpers import json_html_highlighter


@admin.register(DataCiteResource)
class DataCiteResourceAdmin(admin.ModelAdmin):
    save_on_top = False
    # change_form_template = "doimanager/admin/change_form.html"

    readonly_fields = [
        "citation_snippet",
        # 'doi',
        "created",
        "updated",
    ]

    def get_list_display(self, request):
        """
        Return a sequence containing the fields to be displayed on the
        changelist.
        """
        res = self.list_display
        print(f"{res=}")
        return res

    list_display = [
        "__str__",
        "created",
        "updated",
    ]
    # fieldsets = (
    #     ('READONLY', {
    #         'classes': ('collapse',),
    #         'fields': (
    #             'citation_snippet',
    #             'datacite_history_formatted',
    #         ),
    #     }),
    # )

    @admin.display(description="DataCite Response History")
    def datacite_history_formatted(self, instance):
        """Function to display pretty version of our data"""
        json_data = json.dumps(instance.datacite_history, sort_keys=True, indent=2)
        return json_html_highlighter(json_data)

    def response_change(self, request, obj):
        # if "_datacite_handler" in request.POST:
        #     res = DataCite(obj.id, obj.doi)
        #     res = res.manage_doi()
        #     obj.save()
        #     self.message_user(request, f"Successfully registered DOI ")
        #     return HttpResponseRedirect(".")
        return super().response_change(request, obj)


@admin.register(DataCiteConfiguration)
class DataCiteConfigurationAdmin(admin.ModelAdmin):
    pass
