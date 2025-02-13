# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import pytest

from django.contrib.auth.models import Permission
from django.urls import reverse
from django.http import HttpResponseForbidden

from rdml.research.models import Resource
from rdml.doimanager.models import DataCiteResource, DataCiteConfiguration
from rdml.doimanager.datacite.rest_client import DataCiteRESTClient


@pytest.fixture
def resource(db):
    return Resource.objects.create(language="de")


@pytest.fixture
def datacite_configuration(db):
    return DataCiteConfiguration.objects.create(
        is_active=True, datacite_instance=DataCiteConfiguration.DataCiteInstance.TEST
    )


@pytest.fixture
def user_without_permission(db, django_user_model):
    user = django_user_model.objects.create_user(email="noperm@example.org", password="secret")
    return user


@pytest.fixture
def user_with_permission(db, django_user_model):
    user = django_user_model.objects.create_user(email="curator@example.org", password="secret")
    perm = Permission.objects.get(codename="register_or_update_dois", content_type__app_label="doimanager")
    user.user_permissions.add(perm)
    return user


@pytest.fixture
def datacite_resource(resource):
    return DataCiteResource.objects.create(resource=resource)


@pytest.mark.django_db
def test_datacite_manager_without_permission(client, resource, datacite_configuration, user_without_permission):
    client.force_login(user_without_permission)
    url = reverse("doimanager:datacite_manager", args=[resource.id])

    response = client.get(url)
    assert response.status_code == HttpResponseForbidden.status_code  # 403


@pytest.mark.django_db
def test_datacite_manager_with_permission_basic_access(client, resource, datacite_configuration, user_with_permission):
    """Test that a user with permission can access the view"""
    client.force_login(user_with_permission)
    url = reverse("doimanager:datacite_manager", args=[resource.id])
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_datacite_manager_draft_transition(
    client, resource, datacite_resource, datacite_configuration, user_with_permission, monkeypatch
):
    """Test the DOI draft transition specifically"""
    client.force_login(user_with_permission)

    # Mock only the external API call
    monkeypatch.setattr(DataCiteRESTClient, "draft_doi", lambda self, metadata, **kwargs: "10.12345/67890")

    url = reverse("doimanager:datacite_manager", args=[resource.id])
    response = client.get(url, {"transition_to": "draft"})
    assert response.status_code == 200
