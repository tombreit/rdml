# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

"""
Documents what `Resource.curators` grants in the admin, and which model
permissions a curator additionally needs. See docs/administration.md.
"""

import pytest
from django.contrib.auth.models import Permission
from django.http import HttpResponseForbidden
from django.urls import reverse

from rdml.core import middleware
from rdml.doimanager.models import DataCiteResource
from rdml.organization.models import Organization, OrganizationalUnit
from rdml.research.models import CreatorPerson, ResearchResource


@pytest.fixture(autouse=True)
def allow_localhost(monkeypatch):
    monkeypatch.setattr(middleware, "ips_allowed", {"127.0.0.1"})
    monkeypatch.setattr(middleware, "ips_allowed_all", False)


@pytest.fixture(autouse=True)
def plain_static_storage(settings):
    settings.STORAGES = {
        **settings.STORAGES,
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }


@pytest.fixture
def publisher(db):
    return Organization.objects.create(name="Publisher", slug="publisher")


@pytest.fixture
def organizational_unit(db):
    return OrganizationalUnit.objects.create(name="Unit", slug="unit")


@pytest.fixture
def resource(db, publisher, organizational_unit):
    resource = ResearchResource.objects.create(
        title_en="Resource",
        slug="resource",
        language="de",
        publisher=publisher,
        organizational_unit=organizational_unit,
    )
    DataCiteResource.objects.create(resource=resource)
    return resource


@pytest.fixture
def staff_user(db, django_user_model):
    user = django_user_model.objects.create_user(email="staff@example.org", password="secret")
    user.is_staff = True
    user.save()
    return user


@pytest.fixture
def curator(staff_user, resource):
    resource.curators.add(staff_user)
    return staff_user


def grant(user, *perms):
    for perm in perms:
        app_label, codename = perm.split(".")
        user.user_permissions.add(Permission.objects.get(content_type__app_label=app_label, codename=codename))


def change_url(resource):
    return reverse("admin:research_researchresource_change", args=[resource.pk])


def inline_models(response):
    return [formset.opts.model for formset in response.context["inline_admin_formsets"]]


@pytest.mark.django_db
def test_curator_can_open_and_save_resource(client, curator, resource, publisher, organizational_unit):
    client.force_login(curator)

    assert client.get(change_url(resource)).status_code == 200

    response = client.post(
        change_url(resource),
        {
            "title_en": "Resource changed",
            "slug": resource.slug,
            "publisher": publisher.pk,
            "organizational_unit": organizational_unit.pk,
            "language": "de",
            "datacite_resource_type_general": resource.datacite_resource_type_general,
            "_save": "Save",
        },
    )
    assert response.status_code == 302
    resource.refresh_from_db()
    assert resource.title_en == "Resource changed"


@pytest.mark.django_db
def test_non_curator_cannot_open_resource(client, staff_user, resource):
    client.force_login(staff_user)
    assert client.get(change_url(resource)).status_code == HttpResponseForbidden.status_code


@pytest.mark.django_db
def test_curator_without_view_permission_has_no_changelist(client, curator):
    client.force_login(curator)
    response = client.get(reverse("admin:research_researchresource_changelist"))
    assert response.status_code == HttpResponseForbidden.status_code


@pytest.mark.django_db
def test_curator_with_view_permission_has_changelist(client, curator):
    grant(curator, "research.view_researchresource")
    client.force_login(curator)
    response = client.get(reverse("admin:research_researchresource_changelist"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_curator_sees_no_inlines_without_inline_permissions(client, curator, resource):
    client.force_login(curator)
    response = client.get(change_url(resource))
    assert inline_models(response) == []


@pytest.mark.django_db
def test_curator_can_edit_creators_with_inline_permissions(client, curator, resource):
    grant(
        curator,
        "research.add_creatorperson",
        "research.change_creatorperson",
        "research.delete_creatorperson",
    )
    client.force_login(curator)
    response = client.get(change_url(resource))
    assert inline_models(response) == [CreatorPerson]


@pytest.mark.django_db
def test_autocomplete_needs_view_permission_on_related_model(client, curator):
    client.force_login(curator)
    url = reverse("admin:autocomplete")
    params = {"app_label": "research", "model_name": "researchresource", "field_name": "publisher"}

    assert client.get(url, params).status_code == HttpResponseForbidden.status_code

    grant(curator, "organization.view_organization")
    assert client.get(url, params).status_code == 200


@pytest.mark.django_db
def test_add_related_button_needs_add_permission(client, curator, resource):
    client.force_login(curator)
    assert b'id="add_id_publisher"' not in client.get(change_url(resource)).content

    grant(curator, "organization.add_organization")
    assert b'id="add_id_publisher"' in client.get(change_url(resource)).content


@pytest.mark.django_db
def test_audit_log_needs_view_permission(client, curator):
    client.force_login(curator)
    url = reverse("admin:auditlog_logentry_changelist")

    assert client.get(url).status_code == HttpResponseForbidden.status_code

    grant(curator, "auditlog.view_logentry")
    assert client.get(url).status_code == 200


@pytest.mark.django_db
def test_only_superusers_can_delete_resources(client, curator, resource, django_user_model):
    delete_url = reverse("admin:research_researchresource_delete", args=[resource.pk])

    grant(curator, "research.delete_researchresource")
    client.force_login(curator)
    assert client.get(delete_url).status_code == HttpResponseForbidden.status_code

    superuser = django_user_model.objects.create_superuser(email="admin@example.org", password="secret")
    client.force_login(superuser)
    assert client.get(delete_url).status_code == 200


@pytest.mark.django_db
def test_staff_with_add_permission_can_add_resources(client, staff_user):
    client.force_login(staff_user)
    add_url = reverse("admin:research_researchresource_add")

    assert client.get(add_url).status_code == HttpResponseForbidden.status_code

    grant(staff_user, "research.add_researchresource")
    assert client.get(add_url).status_code == 200
