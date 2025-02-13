# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import re

from django.db import models
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from ..core.models import TimeStampedBaseModel, UUIDBaseModel, SingletonBaseModel


def validate_coneid(value):
    CONEID_REGEX = r"^persons\d{6}$"
    regex = re.compile(CONEID_REGEX, re.IGNORECASE)
    if not regex.match(value):
        raise ValidationError('PuRe person CoNE ID does not match format "persons123456"')


def validate_orcid(value):
    """
    Ref: https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier
    """
    ORCID_REGEX = r"^https://orcid.org/\d{4}-\d{4}-\d{4}-\d{4}$"
    regex = re.compile(ORCID_REGEX, re.IGNORECASE)
    if not regex.match(value):
        raise ValidationError('ORCID does not match format "https://orcid.org/xxxx-xxxx-xxxx-xxxx"')


class OrganizationBaseModel(TimeStampedBaseModel, UUIDBaseModel):
    class Meta:
        abstract = True


class Organization(OrganizationBaseModel):
    name = models.CharField(
        max_length=255,
        blank=False,
    )
    slug = models.SlugField(
        max_length=255,
        allow_unicode=False,
        null=True,
        unique=True,
    )
    abbr = models.CharField(
        max_length=255,
        blank=True,
        help_text="Abbreviation for this Organization",
    )
    url = models.URLField(
        blank=True,
    )
    ror_id = models.CharField(
        max_length=255,
        blank=True,
    )

    def __str__(self):
        return self.name


class OrganizationalUnit(OrganizationBaseModel):
    name = models.CharField(
        max_length=255,
        blank=False,
    )
    slug = models.SlugField(
        max_length=255,
        allow_unicode=False,
        null=True,
        unique=True,
    )
    abbr = models.CharField(
        max_length=255,
        blank=True,
        help_text="Abbreviation for this Organizational Unit.",
    )
    url = models.URLField(
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="unique_ou_name",
            ),
            models.UniqueConstraint(
                Lower("slug"),
                name="unique_ou_slug",
            ),
        ]


class Person(OrganizationBaseModel):
    first_name = models.CharField(
        max_length=255,
        blank=False,
    )
    last_name = models.CharField(
        max_length=255,
        blank=False,
    )
    name_slug = models.SlugField(
        max_length=255,
        allow_unicode=False,
        unique=True,
        null=True,
    )
    email = models.EmailField(
        blank=True,
        null=True,
        unique=True,
    )
    organization = models.ForeignKey(
        "organization.Organization",
        blank=False,
        null=True,
        on_delete=models.PROTECT,
    )
    cone_id = models.CharField(
        max_length=13,
        blank=True,
        null=True,
        verbose_name="PuRe person CoNE ID",
        help_text="PuRe Person CoNE ID, eg: `persons123456`",
        validators=[validate_coneid],
    )
    orcid_id = models.URLField(
        blank=True,
        null=True,
        verbose_name="ORCID ID",
        help_text="Format: full https URI: https://orcid.org/xxxx-xxxx-xxxx-xxxx, complete with the protocol (https://), and with hyphens in the identifier (xxxx-xxxx-xxxx-xxxx).",
        validators=[validate_orcid],
    )
    gnd_id = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="GND ID",
        help_text="Gemeinsame Normdatei, eg: `13015461X`",
        # TODO: Validator https://de.wikipedia.org/wiki/Gemeinsame_Normdatei#Entit%C3%A4tsidentifikator
    )

    @property
    def get_full_name(self):
        return f"{self.last_name}, {self.first_name}"

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="unique_email",
            ),
            models.UniqueConstraint(
                fields=("first_name", "last_name"),
                name="unique_name",
            ),
            models.UniqueConstraint(
                Lower("cone_id"),
                name="unique_coneid",
            ),
            models.UniqueConstraint(
                Lower("orcid_id"),
                name="unique_orcid",
            ),
        ]


class Publisher(OrganizationBaseModel):
    name_en = models.CharField(
        max_length=255,
        blank=False,
        help_text="The name of the entity that holds, archives, publishes prints, distributes, releases, issues, or produces the resource.",
    )
    abbr_en = models.CharField(
        max_length=255,
        blank=True,
        help_text="Abbreviation for this publisher",
    )
    url = models.URLField(
        blank=True,
    )
    ror_id = models.CharField(
        max_length=255,
        blank=True,
    )

    def __str__(self):
        return f"{self.name_en}"


class Branding(SingletonBaseModel):
    organization_name = models.CharField(
        max_length=255,
        blank=False,
        default="ACME Institute",
    )
    organization_abbr = models.CharField(
        max_length=255,
        blank=False,
        default="ACME",
        verbose_name="Organization abbreviation",
    )
    organization_logo = models.FileField(
        null=True,
        blank=True,
        upload_to="branding/",
        validators=[FileExtensionValidator(["svg"])],
        verbose_name="Logo file",
        help_text="Logo file (SVG)",
    )
    organization_figurative_mark = models.FileField(
        null=True,
        blank=True,
        upload_to="branding/",
        validators=[FileExtensionValidator(["svg"])],
        verbose_name='Figurative Mark/"Bildmarke"',
    )
    organization_affiliation = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Affiliation",
        help_text="E.g. the name of a higher-level institution. Displayed in the footer of the website.",
    )

    def __str__(self):
        return "Branding configuration"

    class Meta:
        verbose_name = "Branding"
        verbose_name_plural = "Branding"
