# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import urllib.error
from contextlib import contextmanager

import pytest

from rdml.core import helpers
from rdml.core.helpers import _NoRedirectHandler, linkchecker


@pytest.fixture
def public_hostname(monkeypatch):
    """Skip the DNS lookup so the tests below exercise the HTTP handling only."""
    monkeypatch.setattr(helpers, "_is_public_hostname", lambda hostname: True)


def fake_opener(monkeypatch, *, status=None, error=None, calls=None):
    """Stub out `build_opener` so no request leaves the machine."""

    class FakeOpener:
        @contextmanager
        def open(self, req, **kwargs):
            if calls is not None:
                calls.update(kwargs)
            if error is not None:
                raise error
            yield type("FakeResponse", (), {"status": status})()

    monkeypatch.setattr(helpers.urllib.request, "build_opener", lambda *handlers: FakeOpener())


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8000/",
        "http://localhost/",
        "http://[::1]/",
        "http://10.1.2.3/",
        "http://192.168.1.1/",
        "http://169.254.169.254/latest/meta-data/",
        "ftp://example.org/",
        "file:///etc/passwd",
    ],
)
def test_non_public_targets_are_reported_unreachable(url):
    """Regression test: linkchecker must not be usable to probe the internal network."""
    assert linkchecker(url) is False


def test_redirect_handler_never_follows():
    """
    Regression test, asserted on the handler itself rather than on a stub: a
    redirect must not be followed, or the `_is_public_hostname` check above can
    be sidestepped by a 302 into the internal network.
    """
    handler = _NoRedirectHandler()

    assert handler.redirect_request(None, None, 302, "Found", {}, "http://127.0.0.1:8000/") is None


def test_public_target_is_still_checked(monkeypatch, public_hostname):
    """The SSRF guard must not block ordinary public URLs."""
    calls = {}
    fake_opener(monkeypatch, status=200, calls=calls)

    assert linkchecker("https://example.org/") is True
    assert calls["timeout"] == 5


def test_redirect_counts_as_reachable(monkeypatch, public_hostname):
    """Refusing to follow a redirect surfaces as an HTTPError carrying the 3xx code."""
    error = urllib.error.HTTPError("https://example.org/", 302, "Found", {}, None)
    fake_opener(monkeypatch, error=error)

    assert linkchecker("https://example.org/") is True


def test_error_status_is_unreachable(monkeypatch, public_hostname):
    error = urllib.error.HTTPError("https://example.org/", 404, "Not Found", {}, None)
    fake_opener(monkeypatch, error=error)

    assert linkchecker("https://example.org/") is False
