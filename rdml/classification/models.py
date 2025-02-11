from django.db import models
from django.utils.translation import gettext_lazy as _

from ..core.models import TimeStampedBaseModel, UUIDBaseModel
from .abstracts import CVBaseModel, CVKeywordBaseModel, CVGesisBaseModel


class License(models.TextChoices):
    CC_BY = "CC_BY", _("CC BY")
    CC_BY_SA = "CC_BY_SA", _("CC BY-SA")
    CC_BY_NC = "CC_BY_NC", _("CC BY-NC")
    CC_BY_NC_SA = "CC_BY_NC_SA", _("CC BY-NC-SA")
    CC_BY_ND = "CC_BY_ND", _("CC BY-ND")
    CC_BY_NC_ND = "CC_BY_NC_ND", _("CC BY-NC-ND")
    CC_0 = "CC_0", _("CC0")

#
# New DDI- or ISO-based models / Controlled Vocabluaries
# 

class CVGeographicArea(TimeStampedBaseModel, UUIDBaseModel):
    """
    ISO 3166-1 with ISO 3166-2 country and subdivisions.
    Data from: https://unece.org/trade/cefact/UNLOCODE-Download
    """

    country_code = models.CharField(
        max_length=2,
        blank=False,
    )
    country_name = models.CharField(
        max_length=255,
        blank=False,
    )
    subdivision_code = models.CharField(
        max_length=3,
        blank=True,
    )
    subdivision_name = models.CharField(
        max_length=255,
        blank=True,
    )
    subdivision_type = models.CharField(
        max_length=255,
        blank=True,
    )

    def __str__(self):
        return "{country_code} ({country_name}){has_subdivision}{subdivision}".format(
            country_code=self.country_code,
            country_name=self.country_name,
            has_subdivision=": " if self.subdivision_name else "",
            subdivision=self.subdivision_name if self.subdivision_name else "",
        )

    class Meta:
        ordering = ['country_code', 'subdivision_code', 'pk']
        verbose_name = 'Geographic Area (ISO-3166)'
        verbose_name_plural = 'Geographic Areas (ISO-3166)'


class CVModeOfCollection(CVGesisBaseModel):
    """
    The procedure, technique, or mode of inquiry used to attain the data.
    """

    class Meta(CVGesisBaseModel.Meta):
        verbose_name = "MD 17 Erhebungsverfahren/Mode of Collection"
        verbose_name_plural = "MD 17 Erhebungsverfahren/Modes of Collection"


class CVTimeDimension(CVGesisBaseModel):
    class Meta(CVGesisBaseModel.Meta):
        verbose_name = "MD 14 Typ Forschungsdesign/Time Dimension"
        verbose_name_plural = "MD 14 Typen Forschungsdesign/Time Dimensions"


class CVSamplingProcedure(CVGesisBaseModel):
    class Meta(CVGesisBaseModel.Meta):
        verbose_name = "MD 16 Auswahlverfahren/SamplingProcedure"
        verbose_name_plural = "MD 16 Auswahlverfahren/SamplingProcedures"

#
# Common Vocabularies
#

class CVClassificationKeyword(CVKeywordBaseModel):
    class Meta(CVKeywordBaseModel.Meta):
        verbose_name = "Keyword"
        verbose_name_plural = "Keywords"


#
# GESIS Vocabularies
#

class CVSubjectArea(CVBaseModel):
    def __str__(self):
        return f"{self.code}: {self.name_en}/{self.name_de}"

    class Meta(CVBaseModel.Meta):
        verbose_name = "MD 09 Fachgebiet/Subject area"
        verbose_name_plural = "MD 09 Fachgebiete/Subject areas"
        ordering = ["code"]
#
# Legal aspects
#

# class CVDataProtectionConcept(CVBaseModel):
#     class Meta(CVBaseModel.Meta):
#         verbose_name = "Data Protection Concept"
#         verbose_name_plural = "Data Protection Concepts"

class CVResearchFundingAgency(CVBaseModel):
    class Meta(CVBaseModel.Meta):
        verbose_name = "Research Funding Agency"
        verbose_name_plural = "Research Funding Agencies"

#
# Archiving and access
#

class CVArchivingAccessAvailability(CVBaseModel):
    class Meta(CVBaseModel.Meta):
        verbose_name = "Archiving and access: Availability"
        verbose_name_plural = "Archiving and access: Availabilities"

#
# Technical description of data files
#

class Filetype(TimeStampedBaseModel, UUIDBaseModel):
    extension = models.CharField(
        max_length=255,
        blank=False,
        help_text="File extension, including the leading dot. E.g.: `.txt`.",
    )
    software = models.CharField(
        max_length=255,
        blank=True,
        help_text="Software used to create the file."
    )

    def __str__(self):
        return "{extension}{software}".format(
            extension=self.extension,
            software=f" ({self.software})" if self.software else "",
        )

    class Meta:
        verbose_name = "Filetype"
        verbose_name_plural = "Filetypes"

