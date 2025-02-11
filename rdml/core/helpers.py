# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

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
