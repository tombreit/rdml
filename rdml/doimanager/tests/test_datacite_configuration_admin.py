# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import pytest

from auditlog.models import LogEntry

from rdml.doimanager.admin import DataCiteConfigurationForm
from rdml.doimanager.models import DataCiteConfiguration


@pytest.fixture
def configuration(db):
    return DataCiteConfiguration.objects.create(
        backend_password="s3cret",
        doi_prefix="10.12345",
        repo_id="ABCD.EFGHIJ",
    )


def _form_data(**overrides):
    data = {
        "is_active": "on",
        "note": "",
        "datacite_instance": DataCiteConfiguration.DataCiteInstance.TEST,
        "doi_prefix": "10.12345",
        "repo_id": "ABCD.EFGHIJ",
        "backend_password": "",
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_password_is_not_rendered_to_the_browser(configuration):
    """Regression test: the stored credential must never reach the HTML."""
    assert "s3cret" not in DataCiteConfigurationForm(instance=configuration).as_p()


@pytest.mark.django_db
def test_blank_password_keeps_the_stored_one(configuration):
    form = DataCiteConfigurationForm(data=_form_data(note="edited"), instance=configuration)

    assert form.is_valid(), form.errors
    assert form.save().backend_password == "s3cret"


@pytest.mark.django_db
def test_password_can_still_be_changed(configuration):
    form = DataCiteConfigurationForm(data=_form_data(backend_password="new-one"), instance=configuration)

    assert form.is_valid(), form.errors
    assert form.save().backend_password == "new-one"


@pytest.mark.django_db
def test_password_is_excluded_from_the_audit_log(configuration):
    """Regression test: the credential must never be written to the audit log.

    Queried via `LogEntry` rather than `configuration.history`, which returns
    nothing for this model (see `AuditlogHistoryField` and UUID primary keys).
    """
    configuration.backend_password = "rotated"
    configuration.save()

    entries = LogEntry.objects.filter(object_pk=str(configuration.pk))

    assert entries.exists()
    for entry in entries:
        assert "backend_password" not in entry.changes_dict
        assert "s3cret" not in entry.changes
        assert "rotated" not in entry.changes
