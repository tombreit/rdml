# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import urllib.parse
from typing import NamedTuple

from django.conf import settings
from django.db import models
from django.db.models import Q

from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField

from ..core.models import UUIDBaseModel, TimeStampedBaseModel
from .datacite.rest_client import DataCiteRESTClient
from django.core.exceptions import ValidationError


DataCiteResourceTypeGeneral = models.TextChoices(
    "DataCiteResourceTypeGeneral",
    """
    Audiovisual
    Book
    BookChapter
    Collection
    ComputationalNotebook
    ConferencePaper
    ConferenceProceeding
    DataPaper
    Dataset
    Dissertation
    Event
    Image
    InteractiveResource
    Journal
    JournalArticle
    Model
    OutputManagementPlan
    PeerReview
    PhysicalObject
    Preprint
    Project
    Report
    Service
    Software
    Sound
    Standard
    Text
    Workflow
    Other
    """,
)

# AUDIOVISUAL = 'AUDIOVISUAL', _("Audiovisual")
# BOOK = "BOOK", _("Book")
# BOOKCHAPTER = "BOOKCHAPTER", _("BookChapter")
# COLLECTION = "COLLECTION", _("Collection")
# COMPUTATIONALNOTEBOOK = "COMPUTATIONALNOTEBOOK", _("ComputationalNotebook")
# CONFERENCEPAPER = "CONFERENCEPAPER", _("ConferencePaper")
# CONFERENCEPROCEEDING = "CONFERENCEPROCEEDING", _("ConferenceProceeding")
# DATAPAPER = "DATAPAPER", _("DataPaper")
# DATASET = "DATASET", _("Dataset")
# DISSERTATION = "DISSERTATION", _("Dissertation")
# EVENT = "EVENT", _("Event")
# IMAGE = "IMAGE", _("Image")
# INTERACTIVERESOURCE = "INTERACTIVERESOURCE", _("InteractiveResource")
# JOURNAL = "JOURNAL", _("Journal")
# JOURNALARTICLE = "JOURNALARTICLE", _("JournalArticle")
# MODEL = "MODEL", _("Model")
# OUTPUTMANAGEMENTPLAN = "OUTPUTMANAGEMENTPLAN", _("OutputManagementPlan")
# PEERREVIEW = "PEERREVIEW", _("PeerReview")
# PHYSICALOBJECT = "PHYSICALOBJECT", _("PhysicalObject")
# PREPRINT = "PREPRINT", _("Preprint")
# REPORT = "REPORT", _("Report")
# SERVICE = "SERVICE", _("Service")
# SOFTWARE = "SOFTWARE", _("Software")
# SOUND = "SOUND", _("Sound")
# STANDARD = "STANDARD", _("Standard")
# TEXT = "TEXT", _("Text")
# WORKFLOW = "WORKFLOW", _("Workflow")
# OTHER = "OTHER", _("Other")


DataCiteContributorType = models.TextChoices(
    "ContributorType",
    """
    ContactPerson
    DataCollector
    DataCurator
    DataManager
    Distributor
    Editor
    HostingInstitution
    Producer
    ProjectLeader
    ProjectManager
    ProjectMember
    RegistrationAgency
    RegistrationAuthority
    RelatedPerson
    Researcher
    ResearchGroup
    RightsHolder
    Sponsor
    Supervisor
    WorkPackageLeader
    Other
    """,
)


class DataCiteResource(TimeStampedBaseModel, UUIDBaseModel):
    DOI_TRANSITIONS = {
        "unset": ["draft"],
        "draft": ["registered", "findable"],
        "registered": ["findable"],
        "findable": ["registered"],
    }

    resource = models.OneToOneField(
        "research.Resource",
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
    )
    doi = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        unique=True,
        verbose_name="DOI",
    )

    # DataCite fields
    citation_snippet = models.TextField(
        blank=True,
    )
    datacite_history = models.JSONField(blank=True, default=list, help_text="Collects API responses from DataCite.")

    @property
    def get_datacite_doi_url(self):
        # print(f"get_doi_admin_url for {self.doi}")
        if self.doi:
            from .models import DataCiteConfiguration

            datacite_configuration = DataCiteConfiguration.objects.get(is_active=True)
            backend_url = datacite_configuration.get_datacite_env().backend_url
            return f"{backend_url}{urllib.parse.quote_plus(self.doi)}"

    @property
    def get_doi_resolver_url(self):
        if self.doi:
            return f"https://doi.org/{urllib.parse.quote_plus(self.doi)}"

    @property
    def get_datacite_metadata(self):
        if self.doi:
            return DataCiteRESTClient().get_metadata(self.doi)

    @property
    def get_datacite_doi_state(self):
        if self.doi:
            datacite_doi_state, datacite_found = DataCiteRESTClient().get_datacite_doi_state(doi=self.doi)
            return datacite_doi_state

    def __str__(self):
        return f"DOI: {self.doi or 'n/a'} → {self.resource or 'n/a'}"

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(resource__isnull=False, doi=None) | Q(resource__isnull=False, doi__isnull=False),
                name="%(app_label)s_%(class)s_resource_and_doi_cannot_be_null",
            )
        ]


class DataCiteConfiguration(TimeStampedBaseModel, UUIDBaseModel):
    history = AuditlogHistoryField()

    is_active = models.BooleanField(
        default=False,
        help_text="Only one DataCiteConfiguration can be active at a time.",
    )
    note = models.TextField(blank=True)

    # https://support.datacite.org/docs/testing-guide
    class DataCiteInstance(models.TextChoices):
        TEST = "TEST"
        PRODUCTION = "PROD"

    datacite_instance = models.CharField(
        max_length=10,
        blank=False,
        choices=DataCiteInstance.choices,
        default=DataCiteInstance.TEST,
        help_text="DataCite instance to use. This sets the DataCite Fabrica and API base URLs.",
    )

    doi_prefix = models.CharField(max_length=100, blank=False, default="10.12345", verbose_name="DOI Prefix")
    repo_id = models.CharField(
        max_length=100,
        blank=False,
        default="ABCD.EFGHIJ",
        verbose_name="Repository ID",
        help_text="The Repository ID is a unique identifier for each repository in DataCite. It must contain only upper case letters and numbers, and must start with the Member ID.",
    )
    backend_password = models.CharField(max_length=255, blank=False, default="datacite-secret")

    def get_datacite_env(self):
        # Defaults to datacite_instance == TEST
        # A bit verbose...

        class DataCiteEnvironment(NamedTuple):
            backend_url: str
            api_url: str
            doi_base_url: str

        backend_url = "https://doi.test.datacite.org/dois"
        api_url = "https://api.test.datacite.org/"
        doi_base_url = "https://handle.stage.datacite.org/"

        if self.datacite_instance == self.DataCiteInstance.PRODUCTION:
            backend_url = "https://doi.datacite.org/dois"
            api_url = "https://api.datacite.org/"
            doi_base_url = "https://doi.org/"

        return DataCiteEnvironment(backend_url, api_url, doi_base_url)

    def save(self, *args, **kwargs):
        # TODO: Move to form layer and trigger a Django message
        if not self.is_active and not DataCiteConfiguration.objects.exclude(pk=self.pk).filter(is_active=True).exists():
            raise ValidationError("At least one DataCiteConfiguration must be active")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{'✓' if self.is_active else '❌'} {self.get_datacite_instance_display()} instance: {self.doi_prefix}"


auditlog.register(DataCiteConfiguration)
