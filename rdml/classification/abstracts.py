# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

from django.db import models
from django.db.models.functions import Cast
from django.db.models.functions import LPad
from django.db.models import Value
from django.db.models.functions import Replace
from ..core.models import TimeStampedBaseModel, UUIDBaseModel
from ..core.helpers import get_orderable_representation


class CVKeywordBaseModel(TimeStampedBaseModel, UUIDBaseModel):
    name_en = models.CharField(
        max_length=255,
        blank=False,
    )
    name_de = models.CharField(
        max_length=255,
        blank=True,
    )
    slug = models.SlugField(
        max_length=255,
        allow_unicode=False,
        unique=True,
        null=True,
    )
    definition = models.TextField(
        blank=True,
        help_text="Definition of the Code. See for example https://ddialliance.org/Specification/DDI-CV/ModeOfCollection_3.0.html",
    )

    def __str__(self):
        return f"{self.name_en}"

    class Meta:
        abstract = True
        ordering = ["name_en"]


class CVBaseModel(TimeStampedBaseModel, UUIDBaseModel):
    name_en = models.CharField(
        max_length=255,
        blank=False,
    )
    name_de = models.CharField(
        max_length=255,
        blank=True,
    )
    slug = models.SlugField(
        max_length=255,
        allow_unicode=False,
        unique=True,
        null=True,
    )
    code = models.CharField(
        max_length=255,
        blank=True,
        help_text="Value of the Code. Example https://ddialliance.org/controlled-vocabularies",
    )
    definition = models.TextField(
        blank=True,
        help_text="Definition of the Code. Example https://ddialliance.org/controlled-vocabularies",
    )

    def __str__(self):
        return f"{self.name_en}"

    class Meta:
        abstract = True
        ordering = [
            "code",
            "name_en",
        ]


class CVGesisBaseModel(CVBaseModel):
    position = models.CharField(
        max_length=255,
        blank=True,
    )

    def clean(self):
        if self.code:
            self.position = get_orderable_representation(self.code)

    def __str__(self):
        return f"{self.code}: {self.name_en}"

    class Meta(CVBaseModel.Meta):
        abstract = True
        ordering = [
            "position",
            "name_en",
        ]
