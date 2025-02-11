# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from rdml.doimanager.datacite.rest_client import DataCiteRESTClient
from .models import (
    Resource,
    CreatorPerson,
    ContributorPerson,
    ContributionPosition,
    ResearchResource,
    RelatedResource,
    FileInfo,
)


@admin.register(RelatedResource)
class RelatedResourceAdmin(admin.ModelAdmin):
    pass


@admin.register(ContributionPosition)
class ContributionPositionAdmin(admin.ModelAdmin):
    search_fields = ["contribution_position"]


@admin.register(ContributorPerson)
class ContributorPersonAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        """
        Hide this model from django admin app list but keep edit and add
        functionality from related model admins alive.
        """
        return False


# class ContributorPersonInline(admin.TabularInline):
#     model = ContributorPerson
#     # fk_name = "related_resource"
#     extra = 0
#     classes = ["collapse"]


# class ContactPersonInline(admin.TabularInline):
#     model = Resource.contact_persons.through
#     extra = 0
#     classes = ["collapse"]
#     verbose_name = "Contact person"
#     verbose_name_plural = "Contact persons"


@admin.register(FileInfo)
class FileInfoAdmin(admin.ModelAdmin):
    pass


class FileInfoInline(admin.StackedInline):
    model = FileInfo
    extra = 0
    classes = ["collapse"]
    verbose_name = "Data files description"


class CreatorPersonInline(admin.StackedInline):
    model = CreatorPerson
    # fk_name = "related_resource"
    extra = 0
    classes = ["collapse"]
    autocomplete_fields = ["contribution_position"]


