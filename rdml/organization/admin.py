# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.contrib import admin
from .models import Organization, OrganizationalUnit, Person, Branding


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "abbr",
        "slug",
    ]
    search_fields = [
        "name",
        "slug",
        "abbr",
    ]

    prepopulated_fields = {"slug": ("name",)}


@admin.register(OrganizationalUnit)
class OrganizationalUnitAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "abbr",
        "url",
    ]

    prepopulated_fields = {"slug": ("name",)}


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = [
        "last_name",
        "first_name",
        "email",
        "name_slug",
    ]

    search_fields = [
        "last_name",
        "first_name",
        "email",
    ]

    prepopulated_fields = {"name_slug": ("last_name", "first_name")}


# @admin.register(Publisher)
# class PublisherAdmin(admin.ModelAdmin):
#     list_display = [
#         "name_en",
#         "abbr_en",
#     ]


@admin.register(Branding)
class BrandingAdmin(admin.ModelAdmin):
    pass
