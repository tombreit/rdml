# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.contrib import admin

from .models import (
    CVClassificationKeyword,
    CVSubjectArea,
    CVGeographicArea,
    CVModeOfCollection,
    CVSamplingProcedure,
    CVTimeDimension,
    # CVDataProtectionConcept,
    CVResearchFundingAgency,
    CVArchivingAccessAvailability,
    Filetype,
)


class ClassificationBaseAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "name_en",
        "name_de",
    ]

    search_fields = [
        "name_en",
        "name_de",
        "definition",
    ]

    prepopulated_fields = {"slug": ("name_en", "name_de")}

    list_per_page = 999999

    class Meta:
        abstract = True


class CVGesisBaseAdmin(ClassificationBaseAdmin):
    list_display = [
        "get_code",
        "name_en",
        "name_de",
    ]
    readonly_fields = [
        "position",
    ]

    @admin.display(
        description="Code",
        ordering="position",
    )
    def get_code(self, obj):
        return obj.code

    class Meta:
        abstract = True


@admin.register(CVGeographicArea)
class CVGeographicAreaAdmin(admin.ModelAdmin):
    list_display = [
        "country_code",
        "country_name",
        "subdivision_code",
        "subdivision_name",
        "subdivision_type",
    ]

    search_fields = [
        "country_code",
        "country_name",
        "subdivision_code",
        "subdivision_name",
    ]


@admin.register(CVSubjectArea)
class CVSubjectAreaAdmin(ClassificationBaseAdmin):
    pass


@admin.register(CVModeOfCollection)
class CVModeOfCollectionAdmin(CVGesisBaseAdmin):
    pass


@admin.register(CVSamplingProcedure)
class CVSamplingProcedureAdmin(CVGesisBaseAdmin):
    pass


@admin.register(CVTimeDimension)
class CVTimeDimensionAdmin(CVGesisBaseAdmin):
    pass


# @admin.register(CVDataProtectionConcept)
# class CVDataProtectionConceptAdmin(ClassificationBaseAdmin):
#     pass


@admin.register(CVResearchFundingAgency)
class CVResearchFundingAgencyAdmin(ClassificationBaseAdmin):
    pass


@admin.register(CVClassificationKeyword)
class CVClassificationKeywordAdmin(admin.ModelAdmin):
    list_display = [
        "name_en",
        "name_de",
    ]

    search_fields = [
        "name_en",
        "name_de",
        "definition",
    ]

    prepopulated_fields = {"slug": ("name_en",)}

    list_per_page = 999999


@admin.register(CVArchivingAccessAvailability)
class CVArchivingAccessAvailabilityAdmin(ClassificationBaseAdmin):
    pass


@admin.register(Filetype)
class FiletypeAdmin(admin.ModelAdmin):
    pass