class RelatedResourceInline(admin.TabularInline):
    model = RelatedResource
    fk_name = "parent_resource"
    extra = 0
    classes = ["collapse"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Exclude parent object from selectable child objects.
        https://stackoverflow.com/questions/21337142/django-admin-inlines-get-object-from-formfield-for-foreignkey
        """
        if db_field.name == "child_resource":
            try:
                parent_id = request.resolver_match.kwargs.get("object_id")
                kwargs["queryset"] = Resource.objects.exclude(pk=parent_id)
            except IndexError:
                pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class HasDoiListFilter(admin.SimpleListFilter):
    title = _("has DOI")
    parameter_name = "has_doi"

    def lookups(self, request, model_admin):
        return (
            ("True", _("True")),
            ("False", _("False")),
        )

    def queryset(self, request, queryset):
        if self.value() == "False":
            return queryset.filter(dataciteresource__doi__exact=None)
        elif self.value() == "True":
            return queryset.exclude(dataciteresource__doi__exact=None)
        else:
            return queryset


# class ResourceAdminForm(forms.ModelForm):
#     class Meta:
#         fields = ('cv_subject_areas',)
#         widgets = {
#             'cv_subject_areas': AutocompleteSelectMultiple(
#                 Resource.cv_subject_areas.field,
#                 admin.site,
#                 attrs={'data-dropdown-auto-width': 'true'}
#             ),
#         }


class ResourceBaseAdmin(admin.ModelAdmin):
    save_on_top = False
    # form = ResourceAdminForm
    change_form_template = "research/admin/change_form.html"

    list_display = [
        "slug",
        "title_en",
        "get_organizational_unit",
        "get_year_start",
        "get_year_completed",
        "get_resource_type",
        "get_doi",
        "is_public",
    ]

    inlines = [
        FileInfoInline,
        CreatorPersonInline,
        # ContributorPersonInline,
        # ContactPersonInline,
        RelatedResourceInline,
    ]

    list_filter = [
        "organizational_unit",
        HasDoiListFilter,
        # 'cv_subject_areas',
        # 'keywords',
        "is_public",
        "datacite_resource_type_general",
        "updated",
    ]

    search_fields = [
        "title_en",
        "title_de",
        "abstract_en",
        "abstract_de",
        "datacite_resource_type",
    ]

    autocomplete_fields = [
        "curators",
        "keywords",
        "cv_geographic_areas",
        "research_funding_agency",
        "cv_mode_of_collection",
        "cv_time_dimension",
        "cv_sampling_procedure",
    ]

    filter_horizontal = ("cv_subject_areas",)

    exclude = ("contact_persons",)

    _readonly_fields = []
    readonly_fields = ("get_doi",)

    def get_readonly_fields(self, request, obj=None):
        """Allow subclasses to define _readonly_fields."""
        readonly_fields = (
            *self.readonly_fields,
            *self._readonly_fields,
        )
        return readonly_fields

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title_en",
                    "title_de",
                    "slug",
                    "get_doi",
                    ("date_start", "date_completed"),
                    (
                        "publisher",
                        "organizational_unit",
                    ),
                    "language",
                    "website",
                )
            },
        ),
        (
            "WORKFLOW",
            {
                "classes": ("collapse",),
                "fields": (
                    "curators",
                    "is_public",
                    ("datacite_resource_type_general", "datacite_resource_type"),
                ),
            },
        ),
        (
            "DESCRIPTIONS",
            {
                "classes": ("collapse",),
                "fields": (
                    "abstract_en",
                    "abstract_de",
                    "cv_subject_areas",
                    "keywords",
                ),
            },
        ),
        (
            "LEGAL ASPECTS",
            {
                "classes": ("collapse",),
                "fields": (
                    "data_protection_concept",
                    "sensitive_information",
                    "ethical_approval",
                    "research_funding_agency",
                    "research_funding_grant_id",
                    "preregistration",
                ),
            },
        ),
        (
            "GEOGRAPHIC AREA",
            {
                "classes": ("collapse",),
                "fields": (
                    "cv_geographic_areas",
                    "geographic_area_specified",
                ),
            },
        ),
        (
            "METHODS",
            {
                "classes": ("collapse",),
                "fields": (
                    "cv_time_dimension",
                    "time_dimension_specified",
                    ("data_collection_start_at", "data_collection_end_at"),
                    "population_universe",
                    "cv_sampling_procedure",
                    "sampling_procedure_specified",
                    "sample_size",
                    "sample_size_specified",
                    "cv_mode_of_collection",
                    "mode_of_collection_specified",
                ),
            },
        ),
        (
            "ARCHIVING & ACCESS",
            {
                "classes": ("collapse",),
                "fields": (
                    "archiving_access_availability",
                    "archiving_access_embargo_until",
                    "archiving_access_license",
                    "archiving_access_remarks",
                    "archiving_access_publications",
                    "study_documentation",
                ),
            },
        ),
    )

    # @admin.display(description='Identifiers')
    # def get_identifiers(self, obj):
    #     if obj.identifiers.all():
    #         identifiers = list(obj.identifiers.values_list("identifier", flat=True))
    #         return format_html_join(
    #             '',
    #             '<code style="font-size: smaller; border: 1px solid gray; border-radius: 5px; padding: 1px 3px; white-space: nowrap;">{}</code><br style="margin: 3px;">',
    #             ((i,) for i in identifiers)
    #         )

    @admin.display(description="Type")
    def get_resource_type(self, obj):
        return format_html(
            "{}/<br>{}", obj.get_datacite_resource_type_general_display(), f"{obj.datacite_resource_type or 'unset'}"
        )

    @admin.display(description="OU")
    def get_organizational_unit(self, obj):
        if obj.organizational_unit.abbr:
            return format_html(
                '<span title="{title}">{abbr}</span>',
                title=obj.organizational_unit,
                abbr=obj.organizational_unit.abbr,
            )
        else:
            return obj.organizational_unit

    @admin.display(description="DOI")
    def get_doi(self, obj):
        if obj.dataciteresource.doi:
            doi_img_url = static("img/doi-logo.svg")
            datacite_doi_state, datacite_found = DataCiteRESTClient().get_datacite_doi_state(
                doi=obj.dataciteresource.doi
            )

            return format_html(f'''
                <span style="
                    background-color: var(--object-tools-hover-bg); 
                    border-radius: 10px;
                    font-size: smaller;
                    color: white;
                    padding: 2px 4px;
                    white-space: nowrap;
                    display: block; 
                    text-align: center;
                ">
                    <img style="margin-right: 5px; height: 1.2em;" src="{doi_img_url}">
                    <span style="background-color: #e0a800;
                        border-radius: 10px;
                        font-size: smaller;
                        color: black;
                        padding: 1px 2px;
                        margin: 0 4px;
                    ">
                        {datacite_doi_state.title()}
                    </span>
                    <br>
                    {obj.dataciteresource.doi}
                </span>
            ''')

    def get_year_start(self, obj):
        if obj.date_start:
            return f"{obj.date_start:%Y}"

    get_year_start.short_description = "Started"
    get_year_start.admin_order_field = "date_start"

    def get_year_completed(self, obj):
        if obj.date_completed:
            return f"{obj.date_completed:%Y}"

    get_year_completed.short_description = "Completed"
    get_year_completed.admin_order_field = "date_completed"

    def has_change_permission(self, request, obj=None):
        if obj:
            if any(
                [
                    request.user.is_superuser,
                    settings.RDML_ADMIN_GROUP in request.user.groups.values_list("name", flat=True),
                    request.user in obj.curators.all(),
                ]
            ):
                return True

    def has_delete_permission(self, request, obj=None):
        if obj and request.user.is_superuser:
            return True

    class Media:
        css = {"all": ("research/admin/research_admin.css",)}


# @admin.register(Project)
# class ProjectAdmin(ResourceBaseAdmin):
#     _readonly_fields = (
#         'resource_type',
#     )
#     # def get_form(self, request, obj=None, **kwargs):
#     #     form = super().get_form(request, obj, **kwargs)
#     #     form.base_fields['resource_type'] = 'Dataset'
#     #     return form


@admin.register(ResearchResource)
class ResourceAdmin(ResourceBaseAdmin):
    pass

    # def formfield_for_choice_field(self, db_field, request, **kwargs):
    #     if db_field.name == "resource_type":
    #         choices = db_field.get_choices()
    #         to_remove = (Resource.ResourceType.PROJECT.value, Resource.ResourceType.PROJECT.label)
    #         choices.remove(to_remove)
    #         kwargs['choices'] = choices
    #     return super().formfield_for_choice_field(db_field, request, **kwargs)
