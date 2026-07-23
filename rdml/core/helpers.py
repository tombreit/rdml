# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import socket
import urllib.error
import urllib.request
from ipaddress import ip_address, ip_network
from urllib.parse import urlsplit

from django.utils.safestring import mark_safe
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

import json
import collections.abc
import difflib


def json_html_highlighter(json_data):
    formatter = HtmlFormatter(style="colorful")
    data_formatted = highlight(json_data, JsonLexer(), formatter)
    style = "<style>" + formatter.get_style_defs() + "</style><br>"
    return mark_safe(style + data_formatted)


def get_doi_from_url(doi_url: str, base_url: str) -> str:
    """
    Validate if string is a valid URL and strip DOI-URL-thingies:
    FROM: https://doi.org/10.82240/3GHE-7716
    TO:                   10.82240/3GHE-7716
    """
    try:
        validate_url = URLValidator()
        validate_url(doi_url)
    except ValidationError:
        return False

    doi = doi_url.replace(base_url, "")
    return doi


def get_countries_as_choices():
    from ..organization.countries import countries_dict

    country_choices = []
    valid_country_codes = ["en", "de"]
    for k, v in countries_dict.items():
        if v["639-1"] in valid_country_codes:
            country_choices.append(tuple((f"{v['639-1']}", f"{v['639-1']} - {v['name']}")))
    return country_choices


def flatten(dictionary, parent_key=False, separator=".", log=False):
    """
    Turn a nested dictionary into a flattened dictionary
    :param dictionary: The dictionary to flatten
    :param parent_key: The string to prepend to dictionary's keys
    :param separator: The string used to separate flattened keys
    :param log : Bool used to control logging to the terminal
    :return: A flattened dictionary
    Soure: https://www.leehbi.com/blog/2021-06-05-JSON-Handling/
    """

    items = []
    for key, value in dictionary.items():
        if log:
            print("checking:", key)
        new_key = str(parent_key) + separator + key if parent_key else key
        if isinstance(value, collections.abc.MutableMapping):
            if log:
                print(new_key, ": dict found")
            if not value.items():
                if log:
                    print("Adding key-value pair:", new_key, None)
                items.append((new_key, None))
            else:
                items.extend(flatten(value, new_key, separator).items())
        elif isinstance(value, list):
            if log:
                print(new_key, ": list found")
            if len(value):
                for k, v in enumerate(value):
                    items.extend(flatten({str(k): v}, new_key).items())
            else:
                if log:
                    print("Adding key-value pair:", new_key, None)
                items.append((new_key, None))
        else:
            if log:
                print("Adding key-value pair:", new_key, value)
            items.append((new_key, value))
    return dict(items)


def humanized_flatten(jsons, html_highlighted=False):
    if not isinstance(jsons, str):
        jsons = json.dumps(jsons, sort_keys=True, indent=0)
    flat = flatten(json.loads(jsons))
    flat = json.dumps(flat, sort_keys=True, indent=0)

    if html_highlighted:
        json_html_highlighter(flat)

    return flat


def diff_json_to_html(json1, json2):
    def _cleanup(str):
        return str.replace(",", "").replace("{", "").replace("}", "")

    json1 = _cleanup(json1)
    json2 = _cleanup(json2)

    table = difflib.HtmlDiff(wrapcolumn=80).make_table(
        json1.split("\n"),
        json2.split("\n"),
        context=True,
        numlines=0,
    )

    # from pathlib import Path
    # table_file = difflib.HtmlDiff(
    #     wrapcolumn=80,
    #     charjunk=difflib.IS_CHARACTER_JUNK,
    # ).make_file(
    #     json1.split('\n'), json2.split('\n'),
    #     # context=True, numlines=0,
    # )
    # Path('diff.html').write_text(table_file)

    return table


def get_orderable_representation(code):
    """
    Expects a version like code string, eg '1.2.35' and converts that
    to an orderable string representation '000100020035.
    """
    orderable_parts = code.split(".")
    # orderable_code = list(map(int, orderable_parts))
    orderable_code = [str(item).zfill(4) for item in orderable_parts]
    orderable_code = "".join(orderable_code)
    # print(f'{code} -> {orderable_code}')
    return orderable_code


def _convert_partial_ip_to_cidr(ip_range):
    """
    "10"       → "10.0.0.0/8"
    "10.1"     → "10.1.0.0/16"
    "10.1.2"   → "10.1.2.0/24"
    "10.1.2.3" → "10.1.2.3/32"
    """

    if "/" in ip_range:
        return ip_range

    parts = ip_range.split(".")
    if len(parts) == 1:
        return f"{ip_range}.0.0.0/8"
    if len(parts) == 2:
        return f"{ip_range}.0.0/16"
    if len(parts) == 3:
        return f"{ip_range}.0/24"
    if len(parts) == 4:
        return f"{ip_range}/32"

    raise ValueError(f"Invalid IP range: {ip_range}")


def get_ips_from_ranges(ip_ranges):
    """
    Convert a list of IP ranges to a list of IP addresses.
    """
    ips = set()
    for ip_range in ip_ranges:
        try:
            cidr = _convert_partial_ip_to_cidr(ip_range)
            net = ip_network(cidr)
            ips.update([str(ip) for ip in net])
        except ValueError:
            continue

    return ips


def get_client_ip(request):
    x_forwarded_for = request.headers.get("x-forwarded-for")
    if x_forwarded_for:
        client_ip = x_forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.META.get("REMOTE_ADDR")

    return client_ip


def _is_public_hostname(hostname):
    """
    Resolve `hostname` and return True only if every address it resolves to is
    routable on the public internet.

    This keeps `linkchecker` from being used to probe the internal network from
    the application server (SSRF) via a URL entered in the admin.
    """
    if not hostname:
        return False

    try:
        addrinfo = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False

    for *_, sockaddr in addrinfo:
        try:
            address = ip_address(sockaddr[0])
        except ValueError:
            return False
        if (
            address.is_loopback
            or address.is_private
            or address.is_link_local
            or address.is_reserved
            or address.is_unspecified
            or address.is_multicast
        ):
            return False

    return True


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """
    Refuse to follow redirects.

    Returning None makes urllib raise `HTTPError` with the original 3xx code
    instead of following the hop. Without this, a public URL could redirect the
    reachability probe into the internal network, bypassing `_is_public_hostname`.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def linkchecker(url, timeout=5):
    """
    Checks if a fully qualified URL is reachable (HTTP status 200-399).
    Returns True if the request succeeds, False otherwise.

    URLs that do not point at a public HTTP(S) host are reported as unreachable
    rather than fetched.
    """
    try:
        parsed = urlsplit(url)
        if parsed.scheme not in ("http", "https"):
            return False
        if not _is_public_hostname(parsed.hostname):
            return False

        # `_NoRedirectHandler` keeps a public URL from redirecting us into the
        # internal network.
        # Note: the address checked above is resolved again for the request
        # itself, leaving a small DNS rebinding window. Closing it would require
        # pinning the connection to the resolved address, which is not worth the
        # complexity for a reachability probe.
        opener = urllib.request.build_opener(_NoRedirectHandler)
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "RDML Link Checker")
        with opener.open(req, timeout=timeout) as response:
            return 200 <= response.status < 400
    except urllib.error.HTTPError as error:
        # Any non-2xx response arrives here, including the redirects we refuse
        # to follow. A 3xx still counts as reachable, 4xx/5xx do not.
        return 200 <= error.code < 400
    except Exception:
        return False
