# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import uuid
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from ...doimanager.models import DataCiteContributorType, DataCiteResourceTypeGeneral
from ...classification.models import License
from ...core.models import TimeStampedBaseModel, UUIDBaseModel
from ...core.helpers import get_countries_as_choices


class ResourceBaseModel(TimeStampedBaseModel, UUIDBaseModel):
    class Meta:
        abstract = True


class ContributionPosition(ResourceBaseModel):
    name = models.CharField(
        max_length=255,
        blank=False,
        unique=True,
    )
    weight = models.PositiveIntegerField(
        help_text="Ordering for displaying the positions. High values -> high order.",
        default=500,
    )

    def __str__(self):
        return f"{self.name} (weight: {self.weight})"

    class Meta:
        ordering = ["-weight"]


class ContributionBase(ResourceBaseModel):
    person = models.ForeignKey(
        "organization.Person",
        on_delete=models.CASCADE,
    )
    resource = models.ForeignKey(
        "research.Resource",
        on_delete=models.CASCADE,
    )
    person_organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    contribution_start_date = models.DateField(blank=True, null=True)
    contribution_end_date = models.DateField(blank=True, null=True)

    def clean(self):
        # Don't allow start dates before end dates
        if self.contribution_start_date and self.contribution_end_date:
            if self.contribution_start_date > self.contribution_end_date:
                msg = _("The start date cannot be earlier than the end date.")
                raise ValidationError({"contribution_start_date": msg, "contribution_end_date": msg})

    class Meta:
        abstract = True


class ContributorPerson(ContributionBase):
    datacite_contributor_type = models.CharField(
        max_length=50,
        choices=DataCiteContributorType.choices,
        default=DataCiteContributorType.ContactPerson,
        help_text="DataCite Metadata 7.a",
    )

    def __str__(self):
        return f"{self.person} ({self.datacite_contributor_type}) → {self.resource}"

    class Meta:
        verbose_name = "Contributor"
        verbose_name_plural = "Contributors"
        ordering = ["person__last_name"]


class CreatorPerson(ContributionBase):
    contribution_position = models.ForeignKey(
        "research.ContributionPosition",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
    )
    datacite_contributor_type = models.CharField(
        max_length=50,
        choices=DataCiteContributorType.choices,
        default=DataCiteContributorType.ContactPerson,
        help_text="DataCite Metadata 7.a",
    )

    def __str__(self):
        return f"{self.person} ({self.contribution_position}) → {self.resource}"

    class Meta:
        verbose_name = "Creator"
        verbose_name_plural = "Creators"
        ordering = ["-contribution_position__weight", "person__last_name"]


class FileInfo(ResourceBaseModel):
    resource = models.ForeignKey(
        "research.Resource",
        null=True,
        on_delete=models.CASCADE,
    )
    filename = models.CharField(
        max_length=255,
        blank=False,
        help_text="File name. Exactly as stored in archive.",
    )
    filesize = models.FloatField(
        blank=True,
        null=True,
        help_text="Filesize in MB (Megabytes)",
    )
    filetype = models.ForeignKey(
        "classification.Filetype",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        help_text="E.g. DTA (Stata data file), CSV, MP3, etc.",
    )
    special_file_format = models.TextField(
        blank=True,
        help_text="Only if not standard format (line=case/column=variable), information on data structure (e.g. in longitudinal data: long/wide format; relational (n:m)/multilevel data, etc.)",
    )
    description = models.TextField(
        blank=True,
        help_text="Short characterization of data, additional information",
    )
    internal_version_date = models.DateField(
        blank=True,
        null=True,
    )
    language = models.CharField(
        max_length=2,
        blank=True,
        choices=get_countries_as_choices(),
        default="en",
        help_text="Text language (content or labels, e.g. English)",
    )
    number_of_variables = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    number_of_cases = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    # TODO: type of units	Art Erhebungseinheit	specify the type of units (e.g. respondents, aggregate units, …)
    weighting_concept = models.TextField(
        blank=True,
        help_text="Brief description of weighting concept",
    )
    weighting_variable = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of weigthting variable",
    )
    id_variable = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of variable which contains unique (personal) identifier to potentially link data to external information.",
    )
    sensitive_variables = models.TextField(
        blank=True,
        help_text="Variables presenting data protecting risks (i.e. for potential re-identification), with explanations.",
    )
    anonymization_procedures = models.TextField(
        blank=True,
        help_text="Pseudo-/Anonymisierungsverfahren. Description of strategies to remove or defuse sensitive personal information.",
    )

    def __str__(self):
        return f"{self.filename}"

    class Meta:
        verbose_name = "File information"
        verbose_name_plural = "Files information"


