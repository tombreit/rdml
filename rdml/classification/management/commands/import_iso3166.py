# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: EUPL-1.2

import csv
import json
import pathlib
from django.core.management.base import BaseCommand
from django.db import transaction
from rdml.classification.models import CVGeographicArea


class Command(BaseCommand):
    help = (
        "Imports ISO 3166-1 with ISO 3166-2 country and subdivisions"
        "from https://unece.org/trade/cefact/UNLOCODE-Download."
        "expects the extracted csv file as command line argument."
        "This data file seems to be encoded in ISO-8859-1, but some"
        "characters were not... The coutry names are in another JSON file"
        "https://datahub.io/core/country-list#data"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "iso31661jsonfile", type=str, help="Path toJSON file from https://datahub.io/core/country-list#data"
        )
        parser.add_argument(
            "iso31662csvfile", type=str, help="Path to CSV file from https://unece.org/trade/cefact/UNLOCODE-Download"
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            # Get a mapping for two-letter country codes to country names
            country_names_mapping = {}
            iso31661jsonfile = pathlib.Path(options["iso31661jsonfile"])
            with open(iso31661jsonfile) as iso31661file_json:
                _country_names_mapping = json.load(iso31661file_json)
                country_names_mapping = {item["Code"]: item["Name"] for item in _country_names_mapping}
                # print(country_names_mapping)

            # Get country codes with country subdivisions (aka: "Bundesländer" etc.)
            iso31662csvfile = pathlib.Path(options["iso31662csvfile"])
            with open(iso31662csvfile, "r", encoding="ISO-8859-1") as csv_iso31662file:
                reader = csv.reader(csv_iso31662file)

                _country_codes_found = set()
                for index, row in enumerate(reader):
                    _country_code = row[0]
                    print(f"Prcocessing country_code {_country_code}")
                    # print(f"Currently processed country codes: {_country_codes_found}")

                    if _country_code not in _country_codes_found:
                        # To get country-wide elements: countries without subdivisions
                        country_only_dict = {
                            "country_code": _country_code,
                            "country_name": country_names_mapping.get(_country_code, None),
                        }
                        country_only = CVGeographicArea.objects.create(**country_only_dict)
                        country_only.save()
                        _country_codes_found.add(_country_code)

                    country_dict = {
                        "country_code": _country_code,
                        "country_name": country_names_mapping.get(_country_code, None),
                        "subdivision_code": row[1],
                        "subdivision_name": row[2],
                        "subdivision_type": row[3],
                    }

                    geographic_area = CVGeographicArea.objects.create(**country_dict)
                    geographic_area.save()

            self.stdout.write(self.style.SUCCESS("Successfully imported GeographicAreas"))
