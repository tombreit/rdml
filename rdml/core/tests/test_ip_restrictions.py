# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import pytest

from django.urls import reverse
from django.http import HttpResponseForbidden

from rdml.core import middleware


@pytest.fixture
def deny_all_ips(monkeypatch):
    """
    `middleware.ips_allowed` / `ips_allowed_all` are computed at import time, so
    `override_settings(RDML_EDIT_ALLOWED_IP_RANGES=...)` has no effect here.
    """
    monkeypatch.setattr(middleware, "ips_allowed", set())
    monkeypatch.setattr(middleware, "ips_allowed_all", False)


@pytest.fixture
def allow_localhost(monkeypatch):
    monkeypatch.setattr(middleware, "ips_allowed", {"127.0.0.1"})
    monkeypatch.setattr(middleware, "ips_allowed_all", False)


@pytest.mark.django_db
def test_admin_denied_for_disallowed_ip(client, deny_all_ips):
    response = client.get("/admin/")
    assert response.status_code == HttpResponseForbidden.status_code


@pytest.mark.django_db
def test_denied_admin_response_does_not_reflect_html(client, deny_all_ips):
    """Regression test: the 403 template must not render the exception as HTML."""
    response = client.get("/admin/", headers={"x-forwarded-for": "<script>alert(1)</script>"})

    assert response.status_code == HttpResponseForbidden.status_code
    assert b"<script>alert(1)</script>" not in response.content


@pytest.mark.django_db
def test_login_denied_for_disallowed_ip(client, deny_all_ips):
    response = client.get(reverse("accounts:login"))
    assert response.status_code == HttpResponseForbidden.status_code


@pytest.mark.django_db
def test_login_allowed_for_allowed_ip(client, allow_localhost):
    response = client.get(reverse("accounts:login"))
    assert response.status_code == 200