class RelatedResource(ResourceBaseModel):
    class RelationType(models.TextChoices):
        """
        https://support.datacite.org/docs/datacite-metadata-schema-v44-recommended-and-optional-properties#12b-relationtype
        Currently: IsCitedBy, Cites, IsSupplementTo, IsSupplementedBy, IsPartOf, HasPart
        More types available at above mentioned URL.
        """

        IsCitedBy = "IsCitedBy", "IsCitedBy"
        Cites = "Cites", "Cites"
        IsSupplementTo = "IsSupplementTo", "IsSupplementTo"
        IsPartOf = "IsPartOf", "IsPartOf"
        HasPart = "HasPart", "HasPart"

    parent_resource = models.ForeignKey(
        "research.Resource",
        on_delete=models.RESTRICT,
    )
    child_resource = models.ForeignKey(
        "research.Resource",
        on_delete=models.RESTRICT,
        related_name="related_resources",
    )
    relation_type = models.CharField(
        max_length=255,
        choices=RelationType.choices,
        default=RelationType.IsPartOf,
    )

    def __str__(self):
        return f"{self.parent_resource} → {self.relation_type} →  {self.child_resource}"


class PublicResourceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_public=True)


class Resource(ResourceBaseModel):
    objects = models.Manager()
    public_objects = PublicResourceManager()

    # class ResourceType(models.TextChoices):
    #     """
    #     Upstream Datacite: A description of the resource
    #     https://schema.datacite.org/meta/kernel-4.4/doc/DataCite-MetadataKernel_v4.4.pdf#page=16
    #     """
    #     PROJECT = 'PRJ', _('Project')
    #     DATASET = 'DTS', _('Dataset')

    child_resources = models.ManyToManyField(
        "self",
        through="research.RelatedResource",
    )

    curators = models.ManyToManyField(
        "accounts.customuser",
        blank=True,
        help_text="Data curators are the people within the research project who are responsible for maintaining and managing the metadata. There is usually only one, but there may be more.",
    )

    is_public = models.BooleanField(
        default=False,
        help_text="If false (e.g. within an embargo period), this object will not be published.",
    )

    datacite_resource_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="DataCite ResourceType",
        help_text="DataCite Metadata 10. The recommended content is a \
                   single term of some detail so \
                   that a pair can be formed with the resourceTypeGeneral \
                   subproperty. For example, a resourceType of “Census Data” \
                   paired with a resourceTypeGeneral of “Dataset” yields \
                   “Dataset/Census Data”.",
    )
    datacite_resource_type_general = models.CharField(
        max_length=50,
        blank=True,
        choices=DataCiteResourceTypeGeneral.choices,
        default=DataCiteResourceTypeGeneral.Dataset,
        verbose_name="DataCite ResourceTypeGeneral",
        help_text="DataCite Metadata 10.a. Default value is `Dataset`",
    )

    # https://blog.datacite.org/cool-dois/
    slug = models.SlugField(
        unique=True,
        max_length=255,
        allow_unicode=False,
        null=False,
        blank=False,
        default=uuid.uuid4,
        help_text="Short, `speaking`, unique identfier.",
    )

    # Multilanguage Fields
    title_en = models.CharField(
        max_length=255,
        blank=False,
        verbose_name="Title (EN)",
    )
    title_de = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Title (DE)",
    )
    abstract_en = models.TextField(
        blank=True,
        verbose_name="Abstract (EN)",
    )
    abstract_de = models.TextField(
        blank=True,
        verbose_name="Abstract (DE)",
    )

    organizational_unit = models.ForeignKey(
        "organization.OrganizationalUnit",
        blank=False,
        null=True,
        on_delete=models.PROTECT,
    )
    publisher = models.ForeignKey(
        "organization.Organization",
        blank=False,
        null=True,
        on_delete=models.PROTECT,
    )
    language = models.CharField(
        max_length=2,
        choices=get_countries_as_choices(),
        default="de",
        help_text="The primary language of the resource",
    )
    creators = models.ManyToManyField(
        "organization.Person",
        through="research.CreatorPerson",
        related_name="creator_persons",
    )
    contributors = models.ManyToManyField(
        "organization.Person",
        through="research.ContributorPerson",
        related_name="contributor_persons",
    )
    # contact_persons = models.ManyToManyField(
    #     "organization.Person",
    #     through="research.ContactPerson",
    #     related_name="contact_persons",
    # )
    website = models.URLField(
        blank=True,
        verbose_name="Project website",
    )
    date_start = models.DateField(
        blank=True,
        null=True,
        help_text="Date the project has been started. Only the year component will be listed publicly.",
    )
    date_completed = models.DateField(
        blank=True,
        null=True,
        help_text="Date the project has been completed. Only the year component will be listed publicly.",
    )

    #
    # Subject of research
    #

    cv_subject_areas = models.ManyToManyField(
        "classification.CVSubjectArea",
        verbose_name="Area of Research (CV)",
        blank=True,
        help_text="Controlled vocabulary. Choose from list.",
    )
    keywords = models.ManyToManyField(
        "classification.CVClassificationKeyword",
        blank=True,
        help_text="You may choose from existing list of keywords or add new keywords",
    )

    #
    # Legal aspects
    #

    data_protection_concept = models.TextField(
        blank=True,
        verbose_name="Data Protection Concept",
        help_text="Description of the legal basis and measures of data protection (e.g. 'informed consent')",
    )
    sensitive_information = models.TextField(
        blank=True,
        help_text="Elements of data which contain sensitive personal data",
    )
    ethical_approval = models.CharField(
        max_length=255,
        blank=True,
        help_text="Approval by ethics board. Name of ethics board/committee. Leave empty if none.",
    )
    preregistration = models.URLField(
        blank=True,
        help_text="Information on preregistration if applicapble. Please provide an URL.",
    )
    research_funding_agency = models.ManyToManyField(
        "classification.CVResearchFundingAgency",
        blank=True,
    )
    research_funding_grant_id = models.CharField(
        max_length=255, blank=True, help_text="Funding grant ID and/or number."
    )

    #
    # Methods
    #

    cv_time_dimension = models.ManyToManyField(
        "classification.CVTimeDimension",
        blank=True,
        verbose_name="Time Dimension (CV)",
        help_text="Controlled vocabulary. Choose from list.",
    )
    time_dimension_specified = models.TextField(
        blank=True,
        help_text="Additional or other information on time method/research design",
    )
    population_universe = models.CharField(
        max_length=255,
        blank=True,
        help_text="Description of the population from which the sample is drawn",
    )
    cv_sampling_procedure = models.ManyToManyField(
        "classification.CVSamplingProcedure",
        blank=True,
        verbose_name="Sampling Procedure (CV)",
        help_text="Controlled vocabulary. Choose from list.",
    )
    sampling_procedure_specified = models.TextField(
        blank=True,
        help_text="Additional, detailed information about sampling procedure",
    )
    cv_mode_of_collection = models.ManyToManyField(
        "classification.CVModeOfCollection",
        blank=True,
        verbose_name="Mode of Collection (CV)",
        help_text="Controlled vocabulary. Choose from list.",
    )
    mode_of_collection_specified = models.TextField(
        blank=True,
        help_text="Additional, detailed information about mode of data collection",
    )
    sample_size = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Sample size",
        help_text="Additional, detailed information about sample size",
    )
    sample_size_specified = models.TextField(
        blank=True,
        help_text="Detailed information about the corresponding classification field.",
    )
    data_collection_start_at = models.DateField(
        blank=True,
        null=True,
        verbose_name="Start of data collection",
        help_text="'day' currently not evaluated: select first of respective month.",
    )
    data_collection_end_at = models.DateField(
        blank=True,
        null=True,
        verbose_name="End of data collection",
        help_text="'day' currently not evaluated: select first of respective month.",
    )

    #
    # Geographic area
    #

    cv_geographic_areas = models.ManyToManyField(
        "classification.CVGeographicArea",
        blank=True,
        help_text="Geographic areas as ISO-3166-1 and ISO-3166-2. To select area type country name (English).",
        verbose_name="Geographic Area (ISO, CV)",
    )
    geographic_area_specified = models.TextField(
        blank=True,
        help_text="Additional or other information on geographic area not covered by ISO",
    )

    #
    # archiving_access
    #

    archiving_access_availability = models.ForeignKey(
        "classification.CVArchivingAccessAvailability",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        help_text="Availability class of dataset",
        verbose_name="Availability",
    )
    archiving_access_embargo_until = models.DateField(
        null=True,
        blank=True,
        verbose_name="Embargo (until)",
        help_text="Embargoed until (exact date needed)",
    )
    archiving_access_license = models.CharField(
        max_length=255,
        blank=True,
        choices=License,
        verbose_name="License",
    )
    archiving_access_remarks = models.TextField(
        blank=True,
        help_text="Additional information about the project not specified elsewhere",
        verbose_name="Remarks",
    )
    archiving_access_publications = models.TextField(
        blank=True,
        help_text="Publications in relation to this project (free text; sample of key publications only)",
        verbose_name="Publications",
    )
    study_documentation = models.TextField(
        blank=True,
        help_text="List of existing documents relating to: Technical reports, protocols, questionnaires, legal documents (data protection, ethics  approval, funding applicatons, cooperation agreements, ...)",
        verbose_name="Study documentation",
    )

    # file_information = models.ManyToManyField(
    #     "research.FileInfo",
    #     blank=True,
    #     related_name="related_fileinformation",
    #     # null=True,
    #     # on_delete=models.PROTECT,
    #     help_text="Use only for files containing the actual research data, not for auxiliary or metadata files.",
    # )

    @property
    def get_data_collection_duration_weeks(self):
        if self.data_collection_start_at and self.data_collection_end_at:
            day_diff = self.data_collection_end_at - self.data_collection_start_at
            weeks = day_diff.days // 7
            return weeks

    def clean(self):
        # Don't allow start dates before end dates
        if self.date_start and self.date_completed:
            if self.date_start > self.date_completed:
                msg = _("The start date cannot be earlier than the end date.")
                raise ValidationError({"date_start": msg, "date_completed": msg})

    def get_proxyadmin_change_url(self):
        """
        Returns the admin change url. Whenever this method is called on a concrete
        proxy model it returns the change url of this proxy model.
        """
        # print(f"{self._meta.label_lower=}")
        # print(f"{self._meta.model.__name__.lower()=}")

        label = "research_researchresource"
        # if self.resource_type == Resource.ResourceType.PROJECT.value:
        #     label = "research_project"

        return reverse("admin:{label}_change".format(label=label), args=[self.id])

    def __str__(self):
        return f"{self.slug}: {self.title_en}"

    class Meta:
        verbose_name = "Research resource"
        verbose_name_plural = "Research resources"
        constraints = [
            models.UniqueConstraint(
                Lower("slug"),
                name="unique_lower_slug",
                violation_error_message="A research resource with this slug already exists. This validation is case-insensitive.",
            ),
            models.UniqueConstraint(
                Lower("title_en"),
                name="unique_lower_title_en",
                violation_error_message="A research resource with this title (EN) already exists. This validation is case-insensitive.",
                condition=~Q(title_en=""),
            ),
            models.UniqueConstraint(
                Lower("title_de"),
                name="unique_lower_title_de",
                violation_error_message="A research resource with this title (DE) already exists. This validation is case-insensitive.",
                condition=~Q(title_de=""),
            ),
        ]
